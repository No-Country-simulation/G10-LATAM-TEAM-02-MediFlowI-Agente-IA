from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient


def test_create_user_coordinador_success(client: TestClient, admin_bearer_headers: dict):
    """Verifica que un administrador puede registrar un usuario con rol COORDINADOR y especialidad médica."""
    mock_user = {
        "id": "77777777-8888-9999-0000-111111111111",
        "documento_identidad": "88776655",
        "nombres": "Sofía",
        "apellidos": "Mendoza",
        "correo": "sofia.mendoza@hospital.gob.pe",
        "telefono": "987654321",
        "rol": "COORDINADOR",
        "especialidad_medica": "Medicina de Urgencias",
        "estado": "ACTIVO",
        "created_at": "2026-09-30T12:00:00Z",
        "updated_at": "2026-09-30T12:00:00Z",
    }
    with (
        patch("app.api.v1.users.get_user_by_document", new_callable=AsyncMock) as mock_get,
        patch("app.api.v1.users.create_user", new_callable=AsyncMock) as mock_create,
    ):
        mock_get.return_value = None
        mock_create.return_value = mock_user

        response = client.post(
            "/api/v1/users/",
            headers=admin_bearer_headers,
            json={
                "documento_identidad": "88776655",
                "password": "PasswordSeguro123!",
                "nombres": "Sofía",
                "apellidos": "Mendoza",
                "correo": "sofia.mendoza@hospital.gob.pe",
                "telefono": "987654321",
                "rol": "COORDINADOR",
                "especialidad_medica": "Medicina de Urgencias",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["documento_identidad"] == "88776655"
        assert data["rol"] == "COORDINADOR"
        assert data["especialidad_medica"] == "Medicina de Urgencias"


def test_create_user_invalid_role_rejected(client: TestClient, admin_bearer_headers: dict):
    """Verifica que la API rechaza roles hospitalarios no reconocidos."""
    response = client.post(
        "/api/v1/users/",
        headers=admin_bearer_headers,
        json={
            "documento_identidad": "88776655",
            "password": "PasswordSeguro123!",
            "nombres": "Falso",
            "apellidos": "Usuario",
            "correo": "falso@hospital.gob.pe",
            "telefono": "987654321",
            "rol": "SUPER_DOCTOR_NO_EXISTE",
        },
    )
    assert response.status_code == 422


def test_update_user_specialty_success(client: TestClient, admin_bearer_headers: dict):
    """Verifica la actualización de la especialidad médica de un usuario clínico."""
    user_id = "77777777-8888-9999-0000-111111111111"
    existing_user = {
        "id": user_id,
        "documento_identidad": "12345678",
        "nombres": "Carlos",
        "apellidos": "García",
        "correo": "carlos.garcia@hospital.gob.pe",
        "telefono": "987654321",
        "rol": "COORDINADOR",
        "especialidad_medica": "Medicina General",
        "estado": "ACTIVO",
    }
    updated_user = {
        **existing_user,
        "especialidad_medica": "Cardiología Clínica",
    }
    with (
        patch("app.api.v1.users.get_user_by_id", new_callable=AsyncMock) as mock_get_id,
        patch("app.api.v1.users.update_user", new_callable=AsyncMock) as mock_update,
    ):
        mock_get_id.return_value = existing_user
        mock_update.return_value = updated_user

        response = client.put(
            f"/api/v1/users/{user_id}",
            headers=admin_bearer_headers,
            json={"especialidad_medica": "Cardiología Clínica"},
        )
        assert response.status_code == 200
        assert response.json()["especialidad_medica"] == "Cardiología Clínica"


def test_coordinador_cannot_modify_system_storage_settings(client: TestClient, coordinador_bearer_headers: dict):
    """Verifica que el rol COORDINADOR no puede modificar la configuración crítica del sistema (exclusivo ADMIN)."""
    response = client.post(
        "/api/v1/settings",
        headers=coordinador_bearer_headers,
        json={"storage_mode": "LOCAL"},
    )
    # Debe ser denegado por RBAC con 403 Forbidden
    assert response.status_code == 403
