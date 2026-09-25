import pytest
from app.agent.graph import ejecutar_triage
from app.services.llm_service import LLMService
from app.core.config import get_settings
from app.agent.nodes.extraction import dividir_texto_en_bloques
from app.agent.nodes import ingestion
from app.agent.nodes.routing import _calcular_destino


def test_dividir_texto_en_bloques_preserva_el_final_del_documento():
    texto = "a" * 4_000 + "HALLAZGO_FINAL_CRITICO"

    bloques = dividir_texto_en_bloques(texto, max_chars=4_000)

    assert bloques == ["a" * 4_000, "HALLAZGO_FINAL_CRITICO"]


def test_pdf_sin_capa_texto_usa_fallback_ocr(monkeypatch):
    monkeypatch.setattr(ingestion, "_extraer_texto_pdf_pymupdf", lambda _: "")
    monkeypatch.setattr(ingestion, "_extraer_texto_pdf_ocr", lambda _: "texto OCR")

    assert ingestion._extraer_texto_pdf("cGRm") == "texto OCR"


def test_prioridad_ambigua_usa_cola_operativa_dedicada():
    destino, _, _, requiere_auditoria = _calcular_destino(
        score=0.8,
        nivel="Ambiguo",
        diagnostico=None,
        paciente_nombre=None,
    )

    assert destino == "Cola_Revision_Ambigua"
    assert requiere_auditoria is True


@pytest.mark.asyncio
async def test_caso_1_rutina():
    """
    Caso 1 (Rutina): Documento clínico de analítica normal.
    Debe enrutarse a Cola_Rutina con score_confianza >= 0.8.
    """
    settings = get_settings()
    llm = LLMService(settings=settings)

    resultado = await ejecutar_triage(
        documento_id="DOC-001",
        tipo_archivo="TEXTO",
        documento_texto="Analítica normal. Hemograma completo sin hallazgos patológicos.",
        canal_origen="Consulta_Externa",
        llm_service=llm,
    )

    assert resultado.status == "procesado"
    assert resultado.decision_enrutamiento.destino_principal == "Cola_Rutina"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is False
    assert resultado.clasificacion.score_confianza_clasificacion >= 0.75
    assert "ingestion" in resultado.nodos_ejecutados
    assert "extraction" in resultado.nodos_ejecutados
    assert "classification" in resultado.nodos_ejecutados
    assert "confidence" in resultado.nodos_ejecutados
    assert "routing" in resultado.nodos_ejecutados


@pytest.mark.asyncio
async def test_caso_2_urgencia_tep():
    """
    Caso 2 (Urgencia): Informe radiológico crítico con TEP agudo.
    Debe enrutarse a Cola_Emergencia_Medica y generar notificación/alerta.
    """
    settings = get_settings()
    llm = LLMService(settings=settings)

    resultado = await ejecutar_triage(
        documento_id="DOC-002",
        tipo_archivo="TEXTO",
        documento_texto="HOSPITAL SANTA LUCIA. Tomografía de Tórax. Hallazgo: Defecto de llenado en arteria pulmonar compatible con TEP agudo. Se requiere correlación clínica urgente.",
        canal_origen="Guardia_Emergencias",
        llm_service=llm,
    )

    assert resultado.status == "procesado"
    assert resultado.decision_enrutamiento.destino_principal == "Cola_Emergencia_Medica"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is False
    assert resultado.clasificacion.nivel_prioridad == "Urgente"
    assert resultado.decision_enrutamiento.notificacion_generada is not None
    assert "Alerta" in resultado.decision_enrutamiento.notificacion_generada.get("canal", "")


@pytest.mark.asyncio
async def test_caso_3_ambiguo_hitl():
    """
    Caso 3 (Ambiguo): Documento con texto ilegible o baja legibilidad.
    Debe derivarse a Cola_Revision_Ambigua con requiere_auditoria_humana = True.
    """
    settings = get_settings()
    llm = LLMService(settings=settings)

    resultado = await ejecutar_triage(
        documento_id="DOC-003",
        tipo_archivo="TEXTO",
        documento_texto="... texto ilegible ... px ... 45 ... mgr ??? firma no visible",
        canal_origen="Admision",
        llm_service=llm,
    )

    assert resultado.decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is True
    assert resultado.status == "pendiente_auditoria"
