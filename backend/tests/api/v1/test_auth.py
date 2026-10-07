import pytest
from httpx import AsyncClient
from uuid import uuid4

pytestmark = pytest.mark.asyncio

async def test_signup_success(async_client: AsyncClient, mocker):
    mock_create_user = mocker.patch("app.api.v1.auth.create_user")
    mock_get_user = mocker.patch("app.api.v1.auth.get_user_by_document")
    mock_get_email = mocker.patch("app.api.v1.auth.get_user_by_email")
    
    mock_get_user.return_value = None
    mock_get_email.return_value = None
    
    user_id = str(uuid4())
    mock_create_user.return_value = {
        "id": user_id,
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "telefono": "987654321",
        "rol": "OPERADOR",
        "estado": "INACTIVO"
    }
    
    payload = {
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "password": "StrongPassword123!"
    }
    
    response = await async_client.post("/api/v1/auth/signup", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    assert data["documento_identidad"] == payload["documento_identidad"]
    assert data["estado"] == "INACTIVO"
    assert data["nombres"] == payload["nombres"]

async def test_signup_duplicate_document(async_client: AsyncClient, mocker):
    mock_get_user = mocker.patch("app.api.v1.auth.get_user_by_document")
    mock_get_user.return_value = {"id": str(uuid4())}
    
    payload = {
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "password": "StrongPassword123!"
    }
    
    response = await async_client.post("/api/v1/auth/signup", json=payload)
    
    assert response.status_code == 409


async def test_signup_duplicate_email(async_client: AsyncClient, mocker):
    mock_get_user = mocker.patch("app.api.v1.auth.get_user_by_document")
    mock_get_user.return_value = None
    mock_get_user_by_email = mocker.patch("app.api.v1.auth.get_user_by_email")
    mock_get_user_by_email.return_value = {"id": str(uuid4())}
    
    payload = {
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "password": "StrongPassword123!"
    }
    
    response = await async_client.post("/api/v1/auth/signup", json=payload)
    
    assert response.status_code == 409
    assert "correo electrónico" in response.json()["detail"]


async def test_signup_weak_password(async_client: AsyncClient, mocker):
    payload = {
        "documento_identidad": "87654321",
        "nombres": "Juan",
        "apellidos": "Perez",
        "correo": "juan@test.com",
        "password": "weak"
    }
    
    response = await async_client.post("/api/v1/auth/signup", json=payload)
    
    assert response.status_code == 422
