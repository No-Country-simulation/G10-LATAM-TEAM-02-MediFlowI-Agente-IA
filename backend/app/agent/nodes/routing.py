"""
Nodo: routing
Responsabilidad: Determinar el destino final del documento basado en
clasificación y score de confianza. Genera alertas para urgencias.
"""

import structlog

from app.agent.clinical_catalog import es_medicamento_controlado, normalizar_tipo_documento
from app.agent.clinical_guardrails import es_documento_fuera_de_dominio
from app.agent.state import AgentState, DecisionEnrutamientoState
from app.core.alerts import MENSAJE_GUARDIA

logger = structlog.get_logger(__name__)


async def node_routing(state: AgentState) -> dict:
    """
    Determina el destino del documento y construye la decisión de enrutamiento.
    """
    logger.info("nodo.routing.inicio", documento_id=state.documento_id)

    score = state.clasificacion.score_confianza_clasificacion
    nivel = state.clasificacion.nivel_prioridad
    discrepancia_identidad = bool(state.metadata.get("discrepancia_identidad_detectada", False))

    tipo_doc = state.clasificacion.tipo_documento or state.clasificacion.categoria_documento
    meds_controlados = bool(state.metadata.get("medicamentos_controlados", False))

    tiene_medicamentos = False
    if state.datos_extraidos and state.datos_extraidos.medicamentos:
        tiene_medicamentos = len(state.datos_extraidos.medicamentos) > 0
        if not meds_controlados:
            for med in state.datos_extraidos.medicamentos:
                if es_medicamento_controlado(med.medicamento):
                    meds_controlados = True
                    break

    destino, justificacion, notificacion, requiere_auditoria = _calcular_destino(
        score=score,
        nivel=nivel,
        diagnostico=state.datos_extraidos.diagnostico_principal if state.datos_extraidos else None,
        paciente_nombre=state.datos_extraidos.paciente.nombre
        if state.datos_extraidos and state.datos_extraidos.paciente
        else None,
        tipo_documento=tipo_doc,
        medicamentos_controlados=meds_controlados,
        discrepancia_identidad=discrepancia_identidad,
        tiene_medicamentos=tiene_medicamentos,
    )

    new_metadata = dict(state.metadata)
    motivo_retencion: str | None = None

    if tipo_doc and es_documento_fuera_de_dominio(tipo_doc):
        new_metadata["fuera_de_dominio_clinico"] = True
        new_metadata["motivo_retencion"] = "fuera_de_dominio_clinico"
        motivo_retencion = "fuera_de_dominio_clinico"
    elif discrepancia_identidad:
        motivo_retencion = "discrepancia_identidad"
    elif state.metadata.get("cie10_codigos_invalidos"):
        destino = "Cola_Auditoria_Humana"
        justificacion = (
            "Código CIE-10 sugerido inexistente o mal formado. Requiere revisión humana."
        )
        notificacion = None
        requiere_auditoria = True
        motivo_retencion = "cie10_invalido"
    elif state.metadata.get("discordancia_critica_red_flags"):
        destino = "Cola_Revision_Ambigua"
        rf_nombre = state.metadata.get("red_flag_detectada", "Red Flag")
        justificacion = (
            f"Discordancia crítica detectada: Hallazgo de riesgo vital ({rf_nombre}) "
            "clasificado como Rutina. Requiere auditoría médica urgente."
        )
        notificacion = None
        requiere_auditoria = True
        motivo_retencion = "discordancia_critica_red_flags"
        new_metadata["motivo_retencion"] = "discordancia_critica_red_flags"
    elif score < 0.75:
        motivo_retencion = "baja_confianza"

    decision = DecisionEnrutamientoState(
        destino_principal=destino,
        requiere_auditoria_humana=requiere_auditoria,
        justificacion_enrutamiento=justificacion,
        notificacion_generada=notificacion,
        motivo_retencion=motivo_retencion,
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
        "metadata": new_metadata,
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
    tiene_medicamentos: bool = False,
) -> tuple:
    """
    Lógica de decisión condicional:
    - fuera_de_dominio → Cola_Revision_Ambigua + requiere_auditoria=True (US1)
    - discrepancia_identidad → Cola_Revision_Ambigua + requiere_auditoria=True (Issue #29)
    - Ambiguo → Cola_Revision_Ambigua + requiere_auditoria=True
    - nivel Urgente → Cola_Emergencia_Medica + alerta (Precedencia clínica absoluta)
    - score < 0.75 → Cola_Auditoria_Humana + requiere_auditoria=True (Issue #31)
    - Receta_Medica / prescripciones / farmacoterapia → Farmacia_Hospitalaria (Issue #28 / R3)
    - Rutina → Cola_Rutina
    """
    if tipo_documento and es_documento_fuera_de_dominio(tipo_documento):
        return (
            "Cola_Revision_Ambigua",
            f"Documento fuera de dominio clínico ({tipo_documento}). Requiere revisión y clasificación manual.",
            None,
            True,
        )

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

    if nivel == "Urgente":
        diag = diagnostico or "diagnóstico no especificado"
        notificacion = {
            "canal": "Alerta_Guardia_Medica",
            "mensaje": MENSAJE_GUARDIA,
        }
        return (
            "Cola_Emergencia_Medica",
            f"Hallazgo de alta gravedad detectado: {diag}.",
            notificacion,
            False,
        )

    if score < 0.75:
        return (
            "Cola_Auditoria_Humana",
            f"Score de confianza bajo ({score:.2f} < 0.75). Requiere revisión del Coordinador Médico.",
            None,
            True,
        )

    # Evaluación Farmacia
    diag_lower = (diagnostico or "").lower()
    es_farmacia = (
        normalizar_tipo_documento(tipo_documento) == "Receta Médica"
        or tiene_medicamentos
        or ("farmacoterapia" in diag_lower and "descompensación aguda" not in diag_lower)
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
