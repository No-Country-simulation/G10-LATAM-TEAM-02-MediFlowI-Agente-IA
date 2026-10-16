"""Transmisión ASGI incremental, RBAC, mantenimiento y cancelación."""

import asyncio
import contextlib
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app._generated.models import AlertaGuardia
from app.api.v1.alerts import stream_alerts
from app.core.alerts import MENSAJE_GUARDIA
from app.main import app
from app.services.alert_service import AlertBroadcaster, AlertService, get_alert_broadcaster


@pytest.mark.parametrize(
    "token,status",
    [
        (None, 401),
        ("invalido", 401),
        ("test-operator-token", 403),
        ("test-auditor-token", 403),
    ],
)
def test_roles_no_permitidos(client, token, status):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    assert client.get("/api/v1/alerts/stream", headers=headers).status_code == status


def test_token_en_url_no_autoriza(client):
    assert client.get("/api/v1/alerts/stream?token=test-admin-token").status_code == 401


def test_fallo_autenticacion_es_503(client, monkeypatch):
    monkeypatch.setattr(
        "app.core.security.verify_access_token", AsyncMock(side_effect=RuntimeError())
    )
    response = client.get("/api/v1/alerts/stream", headers={"Authorization": "Bearer token"})
    assert response.status_code == 503


@pytest.mark.parametrize(
    "token", ["test-medico-token", "test-coordinador-token", "test-admin-token"]
)
async def test_stream_http_incremental_y_desconexion(token):
    broker = AlertBroadcaster()
    app.dependency_overrides[get_alert_broadcaster] = lambda: broker
    incoming, outgoing = asyncio.Queue(), asyncio.Queue()
    await incoming.put({"type": "http.request", "body": b"", "more_body": False})
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "root_path": "",
        "path": "/api/v1/alerts/stream",
        "raw_path": b"/api/v1/alerts/stream",
        "query_string": b"",
        "headers": [(b"authorization", f"Bearer {token}".encode())],
        "client": ("127.0.0.1", 1234),
        "server": ("testserver", 80),
    }
    task = asyncio.create_task(app(scope, incoming.get, outgoing.put))
    try:
        start = await asyncio.wait_for(outgoing.get(), 2)
        assert start["status"] == 200
        headers = dict(start["headers"])
        assert headers[b"content-type"].startswith(b"text/event-stream")
        assert headers[b"cache-control"] == b"no-cache, no-transform"
        assert headers[b"x-accel-buffering"] == b"no"
        connected = await asyncio.wait_for(outgoing.get(), 2)
        assert connected["body"] == b": connected\n\n"
        stored = AlertaGuardia(
            id=uuid4(),
            documento_id="DOC",
            episodio_id=None,
            prioridad="Urgente",
            fecha=datetime.now(UTC),
            mensaje=MENSAJE_GUARDIA,
        )
        repository = Mock(registrar_alerta=AsyncMock(return_value=stored))
        await AlertService(repository=repository, broadcaster=broker).emitir("DOC", None)
        frame = (
            f"id: {stored.id}\nevent: ALERTA_GUARDIA_EMITIDA\ndata: {stored.model_dump_json()}\n\n"
        )
        event = await asyncio.wait_for(outgoing.get(), 2)
        assert event["body"] == frame.encode()
        assert event["more_body"] is True
        assert not task.done()
        await incoming.put({"type": "http.disconnect"})
        await asyncio.wait_for(task, 2)
        assert broker.subscriber_count == 0
    finally:
        app.dependency_overrides.pop(get_alert_broadcaster, None)
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def test_heartbeat_y_revocacion_sesion(monkeypatch):
    monkeypatch.setattr("app.api.v1.alerts.HEARTBEAT_SECONDS", 0.01)
    verify = AsyncMock(return_value={"rol": "MEDICO"})
    monkeypatch.setattr("app.core.security.verify_access_token", verify)
    broker = AlertBroadcaster()
    stream = stream_alerts("token", broker)
    assert await anext(stream) == ": connected\n\n"
    assert await asyncio.wait_for(anext(stream), 1) == ": heartbeat\n\n"
    verify.return_value = None
    broker.publish("no debe salir")
    with pytest.raises(StopAsyncIteration):
        await anext(stream)
    assert broker.subscriber_count == 0


@pytest.mark.parametrize("session", [{"rol": "OPERADOR"}, RuntimeError("BD caída")])
async def test_cambio_de_rol_o_fallo_sesion_cierra_flujo(monkeypatch, session):
    verify = AsyncMock()
    if isinstance(session, Exception):
        verify.side_effect = session
    else:
        verify.return_value = session
    monkeypatch.setattr("app.core.security.verify_access_token", verify)
    broker = AlertBroadcaster()
    stream = stream_alerts("token", broker)
    await anext(stream)
    broker.publish("evento")
    with pytest.raises(StopAsyncIteration):
        await anext(stream)
    assert broker.subscriber_count == 0
