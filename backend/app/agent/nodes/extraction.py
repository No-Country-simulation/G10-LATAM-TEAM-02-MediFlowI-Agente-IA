"""
Nodo: extraction
Responsabilidad: Extraer entidades clínicas estructuradas usando LLM (Gemini).
Output: DatosExtraidosState con paciente, médico, diagnóstico, CIE-10, hallazgos.
"""

import json
import structlog
from app.agent.state import AgentState, DatosExtraidosState, PacienteState, MedicoSolicitanteState

logger = structlog.get_logger(__name__)

_EXTRACTION_PROMPT = """
Eres un sistema de extracción de datos clínicos de alta precisión.
Analiza el siguiente documento clínico y extrae ÚNICAMENTE la información presente.
Si un campo no está en el texto, devuelve null para ese campo.

Devuelve SOLO un JSON válido con esta estructura (sin texto adicional):
{{
    "paciente": {{
    "nombre": null,
    "edad": null,
    "id_paciente": null,
    "documento_identidad": null,
    "historia_clinica": null
  }},
  "medico_solicitante": {{
    "nombre": null,
    "matricula": null
  }},
  "estudio_realizado": null,
  "diagnostico_principal": null,
  "cie10_sugerido": null,
  "hallazgos_clave": []
}}

Documento a analizar:
---
{texto}
---
"""


def dividir_texto_en_bloques(texto: str, max_chars: int = 4_000) -> list[str]:
    """Divide texto largo sin descartar ningún carácter del documento."""
    if max_chars <= 0:
        raise ValueError("max_chars debe ser mayor que cero")
    return [texto[indice:indice + max_chars] for indice in range(0, len(texto), max_chars)]


async def node_extraction(state: AgentState, llm_service=None) -> dict:
    """
    Extrae entidades clínicas del texto usando el LLM.
    llm_service se inyecta desde el grafo al compilarlo.
    """
    logger.info("nodo.extraction.inicio", documento_id=state.documento_id)

    texto = state.texto_extraido or state.documento_texto or ""

    if not texto.strip():
        logger.warning("nodo.extraction.sin_texto", documento_id=state.documento_id)
        return {
            "datos_extraidos": DatosExtraidosState(),
            "nodos_ejecutados": state.nodos_ejecutados + ["extraction"],
        }

    try:
        bloques = dividir_texto_en_bloques(texto)
        datos = DatosExtraidosState()
        for bloque in bloques:
            prompt = _EXTRACTION_PROMPT.format(texto=bloque)
            datos_bloque = _parsear_respuesta(await _llamar_llm(prompt, llm_service))
            datos = _consolidar_datos(datos, datos_bloque)

        logger.info(
            "nodo.extraction.completado",
            documento_id=state.documento_id,
            diagnostico=datos.diagnostico_principal,
        )

        return {
            "datos_extraidos": datos,
            "nodos_ejecutados": state.nodos_ejecutados + ["extraction"],
        }

    except Exception as exc:
        logger.error("nodo.extraction.error", documento_id=state.documento_id, error=str(exc))
        return {
            "datos_extraidos": DatosExtraidosState(),
            "error_mensaje": f"Error en extraction: {exc}",
            "nodos_ejecutados": state.nodos_ejecutados + ["extraction"],
        }


def _consolidar_datos(
    acumulado: DatosExtraidosState,
    nuevo: DatosExtraidosState,
) -> DatosExtraidosState:
    """Conserva el primer valor clínico encontrado y combina los hallazgos."""
    return DatosExtraidosState(
        paciente=acumulado.paciente or nuevo.paciente,
        medico_solicitante=acumulado.medico_solicitante or nuevo.medico_solicitante,
        estudio_realizado=acumulado.estudio_realizado or nuevo.estudio_realizado,
        diagnostico_principal=acumulado.diagnostico_principal or nuevo.diagnostico_principal,
        cie10_sugerido=acumulado.cie10_sugerido or nuevo.cie10_sugerido,
        hallazgos_clave=list(dict.fromkeys(acumulado.hallazgos_clave + nuevo.hallazgos_clave)),
    )


async def _llamar_llm(prompt: str, llm_service) -> str:
    """Llama al LLM y retorna el texto de la respuesta."""
    if llm_service is not None:
        return await llm_service.completar(prompt)
    from app.services.llm_service import LLMService
    from app.core.config import get_settings
    return LLMService(get_settings())._respuesta_mock(prompt)


def _parsear_respuesta(raw: str) -> DatosExtraidosState:
    """Parsea el JSON devuelto por el LLM al modelo Pydantic."""
    # Limpiar posible markdown wrapper ```json ... ```
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw)

    paciente_data = data.get("paciente") or {}
    medico_data = data.get("medico_solicitante") or {}

    return DatosExtraidosState(
        paciente=PacienteState(**paciente_data) if paciente_data else None,
        medico_solicitante=MedicoSolicitanteState(**medico_data) if medico_data else None,
        estudio_realizado=data.get("estudio_realizado"),
        diagnostico_principal=data.get("diagnostico_principal"),
        cie10_sugerido=data.get("cie10_sugerido"),
        hallazgos_clave=data.get("hallazgos_clave") or [],
    )
