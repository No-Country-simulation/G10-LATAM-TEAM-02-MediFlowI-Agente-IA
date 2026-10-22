"""
Tests unitarios y de integración para Guardrails de Seguridad Clínica (Tarea 2.10 / IA-10).

Verifica:
1. User Story 1 (Out-of-Domain Gate): Documentos ajenos (Otro, No_Clinico, Desconocido) se bloquean de colas operativas y van a Cola_Revision_Ambigua.
2. User Story 2 (PDFs Asimétricos): PDFs con páginas digitales y secundarias escaneadas procesan e integran ambos folios.
3. User Story 3 (Red Flags & Coherencia Semántica): Patologías de riesgo vital con prioridad Rutina anulan confianza a 0.0 y van a auditoría prioritaria.
4. Cumplimiento de contrato guardrails.contract.json.
"""

import base64
import io
import json
from unittest.mock import AsyncMock, Mock

import fitz
import pytest
from PIL import Image

from app.agent.clinical_guardrails import (
    es_documento_fuera_de_dominio,
    evaluar_red_flags,
)
from app.agent.nodes.confidence import node_confidence
from app.agent.nodes.ingestion import node_ingestion
from app.agent.nodes.routing import node_routing
from app.agent.state import AgentState, ClasificacionState, DatosExtraidosState

# ── Fixtures y Generadores de Casos Adversarios ─────────────────────────────

def crear_pdf_asimetrico_2_paginas(
    texto_p1: str = "Hospital Central. Control rutinario anual. Paciente asintomático. Signos vitales estables.",
    texto_p2_imagen: str = "URGENCIA: Sospecha de infarto agudo de miocardio. Dolor precordial opresivo irradiado a mandíbula.",
) -> str:
    """Genera en memoria un PDF donde la pág 1 es digital y la pág 2 es una imagen escaneada."""
    doc = fitz.open()

    # Página 1: Digital nativa
    p1 = doc.new_page()
    p1.insert_text((50, 72), texto_p1)

    # Página 2: Escaneada (sin texto vectorial, solo imagen incrustada)
    p2 = doc.new_page()
    with Image.new("RGB", (600, 800), color=(245, 245, 245)) as img, io.BytesIO() as buf:
        # Guardar imagen PNG para incrustar en pág 2
        img.save(buf, format="PNG")
        p2.insert_image(fitz.Rect(50, 50, 550, 750), stream=buf.getvalue())

    pdf_bytes = doc.tobytes()
    doc.close()
    return base64.b64encode(pdf_bytes).decode()


def crear_pdf_100_digital(
    texto_p1: str = "Hospital Central. Consulta ambulatoria de rutina. Todo normal sin patología activa.",
    texto_p2: str = "Plan de seguimiento en 6 meses. No requiere estudios complementarios ni medicación.",
) -> str:
    """Genera un PDF multipágina 100% digital nativo."""
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_text((50, 72), texto_p1)
    p2 = doc.new_page()
    p2.insert_text((50, 72), texto_p2)
    pdf_bytes = doc.tobytes()
    doc.close()
    return base64.b64encode(pdf_bytes).decode()


# ── Pruebas de Unidad para Funciones Puras del Guardrail ────────────────────

def test_es_documento_fuera_de_dominio_detecta_categorias_no_clinicas():
    """Valida detección estricta de documentos que no deben entrar a colas operativas."""
    assert es_documento_fuera_de_dominio("Otro") is True
    assert es_documento_fuera_de_dominio("No_Clinico") is True
    assert es_documento_fuera_de_dominio("Desconocido") is True
    assert es_documento_fuera_de_dominio("Revista de Viajes") is True
    assert es_documento_fuera_de_dominio("Factura Comercial") is True
    assert es_documento_fuera_de_dominio("") is True
    assert es_documento_fuera_de_dominio(None) is True

    # Documentos clínicos válidos NO deben ser catalogados como fuera de dominio
    assert es_documento_fuera_de_dominio("Informe Clínico") is False
    assert es_documento_fuera_de_dominio("Receta Médica") is False
    assert es_documento_fuera_de_dominio("Informe de Laboratorio") is False
    assert es_documento_fuera_de_dominio("Epicrisis") is False


