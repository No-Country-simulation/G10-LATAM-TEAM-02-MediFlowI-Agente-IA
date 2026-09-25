import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import get_settings


@pytest.fixture(scope="session")
def settings():
    return get_settings()


@pytest.fixture
def client():
    """Cliente de pruebas con header de autenticación por defecto."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(settings):
    """Headers con la API Key configurada."""
    return {
        "X-API-Key": settings.api_key,
        "Content-Type": "application/json",
    }
