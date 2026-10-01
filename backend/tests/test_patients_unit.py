from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from app.api.v1.patients import PatientCreateRequest


def test_patient_create_request_valid_gender_and_phone():
    """Verifica que el modelo Pydantic valida correctamente el género y el teléfono."""
    req_fem = PatientCreateRequest(
        numero_documento="87654321",
        nombres="María",
        apellidos="López",
        genero="FEMENINO",
        numero_telefono="+51 987654321",
        fecha_nacimiento="1995-05-20",
    )
    assert req_fem.genero == "FEMENINO"
    assert req_fem.numero_telefono == "+51 987654321"
    assert req_fem.fecha_nacimiento == "1995-05-20"

    req_masc = PatientCreateRequest(
        numero_documento="12345678",
        nombres="Juan",
        apellidos="Pérez",
        genero="MASCULINO",
        numero_telefono="999888777",
    )
    assert req_masc.genero == "MASCULINO"
    assert req_masc.numero_telefono == "999888777"


def test_patient_create_request_invalid_gender_rejected():
    """Verifica que se rechaza cualquier género fuera de FEMENINO o MASCULINO."""
    with pytest.raises(Exception):
        PatientCreateRequest(
            numero_documento="12345678",
            nombres="Carlos",
            apellidos="Sánchez",
            genero="OTRO_GENERO_NO_PERMITIDO",
        )


def test_api_create_patient_returns_dynamic_age(client: TestClient, bearer_headers: dict):
    """Verifica que al registrar un paciente se calcula y expone dinámicamente la edad."""
    mock_patient_created = {
        "id": "aaaa1111-bbbb-cccc-dddd-eeeeffff0000",
        "tipo_documento": "DNI",
        "numero_documento": "45678901",
        "nombres": "Rosa",
        "apellidos": "Melgar",
        "numero_historia_clinica": "HC-45678901",
        "fecha_nacimiento": "1994-01-15",
        "genero": "FEMENINO",
        "numero_telefono": "912345678",
        "edad": 32,
        "creado_en": "2026-09-30T10:00:00Z",
    }

    with (
        patch("app.repositories.patient_repository.get_patient_by_doc", new_callable=AsyncMock) as mock_by_doc,
        patch("app.repositories.patient_repository.create_patient", new_callable=AsyncMock) as mock_create,
    ):
        mock_by_doc.return_value = None
        mock_create.return_value = mock_patient_created

        response = client.post(
            "/api/v1/patients",
            headers=bearer_headers,
            json={
                "numero_documento": "45678901",
                "nombres": "Rosa",
                "apellidos": "Melgar",
                "genero": "FEMENINO",
                "numero_telefono": "912345678",
                "fecha_nacimiento": "1994-01-15",
            },
        )

        assert response.status_code == 201
        data = response.json()
        paciente = data["paciente"]
        assert paciente["numero_documento"] == "45678901"
        assert paciente["genero"] == "FEMENINO"
        assert paciente["numero_telefono"] == "912345678"
        assert paciente["edad"] == 32
        assert "contacto" not in paciente  # contacto fue reemplazado por numero_telefono


def test_api_create_patient_duplicate_dni_returns_400(client: TestClient, bearer_headers: dict):
    """Verifica que intentar registrar un DNI existente retorna 400 Bad Request."""
    existing_patient = {
        "id": "existente-id",
        "numero_documento": "11223344",
        "nombres": "Existente",
        "apellidos": "Ya Registrado",
    }
    with patch("app.repositories.patient_repository.get_patient_by_doc", new_callable=AsyncMock) as mock_by_doc:
        mock_by_doc.return_value = existing_patient

        response = client.post(
            "/api/v1/patients",
            headers=bearer_headers,
            json={
                "numero_documento": "11223344",
                "nombres": "Duplicado",
                "apellidos": "Prueba",
            },
        )
        assert response.status_code == 400
        assert "Ya existe un paciente" in response.json()["detail"]
