"""Pruebas unitarias e integración para la Ingesta Multimodal (Vision + OCR Fallback).

Feature: specs/009-multimodal-vision-ocr
"""

import base64
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.messages import AIMessage
from PIL import Image

from app.agent.nodes.ingestion import (
    _extraer_texto_imagen,
    _extraer_texto_pdf,
    node_ingestion,
)
from app.agent.state import AgentState
from app.core.config import Settings
from app.services.llm_service import LLMService, LLMUnavailableError


@pytest.fixture
def mock_settings():
    return Settings(
        google_api_key="your-test-placeholder",
        openai_api_key="your-test-placeholder",
        allow_mock_llm=True,
    )


@pytest.fixture
def sample_image_base64():
    """Genera una imagen PNG pequeña válida en base64."""
    img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@pytest.fixture
def sample_empty_pdf_base64():
    """Genera un PDF válido de 1 página en blanco (sin texto embebido) en base64."""
    import fitz

    doc = fitz.open()
    doc.new_page(width=300, height=300)
    pdf_bytes = doc.tobytes()
    doc.close()
    return base64.b64encode(pdf_bytes).decode("utf-8")


# ── T003: Suite base para LLMService.completar_multimodal ────────────────────


@pytest.mark.asyncio
async def test_llm_service_completar_multimodal_mock(mock_settings, sample_image_base64):
    """Verifica que completar_multimodal funcione correctamente en modo mock."""
    service = LLMService(settings=mock_settings)
    assert service.disponible is True
    assert service.proveedor == "mock"

    res = await service.completar_multimodal(
        prompt="Transcribe esta orden médica",
        imagenes=[{"mime_type": "image/png", "data_base64": sample_image_base64}],
    )
    assert isinstance(res, str)
    assert len(res) > 0
    assert "CLÍNICO" in res or "Paciente" in res


@pytest.mark.asyncio
async def test_llm_service_completar_multimodal_unavailable(mock_settings, sample_image_base64):
    """Verifica que completar_multimodal lance LLMUnavailableError si no hay proveedor."""
    service = LLMService(settings=mock_settings)
    service._provider = "unavailable"
    service._client = None

    with pytest.raises(LLMUnavailableError):
        await service.completar_multimodal(
            prompt="Transcribe",
            imagenes=[sample_image_base64],
        )


@pytest.mark.asyncio
async def test_llm_service_completar_multimodal_invokes_client(mock_settings, sample_image_base64):
    """Verifica que se construya el HumanMessage con bloque de tipo image_url."""
    service = LLMService(settings=mock_settings)
    mock_client = MagicMock()
    mock_client.ainvoke = AsyncMock(
        return_value=AIMessage(content="Paciente: Carlos Ramos, Diagnóstico: Rinitis")
    )
    service._client = mock_client
    service._provider = "gemini"

    resultado = await service.completar_multimodal(
        prompt="Extrae texto clínico",
        imagenes=[{"mime_type": "image/png", "data_base64": sample_image_base64}],
    )

    assert resultado == "Paciente: Carlos Ramos, Diagnóstico: Rinitis"
    mock_client.ainvoke.assert_called_once()
    messages_passed = mock_client.ainvoke.call_args[0][0]
    human_msg = messages_passed[0]
    assert isinstance(human_msg.content, list)
    assert human_msg.content[0]["type"] == "text"
    assert human_msg.content[1]["type"] == "image_url"
    assert "data:image/png;base64," in human_msg.content[1]["image_url"]["url"]


# ── T005: US1 - Extracción de imagen médica con Gemini Vision ────────────────


@pytest.mark.asyncio
async def test_node_ingestion_imagen_usa_vision_multimodal(mock_settings, sample_image_base64):
    """Verifica que node_ingestion procese imágenes invocando llm_service.completar_multimodal."""
    service = LLMService(settings=mock_settings)
    service.completar_multimodal = AsyncMock(
        return_value="Receta Médica\nPaciente: María López\nAmoxicilina 500mg"
    )

    state = AgentState(
        documento_id="DOC-IMG-001",
        tipo_archivo="IMAGEN",
        documento_base64=sample_image_base64,
    )

    res = await node_ingestion(state, llm_service=service)

    assert "María López" in res["texto_extraido"]
    assert res.get("metodo_extraccion") == "MULTIMODAL_VISION"
    assert "ingestion" in res["nodos_ejecutados"]


# ── T008: US2 - Detección y rasterización de PDF escaneado (< 50 chars) ──────


@pytest.mark.asyncio
async def test_node_ingestion_pdf_escaneado_activa_vision_multimodal(
    mock_settings, sample_empty_pdf_base64
):
    """Verifica que un PDF con texto < 50 chars active la rasterización y visión multimodal."""
    service = LLMService(settings=mock_settings)
    service.completar_multimodal = AsyncMock(
        return_value="Informe Escaneado\nPaciente: Roberto Díaz\nDiagnóstico: Hernia Inguinal"
    )

    state = AgentState(
        documento_id="DOC-SCAN-001",
        tipo_archivo="PDF",
        documento_base64=sample_empty_pdf_base64,
    )

    res = await node_ingestion(state, llm_service=service)

    assert "Roberto Díaz" in res["texto_extraido"]
    assert res.get("metodo_extraccion") == "MULTIMODAL_VISION"
    service.completar_multimodal.assert_called_once()


# ── T010: US3 - Fallback de resiliencia y degradación elegante ────────────────


@pytest.mark.asyncio
async def test_fallback_a_ocr_local_si_falla_vision_multimodal(mock_settings, sample_image_base64):
    """Si vision multimodal falla, conmuta a OCR local."""
    service = LLMService(settings=mock_settings)
    service.completar_multimodal = AsyncMock(side_effect=RuntimeError("Google API Timeout"))

    state = AgentState(
        documento_id="DOC-IMG-ERR-001",
        tipo_archivo="IMAGEN",
        documento_base64=sample_image_base64,
    )

    with patch(
        "app.agent.nodes.ingestion._extraer_texto_imagen_ocr",
        return_value="Texto extraído por OCR local de respaldo",
    ):
        res = await node_ingestion(state, llm_service=service)

        assert res["texto_extraido"] == "Texto extraído por OCR local de respaldo"
        assert res.get("metodo_extraccion") == "LOCAL_OCR"


@pytest.mark.asyncio
async def test_degradacion_elegante_si_ambos_motores_fallan(mock_settings, sample_image_base64):
    """Si fallan tanto visión como OCR local, el agente no lanza 500 y deriva controladamente."""
    service = LLMService(settings=mock_settings)
    service.completar_multimodal = AsyncMock(side_effect=RuntimeError("Cuota agotada"))

    state = AgentState(
        documento_id="DOC-IMG-FAIL-ALL",
        tipo_archivo="IMAGEN",
        documento_base64=sample_image_base64,
    )

    with patch(
        "app.agent.nodes.ingestion._extraer_texto_imagen_ocr",
        side_effect=RuntimeError("Tesseract no está instalado en el sistema"),
    ):
        res = await node_ingestion(state, llm_service=service)

        assert res["texto_extraido"] == ""
        assert "error_mensaje" in res
        assert "ingestion" in res["nodos_ejecutados"]
