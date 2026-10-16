"""Persistencia previa y difusión SSE en el proceso actual de FastAPI."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog

from app.core.alerts import EVENTO_GUARDIA
from app.repositories.alert_repository import AlertRepository

logger = structlog.get_logger(__name__)


class AlertBroadcaster:
    """Una cola acotada por conexión; un cliente lento no bloquea al triaje."""

    def __init__(self, queue_size: int = 128):
        if queue_size < 1:
            raise ValueError("queue_size debe ser positivo")
        self._queue_size = queue_size
        self._subscribers: set[asyncio.Queue[str | None]] = set()

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[str | None]]:
        queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=self._queue_size)
        self._subscribers.add(queue)
        try:
            yield queue
        finally:
            self._subscribers.discard(queue)

    def publish(self, frame: str) -> None:
        """No espera a clientes. None cierra las conexiones cuya cola se llenó."""
        for queue in tuple(self._subscribers):
            try:
                queue.put_nowait(frame)
            except asyncio.QueueFull:
                self._subscribers.discard(queue)
                # Vaciar la cola permite cerrar sin enviar eventos atrasados.
                while not queue.empty():
                    queue.get_nowait()
                queue.put_nowait(None)
                logger.warning("alerts.cliente_lento_desconectado")


_broadcaster = AlertBroadcaster()


def get_alert_broadcaster() -> AlertBroadcaster:
    """Compartido por los productores y las conexiones SSE de este proceso."""
    return _broadcaster


class AlertService:
    def __init__(self, repository=None, broadcaster: AlertBroadcaster | None = None):
        self._repository = repository if repository is not None else AlertRepository()
        self._broadcaster = broadcaster if broadcaster is not None else get_alert_broadcaster()

    async def emitir(self, documento_id: str, usuario_id: str | None) -> None:
        alerta = await self._repository.registrar_alerta(documento_id, usuario_id)
        frame = f"id: {alerta.id}\nevent: {EVENTO_GUARDIA}\ndata: {alerta.model_dump_json()}\n\n"
        self._broadcaster.publish(frame)
