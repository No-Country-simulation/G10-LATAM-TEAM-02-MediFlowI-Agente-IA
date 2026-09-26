"""Persistencia clínica de pacientes y sus documentos en PostgreSQL."""

from typing import Any

import structlog

from app.repositories.postgres_storage import DatabaseUnavailableError, get_db_pool

logger = structlog.get_logger(__name__)

PATIENT_COLUMNS = """
    id, tipo_documento, numero_documento, historia_clinica,
    nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
    created_at, updated_at
"""


async def _require_pool():
    """Exige PostgreSQL para impedir estados clínicos ficticios en memoria."""
    pool = await get_db_pool()
    if pool is None:
        raise DatabaseUnavailableError("PostgreSQL no está disponible para gestionar pacientes.")
    return pool


def _database_failure(operation: str, exc: Exception) -> DatabaseUnavailableError:
    logger.error("patient_repo.database_error", operation=operation, error=str(exc))
    return DatabaseUnavailableError(f"No fue posible {operation} en PostgreSQL.")


async def list_patients(search: str | None = None) -> list[dict[str, Any]]:
    """Lista pacientes y permite buscar por documento, HC o nombre."""
    pool = await _require_pool()
    try:
        async with pool.acquire() as conn:
            if search and search.strip():
                rows = await conn.fetch(
                    f"""SELECT {PATIENT_COLUMNS} FROM pacientes
                        WHERE numero_documento ILIKE $1
                           OR historia_clinica ILIKE $1
                           OR nombres ILIKE $1
                           OR apellidos ILIKE $1
                           OR (nombres || ' ' || apellidos) ILIKE $1
                        ORDER BY created_at DESC""",
                    f"%{search.strip()}%",
                )
            else:
                rows = await conn.fetch(
                    f"SELECT {PATIENT_COLUMNS} FROM pacientes ORDER BY created_at DESC"
                )
            return [dict(row) for row in rows]
    except Exception as exc:
        raise _database_failure("listar pacientes", exc) from exc


async def get_patient_by_id(patient_id: str) -> dict[str, Any] | None:
    """Obtiene un paciente por UUID."""
    pool = await _require_pool()
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT {PATIENT_COLUMNS} FROM pacientes WHERE id = $1::uuid", patient_id
            )
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("consultar el paciente", exc) from exc


async def get_patient_by_doc(numero_documento: str) -> dict[str, Any] | None:
    """Obtiene un paciente por documento de identidad exacto."""
    pool = await _require_pool()
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT {PATIENT_COLUMNS} FROM pacientes WHERE numero_documento = $1",
                numero_documento.strip(),
            )
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("consultar el paciente por documento", exc) from exc


async def get_patient_by_hc(historia_clinica: str) -> dict[str, Any] | None:
    """Obtiene un paciente por historia clínica exacta."""
    pool = await _require_pool()
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"SELECT {PATIENT_COLUMNS} FROM pacientes WHERE historia_clinica = $1",
                historia_clinica.strip(),
            )
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("consultar el paciente por historia clínica", exc) from exc


async def resolver_paciente_por_identificadores(
    dni: str | None, historia_clinica: str | None
) -> dict[str, Any]:
    """Resuelve identidad sólo por DNI/HC y nunca infiere por el nombre."""
    paciente_dni = await get_patient_by_doc(dni) if dni else None
    paciente_hc = await get_patient_by_hc(historia_clinica) if historia_clinica else None
    if paciente_dni and paciente_hc and paciente_dni["id"] != paciente_hc["id"]:
        return {"estado": "conflicto", "paciente": None}
    paciente = paciente_dni or paciente_hc
    return {"estado": "asociado" if paciente else "sin_coincidencia", "paciente": paciente}


