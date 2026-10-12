"""Validación CIE-10 con LLM simulado y sin conexiones clínicas reales."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.graph import ejecutar_triage
from app.agent.nodes.extraction import node_extraction
from app.agent.state import AgentState
from app.api.v1.documents import _format_document_row


@pytest.mark.asyncio
async def test_extraccion_completa_descripcion_sin_reemplazar_diagnostico():
    llm = AsyncMock()
    llm.completar.return_value = json.dumps(
        {
            "diagnostico_principal": "Sospecha de TEP agudo",
            "cie10_sugerido": "i269",
            "cie10_descripcion": "Texto inventado por el LLM",
        }
    )
    result = await node_extraction(
        AgentState(
            documento_id="CIE10-VALIDO", tipo_archivo="TEXTO", documento_texto="Informe clínico"
        ),
        llm_service=llm,
    )
    datos = result["datos_extraidos"]
    assert datos.cie10_sugerido == "I26.9"
    assert datos.cie10_descripcion == "Embolia pulmonar sin mención de corazón pulmonar agudo"
    assert datos.diagnostico_principal == "Sospecha de TEP agudo"
    assert result["metadata"]["cie10_codigos_invalidos"] == []


@pytest.mark.asyncio
@pytest.mark.parametrize("codigo", ["I21.99", "A00.8", "ZZZ"])
async def test_codigo_invalido_conserva_diagnostico_y_fuerza_auditoria(codigo):
    llm = AsyncMock()
    llm.completar.side_effect = [
        json.dumps(
            {"diagnostico_principal": "Diagnóstico del documento", "cie10_sugerido": codigo}
        ),
        json.dumps({"tipo_documento": "Informe Clínico", "nivel_prioridad": "Urgente"}),
    ]
    result = await ejecutar_triage(
        documento_id="CIE10-INVALIDO",
        tipo_archivo="TEXTO",
        documento_texto="Documento clínico con hallazgos para revisión médica.",
        llm_service=llm,
    )
    assert result.datos_extraidos.diagnostico_principal == "Diagnóstico del documento"
    assert result.datos_extraidos.cie10_sugerido is None
    assert result.datos_extraidos.cie10_descripcion is None
    assert result.metadata["cie10_codigos_invalidos"] == [codigo]
    assert result.status == "pendiente_auditoria"
    assert result.decision_enrutamiento.destino_principal == "Cola_Auditoria_Humana"
    assert result.decision_enrutamiento.requiere_auditoria_humana is True
    assert result.nodos_ejecutados == [
        "ingestion",
        "extraction",
        "classification",
        "confidence",
        "routing",
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("codigo", [None, "", "  "])
async def test_codigo_ausente_no_inventa_diagnostico_ni_obliga_auditoria(codigo):
    llm = AsyncMock()
    llm.completar.side_effect = [
        json.dumps({"diagnostico_principal": "Control clínico", "cie10_sugerido": codigo}),
        json.dumps({"tipo_documento": "Informe Clínico", "nivel_prioridad": "Rutina"}),
    ]
    result = await ejecutar_triage(
        documento_id="CIE10-AUSENTE",
        tipo_archivo="TEXTO",
        documento_texto="Documento clínico de seguimiento sin código registrado.",
        llm_service=llm,
    )
    assert result.datos_extraidos.cie10_sugerido is None
    assert result.datos_extraidos.cie10_descripcion is None
    assert result.decision_enrutamiento.requiere_auditoria_humana is False


@pytest.mark.asyncio
async def test_codigo_invalido_en_otro_bloque_no_se_pierde_al_consolidar():
    llm = AsyncMock()
    llm.completar.side_effect = [
        json.dumps({"cie10_sugerido": "I219"}),
        json.dumps({"cie10_sugerido": "A00.8"}),
    ]
    state = AgentState(
        documento_id="CIE10-BLOQUES", tipo_archivo="TEXTO", documento_texto="a" * 4001
    )
    result = await node_extraction(state, llm_service=llm)
    assert result["datos_extraidos"].cie10_sugerido == "I21.9"
    assert (
        result["datos_extraidos"].cie10_descripcion
        == "Infarto agudo del miocardio, sin otra especificación"
    )
    assert result["metadata"]["cie10_codigos_invalidos"] == ["A00.8"]
    assert state.metadata == {}


@pytest.mark.asyncio
async def test_codigo_valido_no_modifica_prioridad_del_agente():
    llm = AsyncMock()
    llm.completar.side_effect = [
        json.dumps({"cie10_sugerido": "J189"}),
        json.dumps({"tipo_documento": "Informe Clínico", "nivel_prioridad": "Rutina"}),
    ]
    result = await ejecutar_triage(
        documento_id="CIE10-PRIORIDAD",
        tipo_archivo="TEXTO",
        documento_texto="Documento clínico sintético para verificar el enrutamiento.",
        llm_service=llm,
    )
    assert result.datos_extraidos.cie10_sugerido == "J18.9"
    assert result.datos_extraidos.cie10_descripcion == "Neumonía, no especificada"
    assert result.clasificacion.nivel_prioridad == "Rutina"
    assert result.decision_enrutamiento.destino_principal == "Cola_Rutina"


def test_consulta_descripcion_desde_codigo_persistido_en_postgresql():
    row = {"documento_id": "CIE10-PERSISTIDO", "cie10_sugerido": "J18.9"}
    document = _format_document_row(row)
    assert document["datos_extraidos"]["cie10_descripcion"] == "Neumonía, no especificada"
    assert row == {"documento_id": "CIE10-PERSISTIDO", "cie10_sugerido": "J18.9"}


def test_consulta_historica_no_conserva_descripcion_inventada():
    row = {
        "clasificacion": {"tipo_documento": "Informe Clínico"},
        "datos_extraidos": {"cie10_sugerido": "I21.9", "cie10_descripcion": "Inventada"},
    }
    document = _format_document_row(row)
    assert (
        document["datos_extraidos"]["cie10_descripcion"]
        == "Infarto agudo del miocardio, sin otra especificación"
    )
    assert row["datos_extraidos"]["cie10_descripcion"] == "Inventada"


def test_api_persiste_codigo_normalizado_y_expone_descripcion(client, bearer_headers):
    llm = AsyncMock()
    llm.disponible = True
    llm.completar.side_effect = [
        json.dumps({"diagnostico_principal": "TEP agudo", "cie10_sugerido": "i269"}),
        json.dumps({"tipo_documento": "Informe Clínico", "nivel_prioridad": "Urgente"}),
    ]
    with (
        patch("app.api.v1.triage.LLMService", return_value=llm),
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.guardar_resultado",
            new_callable=AsyncMock,
        ) as save,
    ):
        save.return_value = True
        response = client.post(
            "/api/v1/triage",
            headers=bearer_headers,
            json={
                "documento_id": "CIE10-API",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Informe clínico con diagnóstico de TEP agudo.",
            },
        )
    assert response.status_code == 200
    datos = response.json()["datos_extraidos"]
    assert datos["cie10_sugerido"] == "I26.9"
    assert datos["cie10_descripcion"] == "Embolia pulmonar sin mención de corazón pulmonar agudo"
    assert datos["diagnostico_principal"] == "TEP agudo"
    persisted = save.await_args.args[0]
    assert persisted.datos_extraidos.cie10_sugerido == "I26.9"
    assert persisted.datos_extraidos.cie10_descripcion == datos["cie10_descripcion"]
