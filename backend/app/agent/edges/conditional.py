"""
Aristas condicionales del grafo LangGraph.

Define las funciones que determinan qué nodo ejecutar a continuación
basándose en el estado actual del agente.
"""

from app.agent.state import AgentState


def decidir_post_confidence(state: AgentState) -> str:
    """
    Después del nodo 'confidence', decide si continúa a 'routing'
    o termina en 'auditoria' directamente si hay error crítico.
    """
    if state.error_mensaje and state.clasificacion.score_confianza_clasificacion < 0.3:
        # Error grave: derivar directamente a auditoría sin pasar por routing
        return "forzar_auditoria"
    return "routing"


def decidir_post_routing(state: AgentState) -> str:
    """
    Después del nodo 'routing', determina el nodo terminal:
    - 'fin_emergencia': urgencia detectada
    - 'fin_rutina': procesamiento estándar
    - 'fin_auditoria': requiere revisión humana
    """
    destino = state.decision_enrutamiento.destino_principal

    if destino == "Cola_Emergencia_Medica":
        return "fin_emergencia"
    elif destino == "Cola_Auditoria_Humana":
        return "fin_auditoria"
    else:
        return "fin_rutina"
