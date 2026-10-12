from unittest.mock import AsyncMock, patch
from uuid import uuid4
import pytest


@pytest.mark.asyncio
async def test_signup_success(client):
    user_id = str(uuid4())
    mock_created = {
        "id": user_id,
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "telefono": "987654321",
        "rol": "OPERADOR",
        "estado": "INACTIVO",
    }

    with (
        patch("app.api.v1.auth.get_user_by_document", new_callable=AsyncMock) as mock_get_user,
        patch("app.api.v1.auth.get_user_by_email", new_callable=AsyncMock) as mock_get_email,
        patch("app.api.v1.auth.create_user", new_callable=AsyncMock) as mock_create_user,
    ):
        mock_get_user.return_value = None
        mock_get_email.return_value = None
        mock_create_user.return_value = mock_created

        payload = {
            "documento_identidad": "87654321",
            "nombres": "Juan",
            "apellidos": "Perez",
            "correo": "juan@test.com",
            "password": "StrongPassword123!",
        }

        response = client.post("/api/v1/auth/signup", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["documento_identidad"] == payload["documento_identidad"]
        assert data["estado"] == "INACTIVO"
        assert data["nombres"] == payload["nombres"]


@pytest.mark.asyncio
async def test_signup_duplicate_document(client):
    with patch("app.api.v1.auth.get_user_by_document", new_callable=AsyncMock) as mock_get_user:
        mock_get_user.return_value = {"id": str(uuid4())}

        payload = {
            "documento_identidad": "87654321",
            "nombres": "Juan",
            "apellidos": "Perez",
            "correo": "juan@test.com",
            "password": "StrongPassword123!",
        }

        response = client.post("/api/v1/auth/signup", json=payload)

        assert response.status_code == 409


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    with (
        patch("app.api.v1.auth.get_user_by_document", new_callable=AsyncMock) as mock_get_user,
        patch("app.api.v1.auth.get_user_by_email", new_callable=AsyncMock) as mock_get_email,
    ):
        mock_get_user.return_value = None
        mock_get_email.return_value = {"id": str(uuid4())}

        payload = {
            "documento_identidad": "87654321",
            "nombres": "Juan",
            "apellidos": "Perez",
            "correo": "juan@test.com",
            "password": "StrongPassword123!",
        }

        response = client.post("/api/v1/auth/signup", json=payload)

        assert response.status_code == 409
        assert "correo electrónico" in response.json()["detail"]


@pytest.mark.asyncio
async def test_signup_weak_password(client):
    payload = {
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "password": "weak",
    }

    response = client.post("/api/v1/auth/signup", json=payload)

    assert response.status_code == 422
