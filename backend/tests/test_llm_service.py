"""Pruebas unitarias para la normalización de respuestas en LLMService."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import AIMessage

from app.core.config import Settings
from app.services.llm_service import LLMService


@pytest.fixture
def mock_settings():
    return Settings(
        google_api_key="your-test-placeholder",
        openai_api_key="your-test-placeholder",
        allow_mock_llm=True,
    )


@pytest.mark.asyncio
async def test_llm_service_completar_str_directo(mock_settings):
    """Verifica que un string primitivo devuelto por el cliente se conserve intacto."""
    service = LLMService(settings=mock_settings)
    mock_client = MagicMock()
    mock_client.ainvoke = AsyncMock(return_value=AIMessage(content='{"resultado": "ok"}'))
    service._client = mock_client
    service._provider = "gemini"

    resultado = await service.completar("prompt de prueba")
    assert isinstance(resultado, str)
    assert resultado == '{"resultado": "ok"}'


@pytest.mark.asyncio
async def test_llm_service_completar_lista_de_strings(mock_settings):
    """Verifica que una lista de cadenas se consolide en una sola cadena continua."""
    service = LLMService(settings=mock_settings)
    mock_client = MagicMock()
    mock_client.ainvoke = AsyncMock(return_value=AIMessage(content=["parte 1 ", "parte 2"]))
    service._client = mock_client
    service._provider = "gemini"

    resultado = await service.completar("prompt de prueba")
    assert isinstance(resultado, str)
    assert resultado == "parte 1 parte 2"


@pytest.mark.asyncio
async def test_llm_service_completar_lista_de_bloques_dict(mock_settings):
    """Verifica que bloques de contenido Gemini [{'type': 'text', 'text': '...'}] se extraigan y unan."""
    service = LLMService(settings=mock_settings)
    mock_client = MagicMock()
    mock_client.ainvoke = AsyncMock(
        return_value=AIMessage(
            content=[
                {"type": "text", "text": '```json\n{"diagnostico": '},
                {"type": "text", "text": '"Amigdalitis"}\n```'},
            ]
        )
    )
    service._client = mock_client
    service._provider = "gemini"

    resultado = await service.completar("prompt de prueba")
    assert isinstance(resultado, str)
    assert resultado == '```json\n{"diagnostico": "Amigdalitis"}\n```'


@pytest.mark.asyncio
async def test_llm_service_completar_lista_vacia(mock_settings):
    """Verifica que una lista vacía devuelva una cadena vacía sin errores."""
    service = LLMService(settings=mock_settings)
    mock_client = MagicMock()
    mock_client.ainvoke = AsyncMock(return_value=AIMessage(content=[]))
    service._client = mock_client
    service._provider = "gemini"

    resultado = await service.completar("prompt de prueba")
    assert isinstance(resultado, str)
    assert resultado == ""


@pytest.mark.asyncio
async def test_llm_service_completar_objetos_con_atributo_text(mock_settings):
    """Verifica compatibilidad con respuestas que exponen el atributo .text o respuesta directa."""
    service = LLMService(settings=mock_settings)
    mock_item = MagicMock()
    mock_item.text = "contenido extraído"

    mock_resp = MagicMock()
    mock_resp.content = [mock_item]

    mock_client = MagicMock()
    mock_client.ainvoke = AsyncMock(return_value=mock_resp)
    service._client = mock_client
    service._provider = "gemini"

    resultado = await service.completar("prompt de prueba")
    assert isinstance(resultado, str)
    assert resultado == "contenido extraído"
