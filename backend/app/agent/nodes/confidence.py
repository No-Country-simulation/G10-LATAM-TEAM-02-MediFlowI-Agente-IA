"""
Nodo: confidence
Responsabilidad: Calcular el score de confianza final del procesamiento.
Combina señales de extracción + clasificación para producir un score 0.0-1.0.
"""

import structlog

from app.agent.state import AgentState, ClasificacionState

logger = structlog.get_logger(__name__)


async def node_confidence(state: AgentState) -> dict:
    """
    Calcula el score de confianza final y lo ajusta en la clasificación.

    Factores que aumentan confianza:
    - Paciente identificado (+0.10)
    - Diagnóstico extraído (+0.10)
    - CIE-10 encontrado (+0.05)
    - Texto suficientemente largo (+0.05)
    - Hallazgos clave presentes (+0.05)

    Factores que reducen confianza:
    - Texto muy corto o vacío (-0.30)
    - Error en nodo anterior (-0.20)
    - Sin diagnóstico (-0.10)
    """
    logger.info("nodo.confidence.inicio", documento_id=state.documento_id)

    score_base = state.clasificacion.score_confianza_clasificacion
    ajuste = 0.0

    datos = state.datos_extraidos
    texto = state.texto_extraido or state.documento_texto or ""

    # Factores positivos
    if datos.paciente and datos.paciente.nombre:
        ajuste += 0.10
    if datos.diagnostico_principal:
        ajuste += 0.10
    if datos.cie10_sugerido:
        ajuste += 0.05
    if len(texto) > 100:
        ajuste += 0.05
    if datos.hallazgos_clave:
        ajuste += 0.05

    # Factores negativos
    if len(texto) < 20:
        ajuste -= 0.30
    if state.error_mensaje:
        ajuste -= 0.20
    if not datos.diagnostico_principal:
        ajuste -= 0.10

    score_final = max(0.0, min(1.0, score_base + ajuste))

    # Actualizar clasificación con score ajustado
    clasificacion_actualizada = ClasificacionState(
        tipo_documento=state.clasificacion.tipo_documento,
        especialidad=state.clasificacion.especialidad,
        nivel_prioridad=state.clasificacion.nivel_prioridad,
        score_confianza_clasificacion=round(score_final, 3),
    )

    logger.info(
        "nodo.confidence.completado",
        documento_id=state.documento_id,
        score_base=score_base,
        ajuste=ajuste,
        score_final=score_final,
    )

    return {
        "clasificacion": clasificacion_actualizada,
        "nodos_ejecutados": state.nodos_ejecutados + ["confidence"],
    }
