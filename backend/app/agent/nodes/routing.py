"""
Nodo: routing
Responsabilidad: Determinar el destino final del documento basado en
clasificación y score de confianza. Genera alertas para urgencias.
"""

import structlog

from app.agent.state import AgentState, DecisionEnrutamientoState

logger = structlog.get_logger(__name__)


async def node_routing(state: AgentState) -> dict:
    """
    Determina el destino del documento y construye la decisión de enrutamiento.
    """
    logger.info("nodo.routing.inicio", documento_id=state.documento_id)

    score = state.clasificacion.score_confianza_clasificacion
    nivel = state.clasificacion.nivel_prioridad

    destino, justificacion, notificacion, requiere_auditoria = _calcular_destino(
        score=score,
        nivel=nivel,
        diagnostico=state.datos_extraidos.diagnostico_principal,
        paciente_nombre=state.datos_extraidos.paciente.nombre
        if state.datos_extraidos.paciente
        else None,
    )

    decision = DecisionEnrutamientoState(
        destino_principal=destino,
        requiere_auditoria_humana=requiere_auditoria,
        justificacion_enrutamiento=justificacion,
        notificacion_generada=notificacion,
    )

    # Determinar status global
    if requiere_auditoria:
        status_final = "pendiente_auditoria"
    else:
        status_final = "procesado"

    logger.info(
        "nodo.routing.completado",
        documento_id=state.documento_id,
        destino=destino,
        requiere_auditoria=requiere_auditoria,
    )

    return {
        "decision_enrutamiento": decision,
        "status": status_final,
        "nodos_ejecutados": state.nodos_ejecutados + ["routing"],
    }


def _calcular_destino(
    score: float,
    nivel: str | None,
    diagnostico: str | None,
    paciente_nombre: str | None,
) -> tuple:
    """
    Lógica de decisión condicional:
    - score < 0.5 → Cola_Auditoria_Humana
    - score ≥ 0.5 + nivel Urgente → Cola_Emergencia_Medica + alerta
    - score ≥ 0.5 + nivel Rutina → Cola_Rutina
    - Ambiguo → Cola_Auditoria_Humana
    """
    if nivel == "Ambiguo":
        return (
            "Cola_Revision_Ambigua",
            "Documento ambiguo. Requiere revisión clínica de ambigüedad.",
            None,
            True,
        )

    if score < 0.5:
        return (
            "Cola_Auditoria_Humana",
            f"Score de confianza bajo ({score:.2f}) o documento ambiguo. Requiere revisión humana.",
            None,
            True,
        )

    if nivel == "Urgente":
        nombre = paciente_nombre or "Paciente desconocido"
        diag = diagnostico or "diagnóstico no especificado"
        notificacion = {
            "canal": "Alerta_Guardia_Medica",
            "mensaje": f"ALERTA URGENTE: {diag} detectado para {nombre}.",
        }
        return (
            "Cola_Emergencia_Medica",
            f"Hallazgo de alta gravedad detectado: {diag}.",
            notificacion,
            False,
        )

    # Rutina por defecto
    return (
        "Cola_Rutina",
        "Documento procesado con alta confianza. Sin hallazgos urgentes.",
        None,
        False,
    )
