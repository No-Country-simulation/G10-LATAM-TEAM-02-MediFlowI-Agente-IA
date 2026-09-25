from app.api.v1.patients import PatientCreateRequest
from app.repositories import patient_repository
from app.agent.state import AgentState
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
