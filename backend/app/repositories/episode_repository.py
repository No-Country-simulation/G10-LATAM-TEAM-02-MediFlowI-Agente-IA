"""
MediFlow — Repositorio asíncrono para la gestión de Episodios Clínicos.

Encapsula la persistencia en la tabla `episodios_clinicos` y las consultas agregadas
sobre la vista SQL `v_episodios_detalle` en PostgreSQL con asyncpg.
"""

from datetime import datetime, timezone
import secrets
from typing import Any
from uuid import UUID

import structlog

from app.repositories.postgres_storage import DatabaseUnavailableError, get_db_pool

logger = structlog.get_logger(__name__)

ESTADOS_VALIDOS = {"ingresado", "en_triaje", "atendido", "derivado", "cerrado"}

VISTA_EPISODIOS_COLUMNS = """
    episodio_id,
    codigo_episodio,
    estado_atencion,
    nivel_prioridad,
    motivo_consulta,
    diagnostico_general,
    diagnostico_especialista,
    especialidad_requerida,
    created_at,
    updated_at,
    paciente_id,
    paciente_tipo_documento,
    paciente_numero_documento,
    paciente_historia_clinica,
    paciente_nombres,
    paciente_apellidos,
    paciente_nombre_completo,
    paciente_fecha_nacimiento,
    paciente_edad,
    paciente_genero,
    paciente_numero_telefono,
    paciente_correo,
    operador_ingreso_id,
    operador_ingreso_nombre,
    medico_general_id,
    medico_general_nombre,
    medico_general_especialidad,
    medico_especialista_id,
    medico_especialista_nombre,
    medico_especialista_especialidad
"""


def _generate_episode_code() -> str:
    """Genera un código clínico único determinista (ej. EP-20261005-A1B2)."""
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    suffix = secrets.token_hex(2).upper()
    return f"EP-{date_str}-{suffix}"


def _ensure_uuid(val: Any) -> UUID | None:
    """Convierte un valor a UUID si es string o retorna el UUID directo."""
    if val is None:
        return None
    if isinstance(val, UUID):
        return val
    try:
        return UUID(str(val))
    except (ValueError, TypeError, AttributeError):
        return None


async def _require_pool():
    """Valida la disponibilidad del pool de conexiones asyncpg."""
    pool = await get_db_pool()
    if pool is None:
        raise DatabaseUnavailableError("PostgreSQL no está disponible para gestionar episodios clínicos.")
    return pool


def _database_failure(operation: str, exc: Exception) -> DatabaseUnavailableError:
    """Registra en log estructurado y empaqueta el fallo en DatabaseUnavailableError."""
    logger.error("episode_repo.database_error", operation=operation, error=str(exc))
    return DatabaseUnavailableError(f"No fue posible {operation} en PostgreSQL.")


async def create_episode(data: dict[str, Any]) -> dict[str, Any]:
    """
    Crea un nuevo episodio clínico en `episodios_clinicos`.

    Genera automáticamente el código si no se provee y fija 'ingresado' por defecto.
    """
    estado_atencion = data.get("estado_atencion", "ingresado")
    if estado_atencion not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado de atención inválido: {estado_atencion}. Estados permitidos: {ESTADOS_VALIDOS}")

    pool = await _require_pool()

    codigo_episodio = data.get("codigo_episodio") or _generate_episode_code()
    paciente_id = _ensure_uuid(data.get("paciente_id"))
    operador_ingreso_id = _ensure_uuid(data.get("operador_ingreso_id"))
    medico_general_id = _ensure_uuid(data.get("medico_general_id"))
    medico_especialista_id = _ensure_uuid(data.get("medico_especialista_id"))
    especialidad_requerida = data.get("especialidad_requerida")
    nivel_prioridad = data.get("nivel_prioridad", "Rutina")
    motivo_consulta = data.get("motivo_consulta")
    diagnostico_general = data.get("diagnostico_general")
    diagnostico_especialista = data.get("diagnostico_especialista")

    query = """
        INSERT INTO episodios_clinicos (
            codigo_episodio,
            paciente_id,
            operador_ingreso_id,
            medico_general_id,
            medico_especialista_id,
            especialidad_requerida,
            estado_atencion,
            nivel_prioridad,
            motivo_consulta,
            diagnostico_general,
            diagnostico_especialista,
            created_at,
            updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW())
        RETURNING *;
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                query,
                codigo_episodio,
                paciente_id,
                operador_ingreso_id,
                medico_general_id,
                medico_especialista_id,
                especialidad_requerida,
                estado_atencion,
                nivel_prioridad,
                motivo_consulta,
                diagnostico_general,
                diagnostico_especialista,
            )
            if row is None:
                raise DatabaseUnavailableError("La inserción del episodio no devolvió datos.")

            logger.info("episode_repo.created", episodio_id=str(row["id"]), codigo=row["codigo_episodio"])
            return dict(row)
    except DatabaseUnavailableError:
        raise
    except Exception as exc:
        raise _database_failure("crear episodio clínico", exc) from exc


async def get_episode_by_id(episode_id: UUID | str) -> dict[str, Any] | None:
    """Obtiene el detalle consolidado de un episodio clínico desde `v_episodios_detalle`."""
    uuid_val = _ensure_uuid(episode_id)
    if uuid_val is None:
        return None

    pool = await _require_pool()
    query = f"""
        SELECT {VISTA_EPISODIOS_COLUMNS}
        FROM v_episodios_detalle
        WHERE episodio_id = $1;
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, uuid_val)
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("obtener episodio por ID", exc) from exc


