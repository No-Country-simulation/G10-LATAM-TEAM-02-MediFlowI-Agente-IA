import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings
from app.core.security import create_access_token


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

    with patch("app.repositories.postgres_storage.PostgresStorageRepository.guardar_resultado") as mock_save, \
         patch("app.api.v1.settings._guardar_modo_almacenamiento_db") as mock_save_settings:
        mock_save.return_value = True
        mock_save_settings.return_value = None
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
    token = create_access_token({"id": "11111111-2222-3333-4444-555555555555", "rol": "OPERADOR"})
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def auditor_bearer_headers():
    token = create_access_token({"id": "22222222-2222-3333-4444-555555555555", "rol": "AUDITOR"})
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


@pytest.fixture
def admin_bearer_headers():
    token = create_access_token({"id": "33333333-2222-3333-4444-555555555555", "rol": "ADMINISTRADOR"})
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
