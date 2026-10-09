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
            return dict(row)
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
            return dict(row)
        except Exception as exc:
            logger.error("audit.coordinacion.error", decision=decision, error=str(exc))
            raise DatabaseUnavailableError(
                "No se pudo registrar la auditoría de coordinación en PostgreSQL."
            ) from exc
