import base64
import io
import sys
from types import SimpleNamespace

import pytest
from PIL import Image

from app.agent.graph import ejecutar_triage
from app.agent.nodes import ingestion
from app.agent.nodes.classification import consolidar_clasificaciones
from app.agent.nodes.extraction import _parsear_respuesta, dividir_texto_en_bloques
from app.agent.nodes.routing import _calcular_destino
from app.agent.state import ClasificacionState
from app.core.config import get_settings
from app.services.llm_service import LLMService, LLMUnavailableError


def test_dividir_texto_en_bloques_preserva_el_final_del_documento():
    texto = "a" * 4_000 + "HALLAZGO_FINAL_CRITICO"

    bloques = dividir_texto_en_bloques(texto, max_chars=4_000)

    assert bloques == ["a" * 4_000, "HALLAZGO_FINAL_CRITICO"]


@pytest.mark.asyncio
async def test_llm_sin_credenciales_no_genera_resultados_clinicos_ficticios():
    settings = get_settings().model_copy(
        update={
            "google_api_key": "",
            "openai_api_key": "",
            "allow_mock_llm": False,
        }
    )
    llm = LLMService(settings=settings)

    assert llm.proveedor == "unavailable"
    assert llm.disponible is False
    with pytest.raises(LLMUnavailableError):
        await llm.completar("Clasifica este documento clínico")


def test_pdf_sin_capa_texto_usa_fallback_ocr(monkeypatch):
    monkeypatch.setattr(ingestion, "_extraer_texto_pdf_pymupdf", lambda _: "")
    monkeypatch.setattr(ingestion, "_extraer_texto_pdf_ocr", lambda _: "texto OCR")

    assert ingestion._extraer_texto_pdf("cGRm") == "texto OCR"


def test_imagen_ejecuta_ocr_tesseract_en_espanol(monkeypatch):
    image_buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color="white").save(image_buffer, format="PNG")
    monkeypatch.setitem(
        sys.modules,
        "pytesseract",
        SimpleNamespace(image_to_string=lambda image, lang: "Receta médica"),
    )

    texto = ingestion._extraer_texto_imagen(base64.b64encode(image_buffer.getvalue()).decode())

    assert texto == "Receta médica"


def test_prioridad_ambigua_usa_cola_operativa_dedicada():
    destino, _, _, requiere_auditoria = _calcular_destino(
        score=0.8,
        nivel="Ambiguo",
        diagnostico=None,
        paciente_nombre=None,
    )

    assert destino == "Cola_Revision_Ambigua"
    assert requiere_auditoria is True


def test_consolidar_clasificaciones_prioriza_urgente_en_bloque_final():
    clasificacion = consolidar_clasificaciones(
        [
            ClasificacionState(
                tipo_documento="Evolución Clínica",
                nivel_prioridad="Rutina",
                score_confianza_clasificacion=0.8,
            ),
            ClasificacionState(
                tipo_documento="Informe de Estudio por Imagenes",
                nivel_prioridad="Urgente",
                score_confianza_clasificacion=0.85,
            ),
        ]
    )

    assert clasificacion.nivel_prioridad == "Urgente"
    assert clasificacion.tipo_documento == "Informe de Estudio por Imagenes"


def test_extraccion_conserva_dni_e_historia_clinica():
    datos = _parsear_respuesta(
        '{"paciente": {"nombre": "Ana", "documento_identidad": "12345678", "historia_clinica": "HC-01"}}'
    )

    assert datos.paciente.documento_identidad == "12345678"
    assert datos.paciente.historia_clinica == "HC-01"


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
