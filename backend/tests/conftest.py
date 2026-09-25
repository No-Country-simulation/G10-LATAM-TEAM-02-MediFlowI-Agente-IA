import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def settings():
    s = get_settings()
    return s


@pytest.fixture(autouse=True)
def mock_postgres_for_tests():
    """Evita que los tests automatizados de pytest inserten filas o alteren la BD de desarrollo."""
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