def test_evaluar_red_flags_detecta_patologias_de_riesgo_vital():
    """Valida detección de TEP, IAM, Shock, ACV tanto por término como por CIE-10."""
    es_rf, nombre = evaluar_red_flags(diagnostico="Sospecha de Tromboembolismo Pulmonar")
    assert es_rf is True
    assert "TEP" in nombre or "Tromboembolismo" in nombre

    es_rf, nombre = evaluar_red_flags(hallazgos=["Signos de infarto agudo de miocardio"])
    assert es_rf is True
    assert "IAM" in nombre or "Infarto" in nombre

    es_rf, nombre = evaluar_red_flags(cie10="I21.9")
    assert es_rf is True
    assert "I21.9" in nombre

    es_rf, nombre = evaluar_red_flags(diagnostico="Shock séptico de origen urinario")
    assert es_rf is True
    assert "Shock" in nombre


def test_evaluar_red_flags_respeta_contexto_de_negacion():
    """Si el hallazgo indica 'se descarta TEP', no debe disparar falso positivo."""
    es_rf, _ = evaluar_red_flags(diagnostico="Se descarta tromboembolismo pulmonar")
    assert es_rf is False

    es_rf, _ = evaluar_red_flags(hallazgos=["Sin signos de infarto agudo de miocardio"])
    assert es_rf is False

    es_rf, _ = evaluar_red_flags(diagnostico="Descarte de accidente cerebrovascular")
    assert es_rf is False


# ── USER STORY 1: Filtro Fuera de Dominio (Out-of-Domain Gate) ──────────────

@pytest.mark.asyncio
async def test_us1_documento_no_clinico_bloquea_cola_rutina():
    """US1: Documento clasificado como 'Otro' con prioridad 'Rutina' NO debe ir a Cola_Rutina."""
    state = AgentState(
        documento_id="DOC-AFICHE-01",
        tipo_archivo="TEXTO",
        documento_texto="Festival de Rock 2026. Entradas en venta.",
    )
    state.clasificacion = ClasificacionState(
        tipo_documento="Otro",
        nivel_prioridad="Rutina",
        score_confianza_clasificacion=0.95,
    )

    resultado = await node_routing(state)
    decision = resultado["decision_enrutamiento"]

    assert decision.destino_principal == "Cola_Revision_Ambigua"
    assert decision.requiere_auditoria_humana is True
    assert resultado["status"] == "pendiente_auditoria"
    assert resultado["metadata"].get("fuera_de_dominio_clinico") is True
    assert resultado["metadata"].get("motivo_retencion") == "fuera_de_dominio_clinico"


@pytest.mark.asyncio
async def test_us1_documento_no_clinico_bloquea_cola_emergencia():
    """US1: Documento clasificado como 'Otro' que alucine prioridad 'Urgente' NO debe ir a emergencias."""
    state = AgentState(
        documento_id="DOC-REVISTA-02",
        tipo_archivo="IMAGEN",
    )
    state.clasificacion = ClasificacionState(
        tipo_documento="Otro",
        nivel_prioridad="Urgente",
        score_confianza_clasificacion=0.90,
    )

    resultado = await node_routing(state)
    decision = resultado["decision_enrutamiento"]

    assert decision.destino_principal == "Cola_Revision_Ambigua"
    assert decision.requiere_auditoria_humana is True
    assert resultado["status"] == "pendiente_auditoria"
    assert resultado["metadata"].get("fuera_de_dominio_clinico") is True


# ── USER STORY 2: Inspección Página por Página de PDFs Asimétricos ───────────

