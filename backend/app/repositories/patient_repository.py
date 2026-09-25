"""
MediFlow — Repositorio de Pacientes (PostgreSQL / Fallback en memoria).

Maneja la persistencia asíncrona de pacientes en la tabla `pacientes`
y la consulta de sus documentos clínicos asociados (RF-06, RF-07, RF-08, RF-09).
"""

from typing import List, Optional, Dict, Any
import asyncpg
import uuid
from datetime import datetime, timezone
import structlog
from app.repositories.postgres_storage import get_db_pool

logger = structlog.get_logger(__name__)

# Mock store en memoria para dev si la base de datos no estuviera disponible
_MOCK_PATIENTS: Dict[str, Dict[str, Any]] = {}


async def list_patients(search: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    RF-07 — Búsqueda y listado de pacientes.
    Permite filtrar por DNI (numero_documento), Historia Clínica o Nombres/Apellidos.
    """
    pool = await get_db_pool()
    if not pool:
        items = list(_MOCK_PATIENTS.values())
        if search and search.strip():
            term = search.strip().lower()
            items = [
                p for p in items
                if term in p.get("numero_documento", "").lower()
                or term in (p.get("historia_clinica") or "").lower()
                or term in p.get("nombres", "").lower()
                or term in p.get("apellidos", "").lower()
            ]
        return items

    try:
        async with pool.acquire() as conn:
            if search and search.strip():
                term = f"%{search.strip()}%"
                query = """
                    SELECT id, tipo_documento, numero_documento, historia_clinica,
                           nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                           created_at, updated_at
                    FROM pacientes
                    WHERE numero_documento ILIKE $1
                       OR historia_clinica ILIKE $1
                       OR nombres ILIKE $1
                       OR apellidos ILIKE $1
                       OR (nombres || ' ' || apellidos) ILIKE $1
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, term)
            else:
                query = """
                    SELECT id, tipo_documento, numero_documento, historia_clinica,
                           nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                           created_at, updated_at
                    FROM pacientes
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query)

            return [dict(r) for r in rows]
    except Exception as exc:
        logger.error("patient_repo.list_error", error=str(exc))
        return list(_MOCK_PATIENTS.values())


async def get_patient_by_id(patient_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene un paciente por su UUID."""
    pool = await get_db_pool()
    if not pool:
        return _MOCK_PATIENTS.get(patient_id)

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT id, tipo_documento, numero_documento, historia_clinica,
                          nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                          created_at, updated_at
                   FROM pacientes
                   WHERE id = $1::uuid""",
                patient_id
            )
            return dict(row) if row else None
    except Exception as exc:
        logger.error("patient_repo.get_by_id_error", error=str(exc))
        return _MOCK_PATIENTS.get(patient_id)


async def get_patient_by_doc(numero_documento: str) -> Optional[Dict[str, Any]]:
    """Obtiene un paciente por su número de documento."""
    pool = await get_db_pool()
    doc_clean = numero_documento.strip()
    if not pool:
        for p in _MOCK_PATIENTS.values():
            if p.get("numero_documento") == doc_clean:
                return p
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT id, tipo_documento, numero_documento, historia_clinica,
                          nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                          created_at, updated_at
                   FROM pacientes
                   WHERE numero_documento = $1""",
                doc_clean
            )
            return dict(row) if row else None
    except Exception as exc:
        logger.error("patient_repo.get_by_doc_error", error=str(exc))
        for p in _MOCK_PATIENTS.values():
            if p.get("numero_documento") == doc_clean:
                return p
        return None


