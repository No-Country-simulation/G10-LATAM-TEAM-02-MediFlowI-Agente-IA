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

_GLOBAL_DB_POOL = None


def estado_final_auditoria(decision: str) -> str:
    """Devuelve el estado terminal correcto para una decisión HITL."""
    return "rechazado" if decision == "rechazar" else "procesado"


def evento_auditoria(decision: str) -> str:
    """Identifica el evento funcional que corresponde a una decisión HITL."""
    return {
        "aprobar": "AUDITORIA_APROBADA",
        "reclasificar": "AUDITORIA_RECLASIFICADA",
        "rechazar": "AUDITORIA_RECHAZADA",
    }[decision]


async def get_db_pool():
    """Obtiene o inicializa el pool global de conexiones asyncpg."""
    global _GLOBAL_DB_POOL
    if _GLOBAL_DB_POOL is not None:
        return _GLOBAL_DB_POOL
    
    from app.core.config import get_settings
    settings = get_settings()
    db_url = getattr(settings, "database_url", None)
    if not db_url:
        return None
        
    try:
        import asyncpg
        url = db_url.replace("postgresql+asyncpg://", "postgresql://")
        _GLOBAL_DB_POOL = await asyncpg.create_pool(url, min_size=1, max_size=10)
        return _GLOBAL_DB_POOL
    except Exception as exc:
        logger.error("postgres.pool.error", error=str(exc))
        return None


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
        self._mock_history: list[dict] = []
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

    async def guardar_resultado(
        self,
        resultado: AgentState,
        usuario_registro_id: Optional[str] = None,
    ) -> bool:
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
            self._mock_store[resultado.documento_id]["usuario_registro_id"] = usuario_registro_id
            self._mock_store[resultado.documento_id]["paciente_id"] = resultado.metadata.get("paciente_id")
            self._mock_history.extend([
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "DOCUMENTO_RECIBIDO"},
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "PROCESAMIENTO_INICIADO"},
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "OCR_COMPLETADO"},
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "EXTRACCION_IA_COMPLETADA"},
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "CLASIFICACION_COMPLETADA"},
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "ENRUTAMIENTO_COMPLETADO"},
                {"documento_id": resultado.documento_id, "usuario_id": usuario_registro_id, "evento": "PROCESAMIENTO_FINALIZADO"},
            ])
            if resultado.metadata.get("asociacion_paciente"):
                self._mock_history.append({
                    "documento_id": resultado.documento_id,
                    "usuario_id": usuario_registro_id,
                    "evento": {
                        "asociado": "PACIENTE_ASOCIADO",
                        "conflicto": "CONFLICTO_PACIENTE",
                    }.get(resultado.metadata["asociacion_paciente"], "PACIENTE_SIN_COINCIDENCIA"),
                })
            logger.info("postgres.mock.guardado", documento_id=resultado.documento_id)
            return True

        try:
            async with self._pool.acquire() as conn:
                # Obtener el modo de almacenamiento activo en configuracion_sistema
                modo_row = await conn.fetchval(
                    "SELECT valor FROM configuracion_sistema WHERE clave = 'modo_almacenamiento'"
                )
                storage_prov = modo_row.upper() if modo_row else "LOCAL"

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
                        metadata, error_mensaje, storage_provider,
                        archivo_original, resultado_json, nombre_original
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9,
                        $10, $11, $12, $13, $14, $15, $16, $17,
                        $18, $19, $20, $21, $22, $23, $24, $25,
                        $26, $27, $28, $29, $30, $31, $32
                    )
                    ON CONFLICT (documento_id) DO UPDATE SET
                        status                     = EXCLUDED.status,
                        nivel_prioridad            = EXCLUDED.nivel_prioridad,
                        score_confianza            = EXCLUDED.score_confianza,
                        destino_principal          = EXCLUDED.destino_principal,
                        requiere_auditoria_humana  = EXCLUDED.requiere_auditoria_humana,
                        oci_status                 = EXCLUDED.oci_status,
                        storage_provider           = EXCLUDED.storage_provider,
                        archivo_original           = EXCLUDED.archivo_original,
                        resultado_json             = EXCLUDED.resultado_json,
                        nombre_original            = EXCLUDED.nombre_original,
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
                    storage_prov,
                    resultado.almacenamiento_oci.archivo_original,
                    resultado.almacenamiento_oci.resultado_json,
                    resultado.almacenamiento_oci.nombre_original,
                )

                if usuario_registro_id:
                    await conn.execute(
                        """UPDATE documentos_triaje
                           SET usuario_registro_id = COALESCE(usuario_registro_id, $1)
                           WHERE documento_id = $2""",
                        usuario_registro_id,
                        resultado.documento_id,
                    )

                if resultado.metadata.get("paciente_id"):
                    await conn.execute(
                        "UPDATE documentos_triaje SET paciente_id = $1::uuid WHERE documento_id = $2",
                        resultado.metadata["paciente_id"], resultado.documento_id,
                    )

                # También registrar en cola_procesamiento para gestión operativa
                await conn.execute("""
                    INSERT INTO cola_procesamiento (
                        documento_id, destino, nivel_prioridad, score_confianza, status
                    ) VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (documento_id) DO UPDATE SET
                        destino         = EXCLUDED.destino,
                        nivel_prioridad = EXCLUDED.nivel_prioridad,
                        score_confianza = EXCLUDED.score_confianza,
                        status          = EXCLUDED.status
                """,
                    resultado.documento_id,
                    resultado.decision_enrutamiento.destino_principal,
                    resultado.clasificacion.nivel_prioridad,
                    resultado.clasificacion.score_confianza_clasificacion,
                    resultado.status,
                )

                documento = await conn.fetchrow(
                    "SELECT id FROM documentos_triaje WHERE documento_id = $1",
                    resultado.documento_id,
                )
                eventos = [
                    ("DOCUMENTO_RECIBIDO", None, "recibido"),
                    ("PROCESAMIENTO_INICIADO", "recibido", "procesando"),
                    ("OCR_COMPLETADO", "procesando", "procesando"),
                    ("EXTRACCION_IA_COMPLETADA", "procesando", "procesando"),
                    ("CLASIFICACION_COMPLETADA", "procesando", "procesando"),
                    ("ENRUTAMIENTO_COMPLETADO", "procesando", "procesando"),
                    ("PROCESAMIENTO_FINALIZADO", "procesando", resultado.status),
                ]
                if resultado.status == "pendiente_auditoria":
                    eventos.append(("PENDIENTE_AUDITORIA", "procesando", "pendiente_auditoria"))
                if resultado.metadata.get("asociacion_paciente") == "asociado":
                    eventos.append(("PACIENTE_ASOCIADO", None, None))
                elif resultado.metadata.get("asociacion_paciente") == "conflicto":
                    eventos.append(("CONFLICTO_PACIENTE", None, None))
                for evento, estado_anterior, estado_nuevo in eventos:
                    await conn.execute("""
                        INSERT INTO historial_documento (
                            documento_triaje_id, usuario_id, evento,
                            estado_anterior, estado_nuevo
                        ) VALUES ($1, $2, $3, $4, $5)
                    """, documento["id"], usuario_registro_id, evento, estado_anterior, estado_nuevo)

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

    async def listar_historial(self, documento_id: str) -> list[dict]:
        """Lista la trazabilidad funcional del documento en orden cronológico."""
        await self.inicializar()

        if self._pool is None:
            return [event for event in self._mock_history if event["documento_id"] == documento_id]

        async with self._pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT hd.evento, hd.estado_anterior, hd.estado_nuevo,
                       hd.descripcion, hd.metadata, hd.created_at, hd.usuario_id
                FROM historial_documento hd
                JOIN documentos_triaje dt ON dt.id = hd.documento_triaje_id
                WHERE dt.documento_id = $1
                ORDER BY hd.created_at ASC
            """, documento_id)
            return [dict(row) for row in rows]

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
                self._mock_store[documento_id]["status"] = estado_final_auditoria(decision)
            self._mock_history.append({
                "documento_id": documento_id,
                "usuario_id": auditor_id,
                "evento": evento_auditoria(decision),
                "estado_nuevo": estado_final_auditoria(decision),
            })
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
                    nuevo_status = estado_final_auditoria(decision)
                    await conn.execute(
                        "UPDATE documentos_triaje SET status = $1, updated_at = NOW() WHERE documento_id = $2",
                        nuevo_status, documento_id,
                    )
                    await conn.execute("""
                        INSERT INTO historial_documento (
                            documento_triaje_id, usuario_id, evento,
                            estado_anterior, estado_nuevo, descripcion
                        ) VALUES ($1, $2, $3, 'pendiente_auditoria', $4, $5)
                    """,
                        doc["id"], auditor_id, evento_auditoria(decision),
                        nuevo_status, comentario,
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