@pytest.mark.asyncio
async def test_us2_pdf_asimetrico_detecta_y_consolida_ambas_paginas():
    """US2: PDF con pág 1 digital y pág 2 escaneada extrae ambas páginas y activa metadata de asimetría."""
    pdf_b64 = crear_pdf_asimetrico_2_paginas(
        texto_p1="Consulta médica rutinaria. Paciente afebril.",
        texto_p2_imagen="URGENCIA: Sospecha de infarto agudo de miocardio.",
    )

    state = AgentState(
        documento_id="DOC-PDF-ASIM-01",
        tipo_archivo="PDF",
        documento_base64=pdf_b64,
        metadata={},
    )

    # Mock de LLM Service para la página escaneada
    mock_llm = Mock()
    mock_llm.disponible = True
    mock_llm.completar_multimodal = AsyncMock(
        return_value="URGENCIA: Sospecha de infarto agudo de miocardio. Dolor precordial agudo."
    )

    resultado = await node_ingestion(state, llm_service=mock_llm)

    texto_final = resultado.get("texto_extraido", "")
    metadata = resultado.get("metadata", {})

    # Debe contener texto de la página digital 1
    assert "Consulta médica rutinaria" in texto_final
    # Debe contener la transcripción de la página 2 escaneada
    assert "infarto agudo de miocardio" in texto_final.lower()

    # Metadatos requeridos por US2
    assert metadata.get("documento_asimetrico_detectado") is True
    assert metadata.get("paginas_visuales_procesadas") == 1
    assert metadata.get("paginas_rasterizadas_ocr") == [2]

    # Saneamiento de memoria Base64
    assert resultado.get("documento_base64") is None


@pytest.mark.asyncio
async def test_us2_pdf_100_digital_no_activa_vision():
    """US2: PDF 100% digital nativo no dispara llamadas de visión y mantiene método TEXT_EXTRACTION."""
    pdf_b64 = crear_pdf_100_digital(
        texto_p1="Página 1: Control de laboratorio normal.",
        texto_p2="Página 2: Todo en orden, sin tratamientos nuevos.",
    )

    state = AgentState(
        documento_id="DOC-PDF-DIGITAL-02",
        tipo_archivo="PDF",
        documento_base64=pdf_b64,
        metadata={},
    )

    mock_llm = Mock()
    mock_llm.disponible = True
    mock_llm.completar_multimodal = AsyncMock()

    resultado = await node_ingestion(state, llm_service=mock_llm)

    # No debe llamar a visión
    mock_llm.completar_multimodal.assert_not_called()

    assert resultado.get("metodo_extraccion") == "TEXT_EXTRACTION"
    assert "Página 1: Control de laboratorio" in resultado.get("texto_extraido", "")
    assert "Página 2: Todo en orden" in resultado.get("texto_extraido", "")
    assert resultado.get("metadata", {}).get("documento_asimetrico_detectado") is not True


# ── USER STORY 3: Validación Cruzada y Matriz de Red Flags ───────────────────

@pytest.mark.asyncio
async def test_us3_red_flag_discordancia_anula_confianza_a_cero():
    """US3: Diagnóstico de riesgo vital (TEP) con prioridad Rutina anula confianza a 0.0 y enruta a ambigua."""
    state = AgentState(
        documento_id="DOC-RED-FLAG-01",
        tipo_archivo="TEXTO",
        documento_texto="Paciente masculino con sospecha fundada de Tromboembolismo Pulmonar masivo.",
    )
    state.datos_extraidos = DatosExtraidosState(
        diagnostico_principal="Tromboembolismo pulmonar",
        cie10_sugerido="I26.9",
        hallazgos_clave=["Disnea súbita", "Taquicardia", "Dímero D elevado"],
    )
    # Modelo alucina o asigna erróneamente prioridad Rutina
    state.clasificacion = ClasificacionState(
        tipo_documento="Informe Clínico",
        nivel_prioridad="Rutina",
        score_confianza_clasificacion=0.92,
    )

    # 1. Ejecutar nodo confidence
    res_conf = await node_confidence(state)
    score_conf = res_conf["clasificacion"].score_confianza_clasificacion
    meta_conf = res_conf["metadata"]

    # Debe forzar score a 0.0 absoluto
    assert score_conf == 0.0
    assert meta_conf.get("discordancia_critica_red_flags") is True
    assert meta_conf.get("motivo_retencion") == "discordancia_critica_red_flags"
    assert "TEP" in meta_conf.get("red_flag_detectada", "") or "Tromboembolismo" in meta_conf.get("red_flag_detectada", "")

    # 2. Ejecutar nodo routing con el estado penalizado
    state.clasificacion = res_conf["clasificacion"]
    state.metadata = meta_conf

    res_rout = await node_routing(state)
    decision = res_rout["decision_enrutamiento"]

    assert decision.destino_principal == "Cola_Revision_Ambigua"
    assert decision.requiere_auditoria_humana is True
    assert decision.motivo_retencion == "discordancia_critica_red_flags"
    assert res_rout["status"] == "pendiente_auditoria"