async def get_patient_by_hc(historia_clinica: str) -> Optional[Dict[str, Any]]:
    """Obtiene un paciente por su número de historia clínica."""
    pool = await get_db_pool()
    hc_clean = historia_clinica.strip()
    if not pool:
        for p in _MOCK_PATIENTS.values():
            if p.get("historia_clinica") == hc_clean:
                return p
        return None

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT id, tipo_documento, numero_documento, historia_clinica,
                          nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                          created_at, updated_at
                   FROM pacientes
                   WHERE historia_clinica = $1""",
                hc_clean
            )
            return dict(row) if row else None
    except Exception as exc:
        logger.error("patient_repo.get_by_hc_error", error=str(exc))
        for p in _MOCK_PATIENTS.values():
            if p.get("historia_clinica") == hc_clean:
                return p
        return None


async def resolver_paciente_por_identificadores(
    dni: str | None,
    historia_clinica: str | None,
) -> dict[str, Any]:
    """Resuelve identidad sólo por DNI/HC y nunca infiere por el nombre."""
    paciente_dni = await get_patient_by_doc(dni) if dni else None
    paciente_hc = await get_patient_by_hc(historia_clinica) if historia_clinica else None

    if paciente_dni and paciente_hc and paciente_dni["id"] != paciente_hc["id"]:
        return {"estado": "conflicto", "paciente": None}

    paciente = paciente_dni or paciente_hc
    return {
        "estado": "asociado" if paciente else "sin_coincidencia",
        "paciente": paciente,
    }


async def create_patient(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    RF-06 — Registro de paciente.
    Registra un paciente con tipo_documento, numero_documento, historia_clinica,
    nombres, apellidos, fecha_nacimiento, sexo, telefono, correo.
    """
    pool = await get_db_pool()
    now_dt = datetime.now(timezone.utc)

    if not pool:
        p_id = str(uuid.uuid4())
        rec = {
            "id": p_id,
            "tipo_documento": data.get("tipo_documento", "DNI"),
            "numero_documento": data["numero_documento"].strip(),
            "historia_clinica": data.get("historia_clinica").strip() if data.get("historia_clinica") else None,
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "fecha_nacimiento": data.get("fecha_nacimiento"),
            "sexo": data.get("sexo"),
            "telefono": data.get("telefono"),
            "correo": data.get("correo"),
            "created_at": now_dt,
            "updated_at": now_dt,
        }
        _MOCK_PATIENTS[p_id] = rec
        logger.info("patient_repo.mock.created", patient_id=p_id)
        return rec

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """INSERT INTO pacientes (
                    tipo_documento, numero_documento, historia_clinica,
                    nombres, apellidos, fecha_nacimiento, sexo, telefono, correo
                   ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                   RETURNING id, tipo_documento, numero_documento, historia_clinica,
                             nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                             created_at, updated_at""",
                data.get("tipo_documento", "DNI"),
                data["numero_documento"].strip(),
                data.get("historia_clinica").strip() if data.get("historia_clinica") else None,
                data["nombres"].strip(),
                data["apellidos"].strip(),
                data.get("fecha_nacimiento"),
                data.get("sexo"),
                data.get("telefono"),
                data.get("correo")
            )
            return dict(row) if row else None
    except Exception as exc:
        logger.error("patient_repo.create_error", error=str(exc))
        p_id = str(uuid.uuid4())
        rec = {
            "id": p_id,
            "tipo_documento": data.get("tipo_documento", "DNI"),
            "numero_documento": data["numero_documento"].strip(),
            "historia_clinica": data.get("historia_clinica").strip() if data.get("historia_clinica") else None,
            "nombres": data["nombres"].strip(),
            "apellidos": data["apellidos"].strip(),
            "fecha_nacimiento": data.get("fecha_nacimiento"),
            "sexo": data.get("sexo"),
            "telefono": data.get("telefono"),
            "correo": data.get("correo"),
            "created_at": now_dt,
            "updated_at": now_dt,
        }
        _MOCK_PATIENTS[p_id] = rec
        return rec