async def get_episode_by_code(codigo_episodio: str) -> dict[str, Any] | None:
    """Obtiene el detalle consolidado de un episodio clínico por su código único."""
    if not codigo_episodio or not codigo_episodio.strip():
        return None

    pool = await _require_pool()
    query = f"""
        SELECT {VISTA_EPISODIOS_COLUMNS}
        FROM v_episodios_detalle
        WHERE codigo_episodio = $1;
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, codigo_episodio.strip())
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("obtener episodio por código", exc) from exc


async def update_episode_status(episode_id: UUID | str, nuevo_estado: str) -> bool:
    """Actualiza el estado de atención de un episodio clínico."""
    uuid_val = _ensure_uuid(episode_id)
    if uuid_val is None:
        return False

    if nuevo_estado not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado de atención inválido: {nuevo_estado}. Estados permitidos: {ESTADOS_VALIDOS}")

    pool = await _require_pool()
    query = """
        UPDATE episodios_clinicos
        SET estado_atencion = $1,
            updated_at = NOW()
        WHERE id = $2;
    """

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(query, nuevo_estado, uuid_val)
            # asyncpg retorna "UPDATE N"
            updated = result.endswith(" 1") or result == "UPDATE 1"
            if updated:
                logger.info("episode_repo.status_updated", episodio_id=str(uuid_val), nuevo_estado=nuevo_estado)
            return updated
    except Exception as exc:
        raise _database_failure("actualizar estado del episodio", exc) from exc


async def assign_doctor(
    episode_id: UUID | str,
    medico_id: UUID | str,
    rol: str = "general",
    especialidad: str | None = None,
) -> bool:
    """
    Asigna un médico general o especialista al episodio.

    rol: 'general' (actualiza medico_general_id) o 'especialista' (actualiza medico_especialista_id).
    """
    uuid_ep = _ensure_uuid(episode_id)
    uuid_med = _ensure_uuid(medico_id)
    if uuid_ep is None or uuid_med is None:
        return False

    pool = await _require_pool()

    if rol == "especialista":
        query = """
            UPDATE episodios_clinicos
            SET medico_especialista_id = $1,
                especialidad_requerida = COALESCE($2, especialidad_requerida),
                updated_at = NOW()
            WHERE id = $3;
        """
        args = (uuid_med, especialidad, uuid_ep)
    else:
        query = """
            UPDATE episodios_clinicos
            SET medico_general_id = $1,
                updated_at = NOW()
            WHERE id = $2;
        """
        args = (uuid_med, uuid_ep)

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(query, *args)
            updated = result.endswith(" 1") or result == "UPDATE 1"
            if updated:
                logger.info("episode_repo.doctor_assigned", episodio_id=str(uuid_ep), medico_id=str(uuid_med), rol=rol)
            return updated
    except Exception as exc:
        raise _database_failure("asignar médico al episodio", exc) from exc


async def list_episodes(
    estado: str | None = None,
    nivel_prioridad: str | None = None,
    paciente_id: UUID | str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """
    Lista episodios clínicos enriquecidos desde `v_episodios_detalle` aplicando filtros dinámicos.
    """
    pool = await _require_pool()

    clauses: list[str] = []
    params: list[Any] = []

    if estado and estado.strip():
        params.append(estado.strip())
        clauses.append(f"estado_atencion = ${len(params)}")

    if nivel_prioridad and nivel_prioridad.strip():
        params.append(nivel_prioridad.strip())
        clauses.append(f"nivel_prioridad = ${len(params)}")

    paciente_uuid = _ensure_uuid(paciente_id)
    if paciente_uuid:
        params.append(paciente_uuid)
        clauses.append(f"paciente_id = ${len(params)}")

    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""

    params.append(limit)
    limit_param = f"${len(params)}"
    params.append(offset)
    offset_param = f"${len(params)}"

    query = f"""
        SELECT {VISTA_EPISODIOS_COLUMNS}
        FROM v_episodios_detalle
        {where_sql}
        ORDER BY created_at DESC
        LIMIT {limit_param} OFFSET {offset_param};
    """

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [dict(row) for row in rows]
    except Exception as exc:
        raise _database_failure("listar episodios clínicos", exc) from exc
