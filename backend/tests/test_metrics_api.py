"""API-04 reader and HTTP tests; doubles prove control flow, not SQL arithmetic."""

import importlib
import json
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app._generated.models import MetricsResponse
from app.repositories.postgres_storage import DatabaseUnavailableError


def reader_module():
    return importlib.import_module("app.repositories.metrics_repository")


def reader_doubles():
    conn = MagicMock()
    conn.fetchrow = AsyncMock()
    transaction = MagicMock()
    transaction.__aenter__ = AsyncMock(return_value=transaction)
    transaction.__aexit__ = AsyncMock(return_value=False)
    conn.transaction.return_value = transaction
    acquisition = MagicMock()
    acquisition.__aenter__ = AsyncMock(return_value=conn)
    acquisition.__aexit__ = AsyncMock(return_value=False)
    pool = MagicMock()
    pool.acquire.return_value = acquisition
    return pool, conn, acquisition, transaction


@pytest.mark.parametrize("rate,time", [(None, None), (0, 0), (Decimal("33.33"), Decimal("1.667"))])
async def test_metrics_reader_single_readonly_snapshot_numeric_mapping(monkeypatch, rate, time):
    module = reader_module()
    pool, conn, acquisition, transaction = reader_doubles()
    provider = AsyncMock(return_value=pool)
    monkeypatch.setattr(module, "get_db_pool", provider)
    conn.fetchrow.return_value = {"rojo": 2, "amarillo": 1, "verde": 3, "tasa_hitl": rate, "tiempo_promedio_ia_segundos": time}
    result = await module.obtener_metricas()
    assert isinstance(result, MetricsResponse)
    payload = json.loads(result.model_dump_json())
    assert payload == {"distribucion_prioridad": {"Rojo": 2, "Amarillo": 1, "Verde": 3}, "tasa_hitl": None if rate is None else float(rate), "tiempo_promedio_ia_segundos": None if time is None else float(time)}
    provider.assert_awaited_once_with()
    pool.acquire.assert_called_once_with()
    conn.transaction.assert_called_once_with(isolation="read_committed", readonly=True)
    conn.fetchrow.assert_awaited_once()
    acquisition.__aexit__.assert_awaited_once()
    transaction.__aexit__.assert_awaited_once()
    conn.execute.assert_not_called()


@pytest.mark.parametrize("role", ["ADMINISTRADOR", "COORDINADOR", "SUPERVISOR", "AUDITOR", "OPERADOR"])
def test_metrics_http_all_active_roles(client, monkeypatch, role):
    module = reader_module()
    payload = {"distribucion_prioridad": {"Rojo": 2, "Amarillo": 3, "Verde": 5}, "tasa_hitl": 30, "tiempo_promedio_ia_segundos": 2}
    reader = AsyncMock(return_value=MetricsResponse.model_validate(payload))
    monkeypatch.setattr(module, "obtener_metricas", reader)
    session = AsyncMock(return_value={"id": "11111111-2222-3333-4444-555555555555", "rol": role, "estado": "ACTIVO"})
    monkeypatch.setattr("app.core.security.get_active_session_user", session)
    response = client.get("/api/v1/metrics", headers={"Authorization": "Bearer api04-unit-session"})
    assert response.status_code == 200
    assert response.json() == payload
    reader.assert_awaited_once_with()


@pytest.mark.parametrize("kind", ["absent", "malformed", "invalid", "expired", "revoked", "inactive"])
def test_metrics_http_rejected_sessions_do_not_calculate(client, monkeypatch, kind):
    reader = AsyncMock()
    monkeypatch.setattr(reader_module(), "obtener_metricas", reader)
    session = AsyncMock(return_value=None)
    monkeypatch.setattr("app.core.security.get_active_session_user", session)
    headers = {} if kind == "absent" else {"Authorization": "Basic invalid" if kind == "malformed" else "Bearer api04-unit-rejected"}
    response = client.get("/api/v1/metrics", headers=headers)
    assert response.status_code == 401
    reader.assert_not_awaited()
    if kind in ("absent", "malformed"):
        session.assert_not_awaited()


def test_metrics_http_authentication_unavailable_is_distinct(client, monkeypatch):
    reader = AsyncMock()
    monkeypatch.setattr(reader_module(), "obtener_metricas", reader)
    monkeypatch.setattr("app.core.security.get_active_session_user", AsyncMock(side_effect=RuntimeError("sandbox unavailable")))
    response = client.get("/api/v1/metrics", headers={"Authorization": "Bearer api04-unit-session"})
    assert response.status_code == 503
    assert response.json() == {"detail": "El servicio de autenticación no está disponible temporalmente."}
    reader.assert_not_awaited()


def test_metrics_http_calculation_unavailable_uses_existing_handler(client, bearer_headers, monkeypatch):
    monkeypatch.setattr(reader_module(), "obtener_metricas", AsyncMock(side_effect=DatabaseUnavailableError("sandbox unavailable")))
    response = client.get("/api/v1/metrics", headers=bearer_headers)
    assert response.status_code == 503
    assert response.json() == {"detail": {"error": "POSTGRESQL_NO_DISPONIBLE", "mensaje": "PostgreSQL no está disponible temporalmente."}}


def test_metrics_http_route_registered_with_generated_response(client):
    operation = client.get("/openapi.json").json()["paths"]["/api/v1/metrics"]["get"]
    assert operation["responses"]["200"]["content"]["application/json"]["schema"]["$ref"].endswith("/MetricsResponse")


@pytest.mark.parametrize("stage", ["provider", "absent", "acquire", "begin", "fetch", "commit", "release", "empty-row"])
async def test_metrics_reader_database_failures_release_without_fallback(monkeypatch, stage):
    module = reader_module()
    pool, conn, acquisition, transaction = reader_doubles()
    provider = AsyncMock(return_value=None if stage == "absent" else pool)
    monkeypatch.setattr(module, "get_db_pool", provider)
    conn.fetchrow.return_value = {"rojo": 0, "amarillo": 0, "verde": 0, "tasa_hitl": None, "tiempo_promedio_ia_segundos": None}
    error = RuntimeError("private DSN / secret must not become a public diagnostic")
    if stage == "provider":
        provider.side_effect = error
    elif stage == "acquire":
        acquisition.__aenter__.side_effect = error
    elif stage == "begin":
        transaction.__aenter__.side_effect = error
    elif stage == "fetch":
        conn.fetchrow.side_effect = error
    elif stage == "commit":
        transaction.__aexit__.side_effect = error
    elif stage == "release":
        acquisition.__aexit__.side_effect = error
    elif stage == "empty-row":
        conn.fetchrow.return_value = None
    with pytest.raises(DatabaseUnavailableError) as caught:
        await module.obtener_metricas()
    assert "private" not in str(caught.value)
    if stage not in ("provider", "absent", "acquire"):
        acquisition.__aexit__.assert_awaited_once()
    if stage not in ("provider", "absent", "acquire", "begin"):
        transaction.__aexit__.assert_awaited_once()
    conn.execute.assert_not_called()