async def create_patient(data: dict[str, Any]) -> dict[str, Any] | None:
    """Registra un paciente y devuelve la fila persistida."""
    pool = await _require_pool()
    historia_clinica = data.get("historia_clinica")
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""INSERT INTO pacientes (
                        tipo_documento, numero_documento, historia_clinica,
                        nombres, apellidos, fecha_nacimiento, sexo, telefono, correo
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    RETURNING {PATIENT_COLUMNS}""",
                data.get("tipo_documento", "DNI"),
                data["numero_documento"].strip(),
                historia_clinica.strip() if isinstance(historia_clinica, str) else None,
                data["nombres"].strip(),
                data["apellidos"].strip(),
                data.get("fecha_nacimiento"),
                data.get("sexo"),
                data.get("telefono"),
                data.get("correo"),
            )
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("registrar el paciente", exc) from exc


async def update_patient(patient_id: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Actualiza campos permitidos de un paciente existente."""
    pool = await _require_pool()
    fields: list[str] = []
    values: list[Any] = []
    for key in (
        "tipo_documento",
        "numero_documento",
        "historia_clinica",
        "nombres",
        "apellidos",
        "fecha_nacimiento",
        "sexo",
        "telefono",
        "correo",
    ):
        if key in data and data[key] is not None:
            values.append(data[key])
            fields.append(f"{key} = ${len(values)}")
    if not fields:
        return await get_patient_by_id(patient_id)

    values.append(patient_id)
    query = f"""UPDATE pacientes
                SET {", ".join(fields)}, updated_at = NOW()
                WHERE id = ${len(values)}::uuid
                RETURNING {PATIENT_COLUMNS}"""
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
    except Exception as exc:
        raise _database_failure("actualizar el paciente", exc) from exc


async def get_patient_documents(patient_id: str) -> list[dict[str, Any]]:
    """Lista documentos asociados por FK o por DNI/HC exactos detectados por IA."""
    pool = await _require_pool()
    patient = await get_patient_by_id(patient_id)
    if not patient:
        return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT d.id, d.documento_id, d.tipo_archivo, d.canal_origen, d.status,
                          d.tipo_documento, d.especialidad, d.nivel_prioridad, d.score_confianza,
                          d.paciente_nombre, d.paciente_edad, d.paciente_id_externo,
                          d.medico_nombre, d.estudio_realizado, d.diagnostico_principal,
                          d.cie10_sugerido, d.destino_principal, d.created_at
                   FROM documentos_triaje d
                   WHERE d.paciente_id = $1::uuid
                      OR (d.paciente_id_externo IS NOT NULL
                          AND (d.paciente_id_externo = $2 OR d.paciente_id_externo = $3))
                   ORDER BY d.created_at DESC""",
                patient_id,
                patient["numero_documento"],
                patient.get("historia_clinica") or "",
            )
            return [dict(row) for row in rows]
    except Exception as exc:
        raise _database_failure("listar los documentos del paciente", exc) from exc


async def get_unlinked_documents() -> list[dict[str, Any]]:
    """Lista exclusivamente documentos reales aún no vinculados."""
    pool = await _require_pool()
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT id, documento_id, tipo_documento, tipo_archivo,
                          paciente_nombre, created_at
                   FROM documentos_triaje
                   WHERE paciente_id IS NULL
                   ORDER BY created_at DESC LIMIT 50"""
            )
            return [dict(row) for row in rows]
    except Exception as exc:
        raise _database_failure("listar documentos sin asociar", exc) from exc


async def associate_document_to_patient(patient_id: str, documento_id: str) -> bool:
    """Vincula un documento existente; nunca crea expedientes placeholder."""
    pool = await _require_pool()
    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """UPDATE documentos_triaje
                   SET paciente_id = $1::uuid, updated_at = NOW()
                   WHERE documento_id = $2 OR id::text = $2""",
                patient_id,
                documento_id.strip(),
            )
            return result != "UPDATE 0"
    except Exception as exc:
        raise _database_failure("asociar el documento al paciente", exc) from exc
