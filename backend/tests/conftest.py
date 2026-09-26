import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Fuerza un proveedor determinista antes de importar la aplicación. Ninguna prueba
# automatizada debe depender de credenciales reales ni realizar llamadas LLM.
os.environ["GOOGLE_API_KEY"] = "your-test-placeholder"
os.environ["OPENAI_API_KEY"] = "your-test-placeholder"
os.environ["ALLOW_MOCK_LLM"] = "true"

from app.core.config import get_settings
from app.main import app

TEST_SESSIONS = {
    "test-operator-token": {"id": "11111111-2222-3333-4444-555555555555", "rol": "OPERADOR"},
    "test-auditor-token": {"id": "22222222-2222-3333-4444-555555555555", "rol": "AUDITOR"},
    "test-admin-token": {"id": "33333333-2222-3333-4444-555555555555", "rol": "ADMINISTRADOR"},
}


async def _fake_active_session(token: str):
    return TEST_SESSIONS.get(token)


@pytest.fixture(scope="session")
def settings():
    s = get_settings()
    return s


@pytest.fixture(autouse=True)
def mock_postgres_for_tests(request):
    """Evita que los tests automatizados de pytest inserten filas o alteren la BD de desarrollo."""
    if request.node.get_closest_marker("repository_mock"):
        # Esta prueba usa explícitamente un repositorio sin DATABASE_URL: conserva
        # el modo en memoria para verificar la trazabilidad sin tocar mediflow_dev.
        yield None
        return

    with (
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.guardar_resultado"
        ) as mock_save,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.listar",
            new_callable=AsyncMock,
        ) as mock_list,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.listar_historial",
            new_callable=AsyncMock,
        ) as mock_history,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.obtener_por_id",
            new_callable=AsyncMock,
        ) as mock_get_document,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.registrar_auditoria",
            new_callable=AsyncMock,
        ) as mock_audit,
        patch(
            "app.repositories.postgres_storage.get_storage_mode", new_callable=AsyncMock
        ) as mock_storage_mode,
        patch("app.api.v1.settings._guardar_modo_almacenamiento_db") as mock_save_settings,
        patch(
            "app.api.v1.settings._obtener_modo_almacenamiento_db", new_callable=AsyncMock
        ) as mock_get_settings,
        patch("app.core.security.create_session", new_callable=AsyncMock),
        patch("app.core.security.revoke_session", new_callable=AsyncMock),
        patch("app.core.security.get_active_session_user", side_effect=_fake_active_session),
    ):
        mock_save.return_value = True
        mock_list.return_value = []
        mock_history.return_value = []
        mock_get_document.return_value = None
        mock_audit.return_value = False
        mock_storage_mode.return_value = "LOCAL"
        mock_save_settings.return_value = None
        mock_get_settings.return_value = "LOCAL"
        yield mock_save


@pytest.fixture
def client():
    """Cliente de pruebas FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(settings):
    """Headers con la API Key configurada."""
    return {
        "X-API-Key": settings.api_key,
        "Content-Type": "application/json",
    }


@pytest.fixture
def bearer_headers():
    return {"Authorization": "Bearer test-operator-token", "Content-Type": "application/json"}


@pytest.fixture
def auditor_bearer_headers():
    return {"Authorization": "Bearer test-auditor-token", "Content-Type": "application/json"}


@pytest.fixture
def admin_bearer_headers():
    return {"Authorization": "Bearer test-admin-token", "Content-Type": "application/json"}
