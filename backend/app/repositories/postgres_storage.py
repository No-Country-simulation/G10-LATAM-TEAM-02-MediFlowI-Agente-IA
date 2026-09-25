"""
MediFlow — Repositorio PostgreSQL (para desarrollo y pruebas locales).

Alternativa al OCI Object Storage para entornos locales.
En producción, usar OCIStorageRepository.

Uso:
    Configurar DATABASE_URL en .env:
    DATABASE_URL=postgresql+asyncpg://mediflow:mediflow_dev_pass@localhost:5432/mediflow_dev
"""

import json
import structlog
from typing import Optional
from app.agent.state import AgentState
from app.core.config import Settings

logger = structlog.get_logger(__name__)


class PostgresStorageRepository:
    """
    Repositorio PostgreSQL para almacenamiento local de resultados de triaje.
    Usa asyncpg para operaciones asíncronas.

    En modo dev (sin DB configurada), opera en memoria como el OCI mock.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._pool = None
        self._mock_store: dict[str, dict] = {}
        self._initialized = False

    async def inicializar(self):
        """Inicializa el pool de conexiones asyncpg."""
        if self._initialized:
            return

        db_url = getattr(self._settings, "database_url", None)
        if not db_url:
            logger.warning("postgres.modo_mock", razon="DATABASE_URL no configurada")
            self._initialized = True
            return

        try:
            import asyncpg
            # Convertir URL SQLAlchemy a asyncpg format
            url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            self._pool = await asyncpg.create_pool(url, min_size=2, max_size=10)
            self._initialized = True
            logger.info("postgres.inicializado", url=url.split("@")[-1])
        except ImportError:
            logger.warning("asyncpg.no_instalado", fallback="mock")
            self._initialized = True
        except Exception as exc:
            logger.error("postgres.conexion.error", error=str(exc))
            self._initialized = True

    async def guardar_resultado(self, resultado: AgentState) -> bool:
        """
        Guarda el resultado completo de triaje en PostgreSQL.

        Args:
            resultado: Estado final del agente LangGraph

        Returns:
            True si se guardó correctamente
        """
        await self.inicializar()

        datos = resultado.model_dump()

        if self._pool is None:
            # Mock en memoria
            self._mock_store[resultado.documento_id] = datos
            logger.info("postgres.mock.guardado", documento_id=resultado.documento_id)
            return True

        try:
            async with self._pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO documentos_triaje (
                        documento_id, tipo_archivo, canal_origen, status,
                        texto_extraido,
                        tipo_documento, especialidad, nivel_prioridad, score_confianza,
                        paciente_nombre, paciente_edad,
                        medico_nombre, medico_matricula,
                        estudio_realizado, diagnostico_principal, cie10_sugerido,
                        hallazgos_clave,
                        destino_principal, requiere_auditoria_humana,
                        justificacion_enrutamiento, notificacion_generada,
                        oci_bucket, oci_ruta_objeto, oci_status,
                        nodos_ejecutados, tiempo_procesamiento_ms,
                        metadata, error_mensaje
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9,
                        $10, $11, $12, $13, $14, $15, $16, $17,
                        $18, $19, $20, $21, $22, $23, $24, $25,
                        $26, $27, $28
                    )
                    ON CONFLICT (documento_id) DO UPDATE SET
                        status                     = EXCLUDED.status,
                        nivel_prioridad            = EXCLUDED.nivel_prioridad,
                        score_confianza            = EXCLUDED.score_confianza,
                        destino_principal          = EXCLUDED.destino_principal,
                        requiere_auditoria_humana  = EXCLUDED.requiere_auditoria_humana,
                        oci_status                 = EXCLUDED.oci_status,
                        updated_at                 = NOW()
                """,
                    resultado.documento_id,
                    resultado.tipo_archivo,
                    resultado.canal_origen,
                    resultado.status,
                    resultado.texto_extraido,
                    resultado.clasificacion.tipo_documento,
                    resultado.clasificacion.especialidad,
                    resultado.clasificacion.nivel_prioridad,
                    resultado.clasificacion.score_confianza_clasificacion,
                    resultado.datos_extraidos.paciente.nombre if resultado.datos_extraidos.paciente else None,
                    resultado.datos_extraidos.paciente.edad if resultado.datos_extraidos.paciente else None,
                    resultado.datos_extraidos.medico_solicitante.nombre if resultado.datos_extraidos.medico_solicitante else None,
                    resultado.datos_extraidos.medico_solicitante.matricula if resultado.datos_extraidos.medico_solicitante else None,
                    resultado.datos_extraidos.estudio_realizado,
                    resultado.datos_extraidos.diagnostico_principal,
                    resultado.datos_extraidos.cie10_sugerido,
                    json.dumps(resultado.datos_extraidos.hallazgos_clave),
                    resultado.decision_enrutamiento.destino_principal,
                    resultado.decision_enrutamiento.requiere_auditoria_humana,
                    resultado.decision_enrutamiento.justificacion_enrutamiento,
                    json.dumps(resultado.decision_enrutamiento.notificacion_generada),
                    resultado.almacenamiento_oci.bucket,
                    resultado.almacenamiento_oci.ruta_objeto,
                    resultado.almacenamiento_oci.status_backup,
                    json.dumps(resultado.nodos_ejecutados),
                    resultado.tiempo_procesamiento_ms,
                    json.dumps(resultado.metadata),
                    resultado.error_mensaje,
                )
            logger.info("postgres.guardado", documento_id=resultado.documento_id)
            return True
        except Exception as exc:
            logger.error("postgres.guardar.error", documento_id=resultado.documento_id, error=str(exc))
            raise

    async def obtener_por_id(self, documento_id: str) -> Optional[dict]:
        """Obtiene un resultado de triaje por documento_id."""
        await self.inicializar()

        if self._pool is None:
            return self._mock_store.get(documento_id)

        try:
            async with self._pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM documentos_triaje WHERE documento_id = $1",
                    documento_id,
                )
                return dict(row) if row else None
        except Exception as exc:
            logger.error("postgres.obtener.error", documento_id=documento_id, error=str(exc))
            return None

    async def listar(
        self,
        status: Optional[str] = None,
        nivel_prioridad: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Lista documentos con filtros opcionales."""
        await self.inicializar()

        if self._pool is None:
            items = list(self._mock_store.values())
            if status:
                items = [i for i in items if i.get("status") == status]
            return items[:limit]

        try:
            async with self._pool.acquire() as conn:
                query = "SELECT * FROM documentos_triaje WHERE 1=1"
                params = []
                i = 1
                if status:
                    query += f" AND status = ${i}"
                    params.append(status)
                    i += 1
                if nivel_prioridad:
                    query += f" AND nivel_prioridad = ${i}"
                    params.append(nivel_prioridad)
                    i += 1
                query += f" ORDER BY created_at DESC LIMIT ${i}"
                params.append(limit)

                rows = await conn.fetch(query, *params)
                return [dict(r) for r in rows]
        except Exception as exc:
            logger.error("postgres.listar.error", error=str(exc))
            return []

    async def registrar_auditoria(
        self,
        documento_id: str,
        decision: str,
        auditor_id: str,
        comentario: Optional[str] = None,
        nueva_clasificacion: Optional[dict] = None,
    ) -> bool:
        """Registra una decisión de auditoría HITL."""
        await self.inicializar()

        if self._pool is None:
            if documento_id in self._mock_store:
                self._mock_store[documento_id]["auditoria"] = {
                    "decision": decision,
                    "auditor_id": auditor_id,
                }
            return True

        try:
            async with self._pool.acquire() as conn:
                async with conn.transaction():
                    # Obtener ID del documento
                    doc = await conn.fetchrow(
                        "SELECT id FROM documentos_triaje WHERE documento_id = $1",
                        documento_id,
                    )
                    if not doc:
                        return False

                    # Insertar registro de auditoría
                    await conn.execute("""
                        INSERT INTO auditorias_hitl (
                            documento_triaje_id, documento_id,
                            decision, auditor_id, comentario,
                            nueva_nivel_prioridad, nuevo_destino
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                    """,
                        doc["id"], documento_id,
                        decision, auditor_id, comentario,
                        nueva_clasificacion.get("nivel_prioridad") if nueva_clasificacion else None,
                        nueva_clasificacion.get("destino") if nueva_clasificacion else None,
                    )

                    # Actualizar status del documento
                    nuevo_status = "procesado" if decision in ("aprobar", "reclasificar") else "error"
                    await conn.execute(
                        "UPDATE documentos_triaje SET status = $1, updated_at = NOW() WHERE documento_id = $2",
                        nuevo_status, documento_id,
                    )

            logger.info("postgres.auditoria.registrada", documento_id=documento_id, decision=decision)
            return True
        except Exception as exc:
            logger.error("postgres.auditoria.error", documento_id=documento_id, error=str(exc))
            raise

    async def cerrar(self):
        """Cierra el pool de conexiones."""
        if self._pool:
            await self._pool.close()

    @property
    def disponible(self) -> bool:
        return self._pool is not None
