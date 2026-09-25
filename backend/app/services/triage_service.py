"""
MediFlow — Servicio de Triaje.

Orquesta la ejecución del agente LangGraph y persiste los resultados
en OCI Object Storage y la base de datos PostgreSQL (documentos_triaje).
"""

import json
import structlog
from app.agent.graph import ejecutar_triage
from app.agent.state import AgentState
from app.core.config import Settings
from app.repositories.postgres_storage import PostgresStorageRepository

logger = structlog.get_logger(__name__)


class TriageService:
    """
    Servicio principal de triaje clínico.
    Coordina: agente LangGraph + persistencia PostgreSQL + OCI/Disco Local.
    """

    def __init__(self, settings: Settings, llm_service=None, oci_storage=None, postgres_storage=None):
        from app.repositories.oci_storage import OCIStorageRepository
        self._settings = settings
        self._llm_service = llm_service
        self._oci_storage = oci_storage or OCIStorageRepository(settings)
        self._postgres_storage = postgres_storage or PostgresStorageRepository(settings)

    async def procesar_documento(
        self,
        documento_id: str,
        tipo_archivo: str,
        documento_texto: str | None = None,
        documento_base64: str | None = None,
        canal_origen: str = "",
        metadata: dict | None = None,
        nombre_original: str | None = None,
        usuario_registro_id: str | None = None,
    ) -> AgentState:
        """
        Procesa un documento clínico completo:
        1. Ejecuta el agente LangGraph
        2. Persiste el archivo original en recibidos/<documento_id>/original.<ext>
        3. Persiste el resultado JSON en <estado>/<documento_id>/resultado.json
        4. Persiste los metadatos y resultado en PostgreSQL (documentos_triaje)
        5. Retorna el estado final
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

        ext = "pdf" if tipo_archivo == "PDF" else ("png" if tipo_archivo == "IMAGEN" else "txt")
        nombre_orig = nombre_original or f"ingesta_{documento_id}.{ext}"

        # 2. Persistir en OCI Object Storage / Disco Local
        if self._oci_storage:
            try:
                # A. Guardar archivo original (recibidos/<documento_id>/original.<ext>)
                ruta_orig = f"recibidos/{documento_id}/original.{ext}"
                if documento_base64:
                    import base64
                    contenido_bytes = base64.b64decode(documento_base64)
                    mime = "application/pdf" if tipo_archivo == "PDF" else "image/png"
                    await self._oci_storage.guardar_documento(
                        objeto_key=ruta_orig,
                        contenido=contenido_bytes,
                        content_type=mime,
                    )
                elif documento_texto:
                    await self._oci_storage.guardar_documento(
                        objeto_key=ruta_orig,
                        contenido=documento_texto,
                        content_type="text/plain",
                    )

                # B. Guardar resultado JSON (<estado>/<documento_id>/resultado.json)
                ruta_res = self._calcular_ruta_oci(resultado)
                await self._oci_storage.guardar_documento(
                    objeto_key=ruta_res,
                    contenido=resultado.model_dump_json(indent=2),
                    content_type="application/json",
                )

                resultado.almacenamiento_oci.bucket = self._settings.oci_bucket_name
                resultado.almacenamiento_oci.ruta_objeto = ruta_res
                resultado.almacenamiento_oci.archivo_original = ruta_orig
                resultado.almacenamiento_oci.resultado_json = ruta_res
                resultado.almacenamiento_oci.nombre_original = nombre_orig
                resultado.almacenamiento_oci.status_backup = "exito"
                logger.info("triage_service.oci.guardado", original=ruta_orig, resultado=ruta_res)
            except Exception as exc:
                logger.error("triage_service.oci.error", error=str(exc))
                resultado.almacenamiento_oci.status_backup = "error"

        # 3. Persistir en la base de datos PostgreSQL (documentos_triaje)
        if self._postgres_storage:
            try:
                await self._postgres_storage.guardar_resultado(resultado, usuario_registro_id)
                logger.info("triage_service.postgres.guardado", documento_id=documento_id)
            except Exception as exc:
                logger.error("triage_service.postgres.error", documento_id=documento_id, error=str(exc))

        logger.info(
            "triage_service.completado",
            documento_id=documento_id,
            destino=resultado.decision_enrutamiento.destino_principal,
        )
        return resultado

    def _calcular_ruta_oci(self, resultado: AgentState) -> str:
        """Determina la ruta del resultado JSON en OCI según el estado/destino."""
        destino = resultado.decision_enrutamiento.destino_principal
        doc_id = resultado.documento_id

        rutas = {
            "Cola_Emergencia_Medica": f"urgentes/{doc_id}/resultado.json",
            "Cola_Rutina": f"procesados/{doc_id}/resultado.json",
            "Cola_Auditoria_Humana": f"auditoria_humana/{doc_id}/resultado.json",
        }
        return rutas.get(destino, f"procesados/{doc_id}/resultado.json")

