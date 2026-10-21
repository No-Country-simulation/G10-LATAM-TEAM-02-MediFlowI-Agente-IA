"""
Nodo: confidence
Responsabilidad: Calcular el score de confianza final del procesamiento multimodal.
Pondera la calidad del texto extraído, legibilidad OCR y completitud de entidades clínicas,
acotando el resultado estrictamente en [0.0, 1.0] e inyectando trazabilidad con umbral HITL de 0.75.
"""

from typing import Any

import structlog

from app.agent.clinical_guardrails import evaluar_red_flags
from app.agent.state import AgentState, DatosExtraidosState

logger = structlog.get_logger(__name__)

UMBRAL_CONFIANZA_HITL: float = 0.75


def calcular_score_confianza(
    score_base: float,
    datos: DatosExtraidosState,
    texto: str,
    error_mensaje: str | None = None,
) -> tuple[float, dict[str, Any]]:
    """
    Calcula de forma pura y granular el score de confianza multimodal y su desglose explicativo.

    Factores positivos:
    - Paciente identificado (+0.10)
    - Diagnóstico principal presente (+0.10)
    - Código CIE-10 identificado (+0.05)
    - Texto suficientemente largo (> 100 caracteres) (+0.05)
    - Hallazgos clínicos clave presentes (+0.05)

    Factores negativos:
    - Texto muy corto (< 20 caracteres) o vacío (-0.30)
    - Error en nodos anteriores (-0.20)
    - Sin diagnóstico principal (-0.15)
    """
    ajuste_texto = 0.0
    ajuste_completitud = 0.0
    penalizaciones = 0.0

    # 1. Calidad de Texto y Extracción
    if len(texto) > 100:
        ajuste_texto += 0.05
    elif len(texto) < 20:
        penalizaciones -= 0.30

    if error_mensaje:
        penalizaciones -= 0.20

    # 2. Completitud Clínica
    if datos.paciente and datos.paciente.nombre:
        ajuste_completitud += 0.10
    if datos.diagnostico_principal:
        ajuste_completitud += 0.10
    else:
        penalizaciones -= 0.10

    if datos.cie10_sugerido:
        ajuste_completitud += 0.05

    if datos.hallazgos_clave:
        ajuste_completitud += 0.05

    ajuste_total = ajuste_texto + ajuste_completitud + penalizaciones
    score_bruto = score_base + ajuste_total
    score_final = max(0.0, min(1.0, round(score_bruto, 3)))

    factores = {
        "score_base": round(score_base, 3),
        "ajuste_texto": round(ajuste_texto, 3),
        "ajuste_completitud": round(ajuste_completitud, 3),
        "penalizaciones": round(penalizaciones, 3),
        "ajuste_total": round(ajuste_total, 3),
        "score_final": score_final,
        "umbral_minimo_requerido": UMBRAL_CONFIANZA_HITL,
        "retenido_por_confianza": score_final < UMBRAL_CONFIANZA_HITL,
    }

    return score_final, factores


async def node_confidence(state: AgentState) -> dict[str, Any]:
    """
    Nodo LangGraph: calcula el score de confianza final y actualiza ClasificacionState y metadata.
    Aplica validación cruzada determinista contra la Matriz de Red Flags Clínicas.
    """
    logger.info("nodo.confidence.inicio", documento_id=state.documento_id)

    score_base = state.clasificacion.score_confianza_clasificacion
    datos = state.datos_extraidos
    texto = state.texto_extraido or state.documento_texto or ""

    score_final, factores = calcular_score_confianza(
        score_base=score_base,
        datos=datos,
        texto=texto,
        error_mensaje=state.error_mensaje,
    )

    metadata_actualizada = dict(state.metadata)

    # ── Validación Cruzada de Coherencia Semántica (Guardrail Red Flags) ─────
    es_rf, red_flag_detectada = evaluar_red_flags(
        hallazgos=datos.hallazgos_clave if datos else None,
        diagnostico=datos.diagnostico_principal if datos else None,
        cie10=datos.cie10_sugerido if datos else None,
        texto_completo=texto,
    )

    prioridad = state.clasificacion.nivel_prioridad
    if es_rf and prioridad == "Rutina":
        # Discordancia crítica: afección de riesgo vital clasificada erróneamente como Rutina
        score_final = 0.0
        factores["score_final"] = 0.0
        factores["retenido_por_confianza"] = True
        factores["discordancia_critica_red_flags"] = True
        factores["red_flag_detectada"] = red_flag_detectada

        metadata_actualizada["discordancia_critica_red_flags"] = True
        metadata_actualizada["red_flag_detectada"] = red_flag_detectada
        metadata_actualizada["motivo_retencion"] = "discordancia_critica_red_flags"

        logger.warning(
            "nodo.confidence.discordancia_red_flag_detectada",
            documento_id=state.documento_id,
            red_flag=red_flag_detectada,
            prioridad=prioridad,
        )

    clasificacion_actualizada = state.clasificacion.model_copy(
        update={"score_confianza_clasificacion": score_final},
    )

    metadata_actualizada["factores_confianza"] = factores

    logger.info(
        "nodo.confidence.completado",
        documento_id=state.documento_id,
        score_base=score_base,
        score_final=score_final,
        retenido_hitl=factores["retenido_por_confianza"],
    )

    return {
        "clasificacion": clasificacion_actualizada,
        "metadata": metadata_actualizada,
        "nodos_ejecutados": state.nodos_ejecutados + ["confidence"],
    }
