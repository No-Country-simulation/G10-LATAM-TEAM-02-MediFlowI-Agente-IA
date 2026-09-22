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
    "id_paciente": null
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
        prompt = _EXTRACTION_PROMPT.format(texto=texto[:4000])  # límite de contexto
        respuesta_raw = await _llamar_llm(prompt, llm_service)
        datos = _parsear_respuesta(respuesta_raw)

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


async def _llamar_llm(prompt: str, llm_service) -> str:
    """Llama al LLM y retorna el texto de la respuesta."""
    if llm_service is None:
        # Mock para tests sin credenciales
        return json.dumps({
            "paciente": {"nombre": "Paciente Mock", "edad": 40, "id_paciente": None},
            "medico_solicitante": {"nombre": None, "matricula": None},
            "estudio_realizado": None,
            "diagnostico_principal": None,
            "cie10_sugerido": None,
            "hallazgos_clave": [],
        })
    return await llm_service.completar(prompt)


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