@pytest.mark.asyncio
async def test_us3_red_flag_con_urgente_no_es_discordancia():
    """US3: Diagnóstico de riesgo vital (IAM) clasificado como Urgente opera normalmente y genera alerta."""
    state = AgentState(
        documento_id="DOC-RED-FLAG-OK",
        tipo_archivo="TEXTO",
        documento_texto="Paciente con infarto agudo de miocardio en evolución.",
    )
    state.datos_extraidos = DatosExtraidosState(
        diagnostico_principal="Infarto agudo de miocardio",
        cie10_sugerido="I21.9",
    )
    state.clasificacion = ClasificacionState(
        tipo_documento="Informe Clínico",
        nivel_prioridad="Urgente",
        score_confianza_clasificacion=0.88,
    )

    res_conf = await node_confidence(state)
    score_conf = res_conf["clasificacion"].score_confianza_clasificacion
    meta_conf = res_conf["metadata"]

    # NO debe penalizar score ni marcar discordancia
    assert score_conf >= 0.75
    assert meta_conf.get("discordancia_critica_red_flags") is not True

    state.clasificacion = res_conf["clasificacion"]
    state.metadata = meta_conf

    res_rout = await node_routing(state)
    decision = res_rout["decision_enrutamiento"]

    assert decision.destino_principal == "Cola_Emergencia_Medica"
    assert decision.notificacion_generada is not None


# ── CONTRATOS: Validación contra guardrails.contract.json ─────────────────────

def test_cumplimiento_contrato_guardrails():
    """Valida que los resultados de guardrails cumplen estrictamente el contrato JSON schema."""
    from pathlib import Path

    import jsonschema

    contract_path = (
        Path(__file__).parents[2]
        / "specs"
        / "016-clinical-safety-guardrails"
        / "contracts"
        / "guardrails.contract.json"
    )
    schema = json.loads(contract_path.read_text(encoding="utf-8"))

    # 1. Caso Fuera de Dominio
    caso_fuera_dominio = {
        "documento_id": "DOC-AFICHE-99",
        "fuera_de_dominio_clinico": True,
        "tipo_documento_rechazado": "Otro",
        "documento_asimetrico_detectado": False,
        "paginas_visuales_procesadas": 0,
        "discordancia_critica_red_flags": False,
        "red_flag_detectada": None,
        "score_confianza_final": 0.85,
        "destino_enrutamiento": "Cola_Revision_Ambigua",
        "requiere_auditoria_humana": True,
        "status": "pendiente_auditoria",
    }
    jsonschema.validate(instance=caso_fuera_dominio, schema=schema)

    # 2. Caso Discordancia Crítica (Red Flag)
    caso_discordancia = {
        "documento_id": "DOC-TEP-ERR",
        "fuera_de_dominio_clinico": False,
        "tipo_documento_rechazado": None,
        "documento_asimetrico_detectado": False,
        "paginas_visuales_procesadas": 0,
        "discordancia_critica_red_flags": True,
        "red_flag_detectada": "Tromboembolismo Pulmonar (TEP)",
        "score_confianza_final": 0.0,
        "destino_enrutamiento": "Cola_Revision_Ambigua",
        "requiere_auditoria_humana": True,
        "status": "pendiente_auditoria",
    }
    jsonschema.validate(instance=caso_discordancia, schema=schema)

    # 3. Caso PDF Asimétrico Válido
    caso_asimetrico = {
        "documento_id": "DOC-PDF-ASIM",
        "fuera_de_dominio_clinico": False,
        "tipo_documento_rechazado": None,
        "documento_asimetrico_detectado": True,
        "paginas_visuales_procesadas": 1,
        "discordancia_critica_red_flags": False,
        "red_flag_detectada": None,
        "score_confianza_final": 0.90,
        "destino_enrutamiento": "Cola_Rutina",
        "requiere_auditoria_humana": False,
        "status": "procesado",
    }
    jsonschema.validate(instance=caso_asimetrico, schema=schema)