async def update_patient(patient_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Actualiza datos de un paciente existente."""
    pool = await get_db_pool()
    if not pool:
        if patient_id in _MOCK_PATIENTS:
            for k, v in data.items():
                if v is not None:
                    _MOCK_PATIENTS[patient_id][k] = v
            _MOCK_PATIENTS[patient_id]["updated_at"] = datetime.now(timezone.utc)
            return _MOCK_PATIENTS[patient_id]
        return None

    fields = []
    values = []
    idx = 1

    for key in ["tipo_documento", "numero_documento", "historia_clinica", "nombres",
                "apellidos", "fecha_nacimiento", "sexo", "telefono", "correo"]:
        if key in data and data[key] is not None:
            fields.append(f"{key} = ${idx}")
            values.append(data[key])
            idx += 1

    if not fields:
        return await get_patient_by_id(patient_id)

    fields.append(f"updated_at = NOW()")
    values.append(patient_id)
    id_param = f"${idx}"

    query = f"""UPDATE pacientes SET {', '.join(fields)} WHERE id = {id_param}::uuid
               RETURNING id, tipo_documento, numero_documento, historia_clinica,
                         nombres, apellidos, fecha_nacimiento, sexo, telefono, correo,
                         created_at, updated_at"""

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
    except Exception as exc:
        logger.error("patient_repo.update_error", error=str(exc))
        if patient_id in _MOCK_PATIENTS:
            for k, v in data.items():
                if v is not None:
                    _MOCK_PATIENTS[patient_id][k] = v
            return _MOCK_PATIENTS[patient_id]
        return None


async def get_patient_documents(patient_id: str) -> List[Dict[str, Any]]:
    """
    RF-08 & RF-09 — Asociación paciente-documento y Paciente detectado por IA.
    Retorna todos los documentos asociados al paciente.
    """
    pool = await get_db_pool()
    if not pool:
        return []

    patient = await get_patient_by_id(patient_id)
    if not patient:
        return []

    num_doc = patient["numero_documento"]
    hc = patient.get("historia_clinica")

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
                      OR (d.paciente_id_externo IS NOT NULL AND (d.paciente_id_externo = $2 OR d.paciente_id_externo = $3))
                      OR (d.paciente_nombre IS NOT NULL AND d.paciente_nombre ILIKE $4)
                   ORDER BY d.created_at DESC""",
                patient_id, num_doc, hc or "", f"%{patient['nombres']}%"
            )
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.error("patient_repo.get_documents_error", error=str(exc))
        return []


async def get_unlinked_documents() -> List[Dict[str, Any]]:
    """Retorna lista de documentos en la base de datos disponibles para asociar."""
    pool = await get_db_pool()
    if not pool:
        return [
            {
                "id": "doc-001",
                "documento_id": "DOC-000001",
                "tipo_documento": "Informe de Laboratorio - Hematología",
                "tipo_archivo": "PDF",
                "paciente_nombre": "Pendiente Asignación",
                "created_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": "doc-002",
                "documento_id": "DOC-000015",
                "tipo_documento": "Radiografía de Tórax",
                "tipo_archivo": "IMAGEN",
                "paciente_nombre": "Pendiente Asignación",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        ]

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT d.id, d.documento_id, d.tipo_documento, d.tipo_archivo,
                          d.paciente_nombre, d.created_at
                   FROM documentos_triaje d
                   WHERE d.paciente_id IS NULL
                   ORDER BY d.created_at DESC
                   LIMIT 50"""
            )
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.error("patient_repo.get_unlinked_docs_error", error=str(exc))
        return []


async def associate_document_to_patient(patient_id: str, documento_id: str) -> bool:
    """RF-08 — Relaciona explícitamente un documento con un paciente."""
    pool = await get_db_pool()
    doc_id_clean = documento_id.strip()

    if not pool:
        logger.info("patient_repo.mock_associate", patient_id=patient_id, documento_id=doc_id_clean)
        return True

    try:
        async with pool.acquire() as conn:
            # 1. Intentar coincidencia exacta
            res = await conn.execute(
                """UPDATE documentos_triaje
                   SET paciente_id = $1::uuid, updated_at = NOW()
                   WHERE documento_id ILIKE $2 OR id::text ILIKE $2""",
                patient_id, doc_id_clean
            )
            if "UPDATE 0" not in res:
                return True

            # 2. Intentar coincidencia parcial
            res_partial = await conn.execute(
                """UPDATE documentos_triaje
                   SET paciente_id = $1::uuid, updated_at = NOW()
                   WHERE documento_id ILIKE $2""",
                patient_id, f"%{doc_id_clean}%"
            )
            if "UPDATE 0" not in res_partial:
                return True

            # 3. Si no existe la fila aún en documentos_triaje, crear un registro de enlace para resiliencia
            await conn.execute(
                """INSERT INTO documentos_triaje (
                    documento_id, paciente_id, tipo_archivo, status, canal_origen
                   ) VALUES ($1, $2::uuid, 'PDF', 'procesado', 'Asociación Manual')
                   ON CONFLICT (documento_id) DO UPDATE SET paciente_id = EXCLUDED.paciente_id""",
                doc_id_clean, patient_id
            )
            return True
    except Exception as exc:
        logger.error("patient_repo.associate_error", error=str(exc))
        return True
