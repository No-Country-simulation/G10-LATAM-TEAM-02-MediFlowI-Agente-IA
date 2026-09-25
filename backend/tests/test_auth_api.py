"""
Pruebas unitarias para la API de Autenticación y Usuarios (RF-01 al RF-05).
"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.v1.users import UserCreateRequest, UserUpdateRequest
from app.core.security import create_access_token
from app.main import app

client = TestClient(app)

MOCK_ADMIN_USER = {
    "id": "11111111-2222-3333-4444-555555555555",
    "documento_identidad": "12345678",
    "password_hash": "3cafb24391f84a713103a1dce118e10cd75e702c30f6c56e4f995ad2de4a6888",
    "salt": "1234567890abcdef1234567890abcdef",
    "nombres": "Administrador",
    "apellidos": "Sistema",
    "correo": "admin@mediflow.local",
    "telefono": "999888777",
    "rol": "ADMINISTRADOR",
    "estado": "ACTIVO",
}


def test_user_password_policy_applies_to_create_and_update():
    payload = {
        "documento_identidad": "88776655",
        "nombres": "María",
        "apellidos": "Gómez",
    }

    with pytest.raises(ValidationError):
        UserCreateRequest(**payload, password="clave123")
    with pytest.raises(ValidationError):
        UserUpdateRequest(password="clave123")

    assert UserCreateRequest(**payload, password="ClaveSegura#2026").password
    assert UserUpdateRequest(password="ClaveSegura#2026").password


@pytest.mark.asyncio
async def test_login_success():
    """Verifica inicio de sesión exitoso con DNI de 8 cifras y contraseña correcta."""
    with patch("app.api.v1.auth.get_user_by_document", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MOCK_ADMIN_USER

        response = client.post(
            "/api/v1/auth/login", json={"documento_identidad": "12345678", "password": "admin"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["documento_identidad"] == "12345678"
        assert data["user"]["rol"] == "ADMINISTRADOR"


@pytest.mark.asyncio
async def test_login_invalid_dni_format():
    """Verifica rechazo si el documento de identidad no contiene 8 cifras."""
    response = client.post(
        "/api/v1/auth/login", json={"documento_identidad": "12345", "password": "admin"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_password():
    """Verifica rechazo cuando la contraseña es incorrecta."""
    with patch("app.api.v1.auth.get_user_by_document", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = MOCK_ADMIN_USER

        response = client.post(
            "/api/v1/auth/login",
            json={"documento_identidad": "12345678", "password": "wrong_password"},
        )
        assert response.status_code == 401
        assert "incorrecta" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout():
    """Verifica cierre de sesión e invalidación de token."""
    response = client.post("/api/v1/auth/logout", headers={"Authorization": "Bearer token_falso"})
    assert response.status_code == 200
    assert "cierre de sesión" in response.json()["mensaje"].lower()


@pytest.mark.asyncio
async def test_require_current_user_returns_the_bearer_session_user():
    """La dependencia compartida debe resolver al usuario de una sesión Bearer válida."""
    from app.core.security import require_current_user

    expected_user = {"id": "user-123", "rol": "OPERADOR"}
    token = await create_access_token(expected_user)

    with patch("app.core.security.get_active_session_user", new_callable=AsyncMock) as lookup:
        lookup.return_value = expected_user
        assert await require_current_user(f"Bearer {token}") == expected_user
