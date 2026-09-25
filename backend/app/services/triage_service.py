"""
MediFlow — Servicio de Triaje.

Orquesta la ejecución del agente LangGraph y persiste los resultados
en OCI Object Storage.
"""

import json
import structlog
from app.agent.graph import ejecutar_triage
from app.agent.state import AgentState
from app.core.config import Settings

logger = structlog.get_logger(__name__)


class TriageService:
    """
    Servicio principal de triaje clínico.
    Coordina: agente LangGraph + persistencia OCI.
    """

    def __init__(self, settings: Settings, llm_service=None, oci_storage=None):
        self._settings = settings
        self._llm_service = llm_service
        self._oci_storage = oci_storage

    async def procesar_documento(
        self,
        documento_id: str,
        tipo_archivo: str,
        documento_texto: str | None = None,
        documento_base64: str | None = None,
        canal_origen: str = "",
        metadata: dict | None = None,
    ) -> AgentState:
        """
        Procesa un documento clínico completo:
        1. Ejecuta el agente LangGraph
        2. Persiste en OCI Object Storage
        3. Retorna el estado final

        Args:
            documento_id: ID único del documento
            tipo_archivo: PDF | IMAGEN | TEXTO | JSON
            documento_texto: Texto del documento
            documento_base64: Contenido en base64
            canal_origen: Canal de origen del documento
            metadata: Metadatos adicionales

        Returns:
            AgentState con resultado completo del triaje
        """
        logger.info("triage_service.inicio", documento_id=documento_id)

        # 1. Ejecutar agente
        resultado = await ejecutar_triage(
            documento_id=documento_id,
            tipo_archivo=tipo_archivo,
            documento_texto=documento_texto,
            documento_base64=documento_base64,
            canal_origen=canal_origen,
            metadata=metadata,
            llm_service=self._llm_service,
        )

        # 2. Persistir en OCI Object Storage
        if self._oci_storage:
            try:
                ruta = self._calcular_ruta_oci(resultado)
                await self._oci_storage.guardar_documento(
                    objeto_key=ruta,
                    contenido=resultado.model_dump_json(indent=2),
                    content_type="application/json",
                )
                resultado.almacenamiento_oci.bucket = self._settings.oci_bucket_name
                resultado.almacenamiento_oci.ruta_objeto = ruta
                resultado.almacenamiento_oci.status_backup = "exito"
                logger.info("triage_service.oci.guardado", ruta=ruta)
            except Exception as exc:
                logger.error("triage_service.oci.error", error=str(exc))
                resultado.almacenamiento_oci.status_backup = "error"

        logger.info(
            "triage_service.completado",
            documento_id=documento_id,
            destino=resultado.decision_enrutamiento.destino_principal,
        )
        return resultado

    def _calcular_ruta_oci(self, resultado: AgentState) -> str:
        """Determina la ruta del objeto en OCI según el destino."""
        destino = resultado.decision_enrutamiento.destino_principal
        doc_id = resultado.documento_id

        rutas = {
            "Cola_Emergencia_Medica": f"procesados/urgentes/{doc_id}.json",
            "Cola_Rutina": f"procesados/rutina/{doc_id}.json",
            "Cola_Auditoria_Humana": f"auditoria_humana/{doc_id}.json",
        }
        return rutas.get(destino, f"procesados/otros/{doc_id}.json")
