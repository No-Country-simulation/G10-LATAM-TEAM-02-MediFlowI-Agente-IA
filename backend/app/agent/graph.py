"""
MediFlow — Grafo de Decisión LangGraph.

Define y compila el grafo del agente autónomo de triaje clínico.
Estructura:
    START → ingestion → extraction → classification → confidence
          → [conditional] → routing → END

NOTA: Este archivo es MANUAL. No está en _generated/.
El grafo refleja el flujo definido en ARQUITECTURA-SDD.md.
"""

import functools
import time
from typing import Any

import structlog
from langgraph.graph import END, StateGraph

from app.agent.edges.conditional import decidir_post_confidence
from app.agent.nodes.classification import node_classification
from app.agent.nodes.confidence import node_confidence
from app.agent.nodes.extraction import node_extraction
from app.agent.nodes.ingestion import node_ingestion
from app.agent.nodes.routing import node_routing
from app.agent.state import AgentState

logger = structlog.get_logger(__name__)


def _wrap_with_llm(node_fn, llm_service):
    """Wrappea nodos que requieren llm_service via functools.partial."""

    @functools.wraps(node_fn)
    async def wrapper(state: AgentState) -> dict:
        return await node_fn(state, llm_service=llm_service)

    return wrapper


def build_graph(llm_service=None) -> Any:
    """
    Construye y compila el grafo LangGraph de MediFlow.

    Args:
        llm_service: Instancia obligatoria para los nodos clínicos con IA.

    Returns:
        Grafo compilado listo para invocar.
    """
    graph = StateGraph(AgentState)

    # ── Registrar nodos ──────────────────────────────────────────────────────
    graph.add_node("ingestion", node_ingestion)
    graph.add_node("extraction", _wrap_with_llm(node_extraction, llm_service))
    graph.add_node("classification", _wrap_with_llm(node_classification, llm_service))
    graph.add_node("confidence", node_confidence)
    graph.add_node("routing", node_routing)

    # Nodo terminal para auditoría forzada (error crítico)
    async def nodo_forzar_auditoria(state: AgentState) -> dict:
        from app.agent.state import DecisionEnrutamientoState

        return {
            "decision_enrutamiento": DecisionEnrutamientoState(
                destino_principal="Cola_Auditoria_Humana",
                requiere_auditoria_humana=True,
                justificacion_enrutamiento="Error crítico en procesamiento. Derivado a auditoría.",
            ),
            "status": "pendiente_auditoria",
        }

    graph.add_node("forzar_auditoria", nodo_forzar_auditoria)

    # ── Definir flujo (edges) ────────────────────────────────────────────────
    graph.set_entry_point("ingestion")
    graph.add_edge("ingestion", "extraction")
    graph.add_edge("extraction", "classification")
    graph.add_edge("classification", "confidence")

    # Edge condicional después de confidence
    graph.add_conditional_edges(
        "confidence",
        decidir_post_confidence,
        {
            "routing": "routing",
            "forzar_auditoria": "forzar_auditoria",
        },
    )

    graph.add_edge("routing", END)
    graph.add_edge("forzar_auditoria", END)

    return graph.compile()


async def ejecutar_triage(
    documento_id: str,
    tipo_archivo: str,
    documento_texto: str | None = None,
    documento_base64: str | None = None,
    canal_origen: str = "",
    metadata: dict | None = None,
    llm_service=None,
) -> AgentState:
    """
    Punto de entrada principal para ejecutar el agente de triaje.

    Args:
        documento_id: ID único del documento
        tipo_archivo: PDF | IMAGEN | TEXTO | JSON
        documento_texto: Texto plano del documento (opcional)
        documento_base64: Contenido en base64 (PDF/imagen)
        canal_origen: Sistema de origen
        metadata: Metadatos adicionales
        llm_service: Servicio LLM inyectado

    Returns:
        AgentState con todos los resultados del grafo
    """
    inicio = time.time()

    estado_inicial = AgentState(
        documento_id=documento_id,
        tipo_archivo=tipo_archivo,
        documento_texto=documento_texto,
        documento_base64=documento_base64,
        canal_origen=canal_origen,
        metadata=metadata or {},
    )

    graph = build_graph(llm_service=llm_service)

    logger.info("agente.triage.inicio", documento_id=documento_id)

    resultado_raw: dict[str, Any] = await graph.ainvoke(estado_inicial.model_dump())
    resultado = AgentState(**resultado_raw)

    tiempo_ms = int((time.time() - inicio) * 1000)
    resultado.tiempo_procesamiento_ms = tiempo_ms

    logger.info(
        "agente.triage.completado",
        documento_id=documento_id,
        status=resultado.status,
        destino=resultado.decision_enrutamiento.destino_principal,
        score=resultado.clasificacion.score_confianza_clasificacion,
        tiempo_ms=tiempo_ms,
    )

    return resultado
