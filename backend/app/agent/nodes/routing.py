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
    discrepancia_identidad = bool(
        state.metadata.get("discrepancia_identidad_detectada", False)
    )

    tipo_doc = state.clasificacion.categoria_documento if state.clasificacion else None
    
    meds_controlados = state.metadata.get("medicamentos_controlados", False) if state.metadata else False
    discrepancia = state.metadata.get("discrepancia_identidad_detectada", False) if state.metadata else False

    destino, justificacion, notificacion, requiere_auditoria = _calcular_destino(
        score=score,
        nivel=nivel,
        diagnostico=state.datos_extraidos.diagnostico_principal if state.datos_extraidos else None,
        paciente_nombre=state.datos_extraidos.paciente.nombre
        if state.datos_extraidos and state.datos_extraidos.paciente
        else None,
        tipo_documento=tipo_doc,
        medicamentos_controlados=meds_controlados,
        discrepancia_identidad=discrepancia
    )

    if state.metadata.get("cie10_codigos_invalidos"):
        destino = "Cola_Auditoria_Humana"
        justificacion = (
            "Código CIE-10 sugerido inexistente o mal formado. Requiere revisión humana."
        )
        notificacion = None
        requiere_auditoria = True

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
    tipo_documento: str | None = None,
    medicamentos_controlados: bool = False,
    discrepancia_identidad: bool = False,
) -> tuple:
    """
    Lógica de decisión condicional:
    - discrepancia_identidad → Cola_Revision_Ambigua + requiere_auditoria=True
    - score < 0.5 → Cola_Auditoria_Humana
    - score ≥ 0.5 + nivel Urgente → Cola_Emergencia_Medica + alerta
    - score ≥ 0.5 + nivel Rutina → Cola_Rutina
    - Ambiguo → Cola_Revision_Ambigua
    """
    if discrepancia_identidad:
        return (
            "Cola_Revision_Ambigua",
            "Discrepancia de identidad detectada. Requiere revisión de admisión.",
            None,
            True,
        )

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

    # Evaluación Farmacia
    diag_lower = (diagnostico or "").lower()
    es_farmacia = (
        tipo_documento == "Receta_Medica" or
        ("farmacoterapia" in diag_lower and "descompensación aguda" not in diag_lower)
    )

    if es_farmacia:
        if medicamentos_controlados:
            return (
                "Farmacia_Hospitalaria",
                "Receta o farmacoterapia con medicamentos controlados/narcóticos. Requiere revisión estricta de Farmacia/Auditor.",
                None,
                True,
            )
        else:
            return (
                "Farmacia_Hospitalaria",
                "Receta o farmacoterapia exclusiva procesada con éxito. Derivada a Farmacia_Hospitalaria.",
                None,
                False,
            )

    # Rutina por defecto
    return (
        "Cola_Rutina",
        "Documento procesado con alta confianza. Sin hallazgos urgentes.",
        None,
        False,
    )

