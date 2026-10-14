"""Inserta alertas inmutables ligadas a un documento de emergencia persistido."""

from app._generated.models import AlertaGuardia
from app.core.alerts import EVENTO_GUARDIA, MENSAJE_GUARDIA
from app.repositories.postgres_storage import DatabaseUnavailableError, get_db_pool


class AlertRepository:
    @staticmethod
    async def registrar_alerta(documento_id: str, usuario_id: str | None) -> AlertaGuardia:
        try:
            pool = await get_db_pool()
            if pool is None:
                raise DatabaseUnavailableError(
                    "PostgreSQL no está disponible para guardar la alerta."
                )
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """WITH evento AS (
                        INSERT INTO trazabilidad_eventos (
                            episodio_id, documento_id, usuario_id, evento, descripcion, metadata
                        )
                        SELECT episodio_id, id, $2::uuid, $3, $4,
                               jsonb_build_object(
                                   'documento_id', documento_id,
                                   'episodio_id', episodio_id,
                                   'prioridad', nivel_prioridad,
                                   'mensaje', $4::text
                               )
                        FROM documentos_triaje
                        WHERE documento_id = $1
                          AND destino_principal = 'Cola_Emergencia_Medica'
                        RETURNING id, episodio_id, metadata, created_at
                    )
                    SELECT id, episodio_id, created_at AS fecha,
                           metadata->>'documento_id' AS documento_id,
                           metadata->>'prioridad' AS prioridad,
                           metadata->>'mensaje' AS mensaje
                    FROM evento""",
                    documento_id,
                    usuario_id,
                    EVENTO_GUARDIA,
                    MENSAJE_GUARDIA,
                )
            if row is None:
                raise DatabaseUnavailableError(
                    "No se confirmó un documento de emergencia para registrar la alerta."
                )
            return AlertaGuardia.model_validate(dict(row))
        except DatabaseUnavailableError:
            raise
        except Exception as exc:
            raise DatabaseUnavailableError("No se pudo persistir la alerta de guardia.") from exc
