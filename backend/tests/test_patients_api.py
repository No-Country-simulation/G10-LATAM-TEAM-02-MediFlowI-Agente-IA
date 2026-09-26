import pytest

from app.agent.state import AgentState
from app.api.v1.patients import PatientCreateRequest
from app.repositories import patient_repository
from app.repositories.postgres_storage import DatabaseUnavailableError
from app.services.triage_service import aplicar_asociacion_paciente


def test_patient_sex_is_optional_without_a_default_value():
    patient = PatientCreateRequest(
        numero_documento="12345678",
        nombres="Ana",
        apellidos="Pérez",
    )

    assert patient.sexo is None


async def test_resolver_paciente_detecta_conflicto_entre_dni_y_hc(monkeypatch):
    async def paciente_por_dni(_: str):
        return {"id": "paciente-dni"}

    async def paciente_por_hc(_: str):
        return {"id": "paciente-hc"}

    monkeypatch.setattr(patient_repository, "get_patient_by_doc", paciente_por_dni)
    monkeypatch.setattr(patient_repository, "get_patient_by_hc", paciente_por_hc)

    resultado = await patient_repository.resolver_paciente_por_identificadores("12345678", "HC-1")

    assert resultado == {"estado": "conflicto", "paciente": None}


def test_conflicto_de_identificadores_fuerza_revision_ambigua():
    resultado = AgentState(documento_id="DOC-CONFLICTO", tipo_archivo="TEXTO")

    aplicar_asociacion_paciente(resultado, {"estado": "conflicto", "paciente": None})

    assert resultado.metadata["asociacion_paciente"] == "conflicto"
    assert resultado.decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"
    assert resultado.status == "pendiente_auditoria"


async def test_patient_repository_never_falls_back_to_memory(monkeypatch):
    async def unavailable_pool():
        return None

    monkeypatch.setattr(patient_repository, "get_db_pool", unavailable_pool)

    with pytest.raises(DatabaseUnavailableError):
        await patient_repository.list_patients()


def test_patients_api_reports_postgresql_unavailable(client, bearer_headers, monkeypatch):
    async def unavailable_list(search=None):
        raise DatabaseUnavailableError("database down")

    monkeypatch.setattr(patient_repository, "list_patients", unavailable_list)
    response = client.get("/api/v1/patients", headers=bearer_headers)

    assert response.status_code == 503
    assert response.json()["detail"]["error"] == "POSTGRESQL_NO_DISPONIBLE"


async def test_association_does_not_create_a_missing_document(monkeypatch):
    class Connection:
        async def execute(self, *_args):
            return "UPDATE 0"

    class AcquireContext:
        async def __aenter__(self):
            return Connection()

        async def __aexit__(self, *_args):
            return None

    class Pool:
        def acquire(self):
            return AcquireContext()

    async def available_pool():
        return Pool()

    monkeypatch.setattr(patient_repository, "get_db_pool", available_pool)

    associated = await patient_repository.associate_document_to_patient(
        "11111111-2222-3333-4444-555555555555", "DOC-INEXISTENTE"
    )

    assert associated is False
