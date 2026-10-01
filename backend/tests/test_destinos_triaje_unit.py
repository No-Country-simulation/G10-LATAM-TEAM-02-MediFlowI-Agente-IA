import pytest
from app.agent.state import AgentState, DecisionEnrutamientoState
from app._generated.models import DecisionEnrutamiento as ModelDecisionEnrutamiento


def test_decision_enrutamiento_state_supports_farmacia_hospitalaria():
    """Verifica que tanto DecisionEnrutamientoState como el modelo Pydantic aceptan 'Farmacia_Hospitalaria'."""
    decision_state = DecisionEnrutamientoState(
        destino_principal="Farmacia_Hospitalaria",
        justificacion_enrutamiento="Requiere dispensación inmediata de antibióticos parenterales.",
        requiere_auditoria_humana=False,
    )
    assert decision_state.destino_principal == "Farmacia_Hospitalaria"

    decision_model = ModelDecisionEnrutamiento(
        destino_principal="Farmacia_Hospitalaria",
        justificacion_enrutamiento="Derivación a farmacia clínica hospitalaria.",
        requiere_auditoria_humana=False,
    )
    assert decision_model.destino_principal == "Farmacia_Hospitalaria"


def test_agent_state_default_canal_origen():
    """Verifica que el estado del agente y los documentos admiten canal de origen clínico."""
    state = AgentState(
        documento_id="DOC-TRIAGE-001",
        tipo_archivo="PDF",
        canal_origen="Admision",
    )
    assert state.canal_origen == "Admision"
    assert state.documento_id == "DOC-TRIAGE-001"


def test_all_state_destinos_are_valid():
    """Verifica que todos los destinos de enrutamiento son permitidos en DecisionEnrutamientoState."""
    destinos_esperados = [
        "Cola_Emergencia_Medica",
        "Cola_Rutina",
        "Farmacia_Hospitalaria",
        "Cola_Auditoria_Humana",
        "Cola_Revision_Ambigua",
    ]
    for d in destinos_esperados:
        dec = DecisionEnrutamientoState(
            destino_principal=d,
            justificacion_enrutamiento="Prueba de destino hospitalario unificado.",
            requiere_auditoria_humana=(d in ["Cola_Revision_Ambigua", "Cola_Auditoria_Humana"]),
        )
        assert dec.destino_principal == d
