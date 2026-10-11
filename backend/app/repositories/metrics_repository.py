"""Agregados de triaje de solo lectura, desde una única vista PostgreSQL."""

import structlog

from app._generated.models import MetricsResponse
from app.repositories.postgres_storage import DatabaseUnavailableError, get_db_pool

logger = structlog.get_logger(__name__)

# Una fila base por documento_id UNIQUE. EXISTS conserva la identidad UUID sin
# multiplicar documentos, tiempos o indicadores por auditorías/eventos repetidos.
METRICS_SQL = """
WITH cohorte AS (
    SELECT d.nivel_prioridad, d.tiempo_procesamiento_ms,
           d.requiere_auditoria_humana
           OR EXISTS (
               SELECT 1 FROM auditorias_hitl a
               WHERE a.documento_triaje_id = d.id
                 AND a.decision IN ('aprobar', 'reclasificar', 'rechazar')
           )
           OR EXISTS (
               SELECT 1 FROM historial_documento h
               WHERE h.documento_triaje_id = d.id
                 AND h.evento IN ('PENDIENTE_AUDITORIA', 'AUDITORIA_APROBADA',
                                  'AUDITORIA_RECLASIFICADA', 'AUDITORIA_RECHAZADA')
           )
           OR EXISTS (
               SELECT 1 FROM auditorias_coordinacion a
               WHERE a.documento_id = d.id
                 AND a.decision IN ('aprobar', 'aprobado', 'reclasificar',
                                    'reclasificado', 'rechazar', 'rechazado')
           ) AS hitl
    FROM documentos_triaje d
    WHERE d.status IN ('procesado', 'pendiente_auditoria', 'rechazado')
      AND EXISTS (
          SELECT 1 FROM historial_documento f
          WHERE f.documento_triaje_id = d.id
            AND f.evento = 'PROCESAMIENTO_FINALIZADO'
      )
), agregados AS (
    SELECT COUNT(*) FILTER (WHERE nivel_prioridad = 'Urgente') AS rojo,
           COUNT(*) FILTER (WHERE nivel_prioridad = 'Ambiguo') AS amarillo,
           COUNT(*) FILTER (WHERE nivel_prioridad = 'Rutina') AS verde,
           COUNT(*)::numeric AS d,
           (COUNT(*) FILTER (WHERE hitl))::numeric AS n,
           (COUNT(*) FILTER (WHERE tiempo_procesamiento_ms >= 0))::numeric AS t,
           SUM(tiempo_procesamiento_ms::numeric)
               FILTER (WHERE tiempo_procesamiento_ms >= 0) AS s
    FROM cohorte
)
SELECT rojo, amarillo, verde,
       CASE WHEN d > 0 THEN div(2::numeric * 10000 * n + d, 2::numeric * d) / 100
            ELSE NULL END AS tasa_hitl,
       CASE WHEN t > 0 THEN div(2::numeric * s + t, 2::numeric * t) / 1000
            ELSE NULL END AS tiempo_promedio_ia_segundos
FROM agregados
"""


async def obtener_metricas() -> MetricsResponse:
    """Lee todos los indicadores sin caché, IA, almacenamiento ni escrituras."""
    try:
        pool = await get_db_pool()
        if pool is None:
            raise DatabaseUnavailableError("PostgreSQL no está disponible para consultar métricas.")
        async with pool.acquire() as conn:
            async with conn.transaction(isolation="read_committed", readonly=True):
                row = await conn.fetchrow(METRICS_SQL)
        if row is None:
            raise DatabaseUnavailableError("PostgreSQL no devolvió los agregados de métricas.")
        # numeric ya cuantizado por SQL; serialización numérica, sin redondeo nuevo.
        return MetricsResponse(
            distribucion_prioridad={"Rojo": row["rojo"], "Amarillo": row["amarillo"], "Verde": row["verde"]},
            tasa_hitl=None if row["tasa_hitl"] is None else float(row["tasa_hitl"]),
            tiempo_promedio_ia_segundos=None if row["tiempo_promedio_ia_segundos"] is None else float(row["tiempo_promedio_ia_segundos"]),
        )
    except DatabaseUnavailableError:
        raise
    except Exception as exc:
        # Nunca registrar DSN, credenciales, parámetros o mensajes del driver.
        logger.error("postgres.metrics.error", exception_type=type(exc).__name__)
        raise DatabaseUnavailableError("No fue posible consultar las métricas en PostgreSQL.") from None
