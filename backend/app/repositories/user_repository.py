"""
MediFlow — Repositorio de Usuarios (PostgreSQL).

Maneja la persistencia asíncrona de usuarios en la tabla `usuarios`
con asyncpg.
"""

from typing import Any

from app.repositories.postgres_storage import DatabaseUnavailableError, get_db_pool


async def _require_pool():
    pool = await get_db_pool()
    if pool is None:
        raise DatabaseUnavailableError("PostgreSQL no está disponible para gestionar usuarios.")
    return pool


async def get_user_by_document(documento_identidad: str) -> dict[str, Any] | None:
    """Consulta un usuario por su número de documento de identidad (8 cifras)."""
    pool = await _require_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT id, documento_identidad, password_hash, salt, nombres, apellidos, 
                      correo, telefono, rol, estado, created_at, updated_at
               FROM usuarios
               WHERE documento_identidad = $1""",
            documento_identidad,
        )
        return dict(row) if row else None


async def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    """Consulta un usuario por su UUID."""
    pool = await _require_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT id, documento_identidad, nombres, apellidos, 
                      correo, telefono, rol, estado, created_at, updated_at
               FROM usuarios
               WHERE id = $1::uuid""",
            user_id,
        )
        return dict(row) if row else None


async def list_all_users() -> list[dict[str, Any]]:
    """Retorna el listado completo de usuarios registrados."""
    pool = await _require_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, documento_identidad, nombres, apellidos, 
                      correo, telefono, rol, estado, created_at, updated_at
               FROM usuarios
               ORDER BY created_at DESC"""
        )
        return [dict(r) for r in rows]


async def create_user(
    documento_identidad: str,
    password_hash: str,
    salt: str,
    nombres: str,
    apellidos: str,
    correo: str | None,
    telefono: str | None,
    rol: str,
    estado: str = "ACTIVO",
) -> dict[str, Any] | None:
    """Registra un nuevo usuario en la base de datos."""
    pool = await _require_pool()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO usuarios 
               (documento_identidad, password_hash, salt, nombres, apellidos, correo, telefono, rol, estado)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8::rol_enum, $9::estado_usuario_enum)
               RETURNING id, documento_identidad, nombres, apellidos, correo, telefono, rol, estado, created_at""",
            documento_identidad,
            password_hash,
            salt,
            nombres,
            apellidos,
            correo,
            telefono,
            rol,
            estado,
        )
        return dict(row) if row else None


async def update_user(
    user_id: str,
    nombres: str | None = None,
    apellidos: str | None = None,
    correo: str | None = None,
    telefono: str | None = None,
    rol: str | None = None,
    estado: str | None = None,
    password_hash: str | None = None,
    salt: str | None = None,
) -> dict[str, Any] | None:
    """Actualiza datos, rol o estado de un usuario existente."""
    pool = await _require_pool()

    async with pool.acquire() as conn:
        # Construcción dinámica de consulta UPDATE
        set_clauses = ["updated_at = NOW()"]
        params = [user_id]
        param_idx = 2

        if nombres is not None:
            set_clauses.append(f"nombres = ${param_idx}")
            params.append(nombres)
            param_idx += 1

        if apellidos is not None:
            set_clauses.append(f"apellidos = ${param_idx}")
            params.append(apellidos)
            param_idx += 1

        if correo is not None:
            set_clauses.append(f"correo = ${param_idx}")
            params.append(correo)
            param_idx += 1

        if telefono is not None:
            set_clauses.append(f"telefono = ${param_idx}")
            params.append(telefono)
            param_idx += 1

        if rol is not None:
            set_clauses.append(f"rol = ${param_idx}::rol_enum")
            params.append(rol)
            param_idx += 1

        if estado is not None:
            set_clauses.append(f"estado = ${param_idx}::estado_usuario_enum")
            params.append(estado)
            param_idx += 1

        if password_hash is not None and salt is not None:
            set_clauses.append(f"password_hash = ${param_idx}")
            params.append(password_hash)
            param_idx += 1
            set_clauses.append(f"salt = ${param_idx}")
            params.append(salt)
            param_idx += 1

        query = f"""UPDATE usuarios 
                   SET {", ".join(set_clauses)}
                   WHERE id = $1::uuid
                   RETURNING id, documento_identidad, nombres, apellidos, correo, telefono, rol, estado, updated_at"""

        row = await conn.fetchrow(query, *params)
        return dict(row) if row else None
