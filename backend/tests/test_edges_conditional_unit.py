"""Pruebas unitarias de las aristas condicionales del grafo LangGraph (US-14).

Cubren la lógica de ruteo entre nodos: decisión tras 'confidence' (continuar a
routing o forzar auditoría) y decisión tras 'routing' (nodo terminal según el
destino de enrutamiento).
"""

import pytest

from app.agent.edges.conditional import decidir_post_confidence, decidir_post_routing
from app.agent.state import AgentState


def _estado() -> AgentState:
    return AgentState(documento_id="DOC-EDGE", tipo_archivo="TEXTO", canal_origen="Admision")


def test_post_confidence_error_grave_y_baja_confianza_fuerza_auditoria():
    state = _estado()
    state.error_mensaje = "Fallo crítico de extracción"
    state.clasificacion.score_confianza_clasificacion = 0.1
    assert decidir_post_confidence(state) == "forzar_auditoria"


def test_post_confidence_sin_error_continua_a_routing():
    state = _estado()
    state.error_mensaje = ""
    state.clasificacion.score_confianza_clasificacion = 0.95
    assert decidir_post_confidence(state) == "routing"


def test_post_confidence_error_con_confianza_alta_continua_a_routing():
    state = _estado()
    state.error_mensaje = "Advertencia no bloqueante"
    state.clasificacion.score_confianza_clasificacion = 0.8
    assert decidir_post_confidence(state) == "routing"


@pytest.mark.parametrize(
    "destino, nodo_terminal",
    [
        ("Cola_Emergencia_Medica", "fin_emergencia"),
        ("Cola_Auditoria_Humana", "fin_auditoria"),
        ("Cola_Revision_Ambigua", "fin_auditoria"),
        ("Cola_Rutina", "fin_rutina"),
        ("Farmacia_Hospitalaria", "fin_rutina"),
    ],
)
def test_post_routing_mapea_destino_a_nodo_terminal(destino, nodo_terminal):
    state = _estado()
    state.decision_enrutamiento.destino_principal = destino
    assert decidir_post_routing(state) == nodo_terminal
