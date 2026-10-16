"""Regresiones del recorrido real del agente con LLM y pacientes simulados."""

import json
from unittest.mock import AsyncMock

import pytest

from app.agent.graph import ejecutar_triage
from app.agent.nodes.confidence import node_confidence
from app.agent.nodes.routing import _calcular_destino
from app.agent.state import AgentState, ClasificacionState


@pytest.mark.parametrize("tipo", ["Receta Médica", "Receta_Medica", "receta medica"])
def test_routing_reconoce_receta_del_catalogo_y_variantes_legadas(tipo):
    destino, _, _, auditoria = _calcular_destino(
        score=0.9,
        nivel="Rutina",
        diagnostico="Tratamiento prescrito",
        paciente_nombre=None,
        tipo_documento=tipo,
    )
    assert destino == "Farmacia_Hospitalaria"
    assert auditoria is False


@pytest.mark.asyncio
async def test_confidence_conserva_clasificacion_y_no_muta_entrada():
    clasificacion = ClasificacionState(
        tipo_documento="Receta Médica",
        categoria_documento="Receta_Medica",
        especialidad="Medicina General",
        nivel_prioridad="Rutina",
        score_confianza_clasificacion=0.8,
    )
    state = AgentState(
        documento_id="LG-ESTADO",
        tipo_archivo="TEXTO",
        documento_texto="Documento sintético de seguimiento.",
        clasificacion=clasificacion,
    )
    original = clasificacion.model_dump()
    salida = await node_confidence(state)
    nueva = salida["clasificacion"].model_dump()
    for campo in original.keys() - {"score_confianza_clasificacion"}:
        assert nueva[campo] == original[campo]
    assert clasificacion.model_dump() == original
    assert nueva["score_confianza_clasificacion"] == pytest.approx(0.7)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tipo, prioridad, metadata, destino, auditoria",
    [
        ("Receta Médica", "Rutina", {}, "Farmacia_Hospitalaria", False),
        ("Receta_Medica", "Rutina", {}, "Farmacia_Hospitalaria", False),
        (
            "Receta Médica",
            "Rutina",
            {"medicamentos_controlados": True},
            "Farmacia_Hospitalaria",
            True,
        ),
        ("Receta Médica", "Urgente", {}, "Cola_Emergencia_Medica", False),
        ("Informe Clínico", "Rutina", {}, "Cola_Rutina", False),
        ("Receta Médica", "Ambiguo", {}, "Cola_Revision_Ambigua", True),
        (
            "Receta Médica",
            "Rutina",
            {"discrepancia_identidad_detectada": True},
            "Cola_Revision_Ambigua",
            True,
        ),
    ],
)
async def test_grafo_completo_respeta_destinos_y_conserva_datos(
    tipo, prioridad, metadata, destino, auditoria
):
    llm = AsyncMock()
    llm.completar.side_effect = [
        json.dumps({"diagnostico_principal": "Tratamiento del documento", "cie10_sugerido": "i10"}),
        json.dumps({"tipo_documento": tipo, "nivel_prioridad": prioridad}),
    ]
    original_metadata = dict(metadata)
    resultado = await ejecutar_triage(
        documento_id="LG-RECORRIDO",
        tipo_archivo="TEXTO",
        documento_texto="Documento sintético suficientemente legible para comprobar integración.",
        metadata=metadata,
        llm_service=llm,
    )
    assert resultado.decision_enrutamiento.destino_principal == destino
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is auditoria
    assert resultado.status == ("pendiente_auditoria" if auditoria else "procesado")
    assert resultado.datos_extraidos.diagnostico_principal == "Tratamiento del documento"
    assert resultado.datos_extraidos.cie10_sugerido == "I10"
    assert resultado.datos_extraidos.cie10_descripcion == "Hipertensión esencial (primaria)"
    assert resultado.nodos_ejecutados == [
        "ingestion",
        "extraction",
        "classification",
        "confidence",
        "routing",
    ]
    assert metadata == original_metadata
    assert llm.completar.await_count == 2


@pytest.mark.asyncio
async def test_error_critico_registra_la_rama_terminal_de_auditoria():
    llm = AsyncMock()
    llm.completar.side_effect = RuntimeError("Fallo sintético del proveedor")
    resultado = await ejecutar_triage(
        documento_id="LG-ERROR",
        tipo_archivo="TEXTO",
        documento_texto="Documento clínico sintético para verificar el error del proveedor.",
        llm_service=llm,
    )
    assert resultado.status == "pendiente_auditoria"
    assert resultado.decision_enrutamiento.destino_principal == "Cola_Auditoria_Humana"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is True
    assert resultado.error_mensaje
    assert resultado.nodos_ejecutados == [
        "ingestion",
        "extraction",
        "classification",
        "confidence",
        "forzar_auditoria",
    ]
