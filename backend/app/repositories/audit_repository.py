"""Persistencia inmutable de trazabilidad y auditoría de coordinación (HITL).

Centraliza la inserción de eventos del ciclo de vida clínico en la bitácora
``trazabilidad_eventos`` y los dictámenes del Coordinador en
``auditorias_coordinacion``. Todas las consultas usan parámetros posicionales
de asyncpg ($1, $2, ...): ningún dato clínico se interpola en el SQL, por lo
que la inyección SQL queda descartada por construcción.
"""

import json
from typing import Any

import structlog

from app.repositories.postgres_storage import DatabaseUnavailableError, get_db_pool

logger = structlog.get_logger(__name__)


class AuditRepository:
    """Repositorio de bitácora inmutable y decisiones Human-in-the-Loop."""

    @staticmethod
    async def _require_pool():
        """Exige PostgreSQL: la trazabilidad clínica nunca se persiste en memoria."""
        pool = await get_db_pool()
        if pool is None:
            raise DatabaseUnavailableError(
                "PostgreSQL no está disponible para registrar trazabilidad y auditoría."
            )
        return pool

    @staticmethod
    async def registrar_evento_trazabilidad(
        episodio_id: str | None,
        documento_id: str,
        usuario_id: str | None,
        evento: str,
        descripcion: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Inserta un evento inmutable del ciclo de vida en trazabilidad_eventos.

        Args:
            episodio_id: UUID del episodio clínico asociado (opcional).
            documento_id: Código único del documento de triaje; se resuelve al
                UUID interno de documentos_triaje dentro de la misma sentencia.
            usuario_id: UUID del usuario que originó el evento (opcional).
            evento: Nombre del evento (p. ej. DOCUMENTO_RECIBIDO).
            descripcion: Descripción funcional del evento.
            metadata: Datos complementarios que se serializan a JSONB.

        Returns:
            La fila insertada con el id y created_at generados por PostgreSQL.
        """
        pool = await AuditRepository._require_pool()
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """INSERT INTO trazabilidad_eventos (
                           episodio_id, documento_id, usuario_id,
                           evento, descripcion, metadata
                       ) VALUES (
                           $1::uuid,
                           (SELECT id FROM documentos_triaje WHERE documento_id = $2),
                           $3::uuid,
                           $4, $5, $6::jsonb
                       )
                       RETURNING id, episodio_id, documento_id, usuario_id,
                                 evento, descripcion, metadata, created_at""",
                    episodio_id,
                    documento_id,
                    usuario_id,
                    evento,
                    descripcion,
                    json.dumps(metadata or {}),
                )
            logger.info("audit.trazabilidad.registrada", evento=evento, documento_id=documento_id)
            return dict(row) if row else {}
        except Exception as exc:
            logger.error("audit.trazabilidad.error", evento=evento, error=str(exc))
            raise DatabaseUnavailableError(
                "No se pudo registrar el evento de trazabilidad en PostgreSQL."
            ) from exc

    @staticmethod
    async def registrar_auditoria_coordinacion(
        episodio_id: str | None,
        documento_id: str,
        coordinador_id: str | None,
        decision: str,
        justificacion: str,
    ) -> dict[str, Any]:
        """Inserta el dictamen del Coordinador en auditorias_coordinacion.

        Args:
            episodio_id: UUID del episodio clínico dictaminado (opcional).
            documento_id: Código único del documento de triaje; se resuelve al
                UUID interno de documentos_triaje dentro de la misma sentencia.
            coordinador_id: UUID del usuario COORDINADOR que emite el dictamen.
            decision: Decisión clínica (p. ej. aprobar, reclasificar, rechazar).
            justificacion: Justificación clínica obligatoria del dictamen.

        Returns:
            La fila insertada con el id y created_at generados por PostgreSQL.
        """
        pool = await AuditRepository._require_pool()
        try:
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """INSERT INTO auditorias_coordinacion (
                           episodio_id, documento_id, coordinador_id,
                           decision, justificacion_clinica
                       ) VALUES (
                           $1::uuid,
                           (SELECT id FROM documentos_triaje WHERE documento_id = $2),
                           $3::uuid,
                           $4, $5
                       )
                       RETURNING id, episodio_id, documento_id, coordinador_id,
                                 decision, justificacion_clinica, created_at""",
                    episodio_id,
                    documento_id,
                    coordinador_id,
                    decision,
                    justificacion,
                )
            logger.info(
                "audit.coordinacion.registrada",
                decision=decision,
                documento_id=documento_id,
            )
            return dict(row) if row else {}
        except Exception as exc:
            logger.error("audit.coordinacion.error", decision=decision, error=str(exc))
            raise DatabaseUnavailableError(
                "No se pudo registrar la auditoría de coordinación en PostgreSQL."
            ) from exc

    @staticmethod
    async def obtener_triajes_pendientes(
        especialidad: str | None = None,
        minutos_espera: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Consulta la bandeja de triajes pendientes de revisión HITL con filtros opcionales."""
        pool = await AuditRepository._require_pool()
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT 
                           dt.documento_id,
                           dt.episodio_id,
                           dt.created_at AS fecha_ingesta,
                           ROUND(EXTRACT(EPOCH FROM (NOW() - dt.created_at)) / 60)::integer AS tiempo_espera_minutos,
                           dt.status::text AS estado,
                           COALESCE(dt.canal_origen, 'Admision') AS canal_origen,
                           dt.especialidad AS especialidad_sugerida,
                           dt.nivel_prioridad::text AS nivel_prioridad,
                           dt.score_confianza AS confianza_ia,
                           dt.justificacion_enrutamiento AS motivo_hitl,
                           dt.diagnostico_principal AS diagnostico_preliminar,
                           dt.cie10_sugerido AS codigo_cie10,
                           CASE 
                               WHEN p.id IS NOT NULL THEN json_build_object(
                                   'id', p.id::text,
                                   'nombres', p.nombres,
                                   'apellidos', p.apellidos,
                                   'numero_documento', p.numero_documento,
                                   'historia_clinica', p.historia_clinica,
                                   'numero_telefono', p.numero_telefono,
                                   'genero', p.genero
                               )
                               ELSE NULL
                           END AS paciente
                       FROM documentos_triaje dt
                       LEFT JOIN pacientes p ON p.id = dt.paciente_id
                       WHERE (dt.requiere_auditoria_humana = TRUE 
                              OR dt.status = 'pendiente_auditoria' 
                              OR dt.destino_principal = 'Cola_Auditoria_Humana')
                         AND ($1::text IS NULL OR dt.especialidad ILIKE '%' || $1 || '%')
                         AND ($2::integer IS NULL OR (EXTRACT(EPOCH FROM (NOW() - dt.created_at)) / 60) >= $2)
                       ORDER BY dt.created_at ASC
                       LIMIT $3 OFFSET $4""",
                    especialidad,
                    minutos_espera,
                    limit,
                    offset,
                )
                return [dict(r) for r in rows] if rows else []
        except Exception as exc:
            logger.error("audit.obtener_pendientes.error", error=str(exc))
            raise DatabaseUnavailableError(
                "No se pudo consultar la bandeja de triajes pendientes en PostgreSQL."
            ) from exc

    @staticmethod
    async def obtener_eventos_documento(documento_id: str) -> list[dict[str, Any]]:
        """Obtiene la bitácora inmutable de eventos de trazabilidad de un documento."""
        pool = await AuditRepository._require_pool()
        try:
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT 
                           te.id,
                           dt.documento_id,
                           te.episodio_id,
                           te.usuario_id,
                           te.evento,
                           te.descripcion,
                           te.metadata,
                           te.created_at
                       FROM trazabilidad_eventos te
                       JOIN documentos_triaje dt ON dt.id = te.documento_id
                       WHERE dt.documento_id = $1
                       ORDER BY te.created_at ASC""",
                    documento_id,
                )
                results = []
                for r in rows or []:
                    item = dict(r)
                    if isinstance(item.get("metadata"), str):
                        try:
                            item["metadata"] = json.loads(item["metadata"])
                        except Exception:
                            item["metadata"] = {}
                    results.append(item)
                return results
        except Exception as exc:
            logger.error("audit.obtener_eventos.error", documento_id=documento_id, error=str(exc))
            raise DatabaseUnavailableError(
                "No se pudo consultar la trazabilidad del documento en PostgreSQL."
            ) from exc

    @staticmethod
    async def resolver_triaje(
        documento_id: str,
        coordinador_id: str | None,
        decision: str,
        justificacion: str,
        categoria_destino: str | None = None,
        prioridad_sugerida: str | None = None,
    ) -> dict[str, Any]:
        """Ejecuta la resolución completa de un triaje HITL con dictamen, actualización y trazabilidad."""
        pool = await AuditRepository._require_pool()
        try:
            async with pool.acquire() as conn:
                async with conn.transaction():
                    # 1. Verificar existencia del documento
                    doc = await conn.fetchrow(
                        "SELECT id, episodio_id, status FROM documentos_triaje WHERE documento_id = $1",
                        documento_id,
                    )
                    if not doc:
                        raise ValueError(f"Documento no encontrado: {documento_id}")

                    doc_uuid = doc["id"]
                    episodio_id = doc["episodio_id"]

                    # 2. Registrar auditoría de coordinación
                    audit_row = await conn.fetchrow(
                        """INSERT INTO auditorias_coordinacion (
                               episodio_id, documento_id, coordinador_id,
                               decision, justificacion_clinica,
                               nueva_prioridad, nueva_especialidad
                           ) VALUES (
                               $1, $2, $3::uuid, $4, $5, $6, $7
                           )
                           RETURNING id, episodio_id, documento_id, coordinador_id,
                                     decision, justificacion_clinica, created_at""",
                        episodio_id,
                        doc_uuid,
                        coordinador_id,
                        decision,
                        justificacion,
                        prioridad_sugerida,
                        categoria_destino,
                    )

                    # 3. Determinar nuevo estado y destino
                    nuevo_status = "rechazado" if decision == "rechazar" else "procesado"
                    evento_nombre = (
                        "AUDITORIA_APROBADA"
                        if decision == "aprobar"
                        else "AUDITORIA_RECLASIFICADA"
                        if decision == "reclasificar"
                        else "AUDITORIA_RECHAZADA"
                    )

                    # 4. Actualizar documento de triaje
                    await conn.execute(
                        """UPDATE documentos_triaje
                           SET status = $1::status_documento_enum,
                               requiere_auditoria_humana = FALSE,
                               destino_principal = COALESCE($3::destino_enum, destino_principal),
                               nivel_prioridad = COALESCE($4::nivel_prioridad_enum, nivel_prioridad),
                               updated_at = NOW()
                           WHERE id = $2""",
                        nuevo_status,
                        doc_uuid,
                        categoria_destino if categoria_destino in ("Cola_Emergencia_Medica", "Cola_Rutina", "Cola_Auditoria_Humana", "Farmacia_Hospitalaria") else None,
                        prioridad_sugerida if prioridad_sugerida in ("Urgente", "Rutina", "Ambiguo") else None,
                    )

                    # 5. Registrar evento inmutable de trazabilidad
                    await conn.execute(
                        """INSERT INTO trazabilidad_eventos (
                               episodio_id, documento_id, usuario_id,
                               evento, descripcion, metadata
                           ) VALUES (
                               $1, $2, $3::uuid, $4, $5, $6::jsonb
                           )""",
                        episodio_id,
                        doc_uuid,
                        coordinador_id,
                        evento_nombre,
                        f"Resolución HITL: {decision}. Justificación: {justificacion}",
                        json.dumps({
                            "decision": decision,
                            "justificacion": justificacion,
                            "categoria_destino": categoria_destino,
                            "prioridad_sugerida": prioridad_sugerida,
                        }),
                    )

                    logger.info(
                        "audit.triaje.resuelto",
                        documento_id=documento_id,
                        decision=decision,
                        nuevo_status=nuevo_status,
                    )

                    res = dict(audit_row) if audit_row else {}
                    res["documento_id"] = documento_id
                    res["nuevo_estado"] = nuevo_status
                    return res
        except Exception as exc:
            logger.error("audit.resolver_triaje.error", documento_id=documento_id, error=str(exc))
            if isinstance(exc, ValueError):
                raise
            raise DatabaseUnavailableError(
                "No se pudo completar la resolución médica en PostgreSQL."
            ) from exc
