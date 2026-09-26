"""
Nodo: classification
Responsabilidad: Clasificar el tipo de documento y nivel de prioridad usando LLM.
Output: ClasificacionState con tipo_documento, especialidad, nivel_prioridad.
"""

import json

import structlog

from app.agent.clinical_catalog import CATALOGO_PARA_PROMPT, normalizar_tipo_documento
from app.agent.nodes.extraction import dividir_texto_en_bloques
from app.agent.state import AgentState, ClasificacionState

logger = structlog.get_logger(__name__)

_CLASSIFICATION_PROMPT = """
Eres un sistema experto en clasificación de documentos clínicos hospitalarios.
Analiza el siguiente texto extraído de un documento clínico.

Devuelve SOLO un JSON válido con esta estructura (sin texto adicional):
{{
  "tipo_documento": "{catalogo}",
  "especialidad": "especialidad médica o null",
  "nivel_prioridad": "Urgente | Rutina | Ambiguo",
  "razon_prioridad": "breve justificación de la prioridad asignada"
}}

Criterios de prioridad:
- "Urgente": hallazgos críticos, emergencias, diagnósticos de alto riesgo vital
- "Rutina": resultados normales, consultas de seguimiento, controles
- "Ambiguo": texto ilegible, información insuficiente, contradictoria o incierta

Texto del documento:
---
{texto}
---

Datos ya extraídos:
- Diagnóstico principal: {diagnostico}
- Hallazgos clave: {hallazgos}
"""


def consolidar_clasificaciones(bloques: list[ClasificacionState]) -> ClasificacionState:
    """Da prioridad clínica a urgencias y deriva inconsistencias a Ambiguo."""
    if not bloques:
        return ClasificacionState(tipo_documento="Desconocido", nivel_prioridad="Ambiguo")

    urgentes = [bloque for bloque in bloques if bloque.nivel_prioridad == "Urgente"]
    if urgentes:
        return urgentes[0]

    prioridades = {bloque.nivel_prioridad for bloque in bloques}
    if "Ambiguo" in prioridades or len(prioridades) > 1:
        return next(
            (bloque for bloque in bloques if bloque.nivel_prioridad == "Ambiguo"),
            ClasificacionState(tipo_documento="Desconocido", nivel_prioridad="Ambiguo"),
        )

    return bloques[0]


async def node_classification(state: AgentState, llm_service=None) -> dict:
    """Clasifica el documento y determina nivel de prioridad."""
    logger.info("nodo.classification.inicio", documento_id=state.documento_id)

    texto = state.texto_extraido or state.documento_texto or ""
    diagnostico = state.datos_extraidos.diagnostico_principal or "No determinado"
    hallazgos = ", ".join(state.datos_extraidos.hallazgos_clave) or "Ninguno"

    if not texto.strip():
        clasificacion = ClasificacionState(
            tipo_documento="Desconocido",
            nivel_prioridad="Ambiguo",
            score_confianza_clasificacion=0.0,
        )
        return {
            "clasificacion": clasificacion,
            "nodos_ejecutados": state.nodos_ejecutados + ["classification"],
        }

    try:
        clasificaciones = []
        for bloque in dividir_texto_en_bloques(texto):
            prompt = _CLASSIFICATION_PROMPT.format(
                texto=bloque,
                diagnostico=diagnostico,
                hallazgos=hallazgos,
                catalogo=CATALOGO_PARA_PROMPT,
            )
            clasificaciones.append(_parsear_respuesta(await _llamar_llm(prompt, llm_service)))
        clasificacion = consolidar_clasificaciones(clasificaciones)

        logger.info(
            "nodo.classification.completado",
            documento_id=state.documento_id,
            prioridad=clasificacion.nivel_prioridad,
        )

        return {
            "clasificacion": clasificacion,
            "nodos_ejecutados": state.nodos_ejecutados + ["classification"],
        }

    except Exception as exc:
        logger.error("nodo.classification.error", documento_id=state.documento_id, error=str(exc))
        return {
            "clasificacion": ClasificacionState(
                tipo_documento="Error",
                nivel_prioridad="Ambiguo",
                score_confianza_clasificacion=0.0,
            ),
            "error_mensaje": f"Error en classification: {exc}",
            "nodos_ejecutados": state.nodos_ejecutados + ["classification"],
        }


async def _llamar_llm(prompt: str, llm_service) -> str:
    if llm_service is None:
        from app.services.llm_service import LLMUnavailableError

        raise LLMUnavailableError("El nodo de clasificación requiere un servicio LLM.")
    return await llm_service.completar(prompt)


def _parsear_respuesta(raw: str) -> ClasificacionState:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    data = json.loads(raw)
    nivel = data.get("nivel_prioridad", "Ambiguo")

    # Score de confianza inicial basado en la solidez de la clasificación
    score_base = {"Urgente": 0.85, "Rutina": 0.80, "Ambiguo": 0.30}.get(nivel, 0.5)

    return ClasificacionState(
        tipo_documento=normalizar_tipo_documento(data.get("tipo_documento")),
        especialidad=data.get("especialidad"),
        nivel_prioridad=nivel,
        score_confianza_clasificacion=score_base,
    )
