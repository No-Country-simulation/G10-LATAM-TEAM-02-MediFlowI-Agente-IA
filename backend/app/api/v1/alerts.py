"""SSE autorizado para el equipo de guardia; autenticación por cabecera."""

import asyncio
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.core import security
from app.core.alerts import ROLES_GUARDIA
from app.services.alert_service import AlertBroadcaster, get_alert_broadcaster

router = APIRouter(prefix="/alerts", tags=["alerts"])
HEARTBEAT_SECONDS = 15


async def _session_allowed(token: str) -> bool:
    try:
        user = await security.verify_access_token(token)
    except RuntimeError:
        return False
    return bool(user and user.get("rol") in ROLES_GUARDIA)


async def stream_alerts(token: str, broadcaster: AlertBroadcaster) -> AsyncIterator[str]:
    async with broadcaster.subscribe() as queue:
        yield ": connected\n\n"
        while True:
            try:
                frame = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SECONDS)
            except TimeoutError:
                frame = ": heartbeat\n\n"
            if frame is None or not await _session_allowed(token):
                return
            yield frame


@router.get(
    "/stream",
    response_class=StreamingResponse,
    summary="Recibir alertas críticas de guardia por SSE",
    responses={
        200: {
            "description": "Eventos ALERTA_GUARDIA_EMITIDA con JSON AlertaGuardia",
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
        },
        401: {"description": "Sesión ausente, inválida o expirada"},
        403: {"description": "Rol sin autorización"},
        503: {"description": "Servicio de autenticación no disponible"},
    },
)
async def recibir_alertas_guardia(
    request: Request,
    _user: dict = Depends(security.require_roles(*ROLES_GUARDIA)),
    broadcaster: AlertBroadcaster = Depends(get_alert_broadcaster),
) -> StreamingResponse:
    token = request.headers["authorization"].removeprefix("Bearer ").strip()
    return StreamingResponse(
        stream_alerts(token, broadcaster),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )
