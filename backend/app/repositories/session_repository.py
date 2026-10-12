"""Persistencia de sesiones revocables en PostgreSQL."""

import hashlib
from datetime import datetime
from typing import Any

from app.repositories.postgres_storage import get_db_pool


def token_digest(token: str) -> str:
    """Calcula el identificador irreversible usado para buscar una sesión."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_session(token: str, user_id: str, expires_at: datetime) -> None:
    """Registra una sesión sin persistir el token Bearer en texto claro."""
    pool = await get_db_pool()
    if pool is None:
        raise RuntimeError("PostgreSQL no está disponible para registrar la sesión.")

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO sesiones_usuario (token_hash, usuario_id, expires_at)
                   VALUES ($1, $2::uuid, $3)""",
                token_digest(token),
                user_id,
                expires_at,
            )
    except Exception as exc:
        raise RuntimeError("No fue posible registrar la sesión en PostgreSQL.") from exc


async def get_active_session_user(token: str) -> dict[str, Any] | None:
    """Obtiene el usuario activo asociado a un token vigente y no revocado."""
    if not token:
        return None

    pool = await get_db_pool()
    if pool is None:
        raise RuntimeError("PostgreSQL no está disponible para validar la sesión.")

    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT u.id, u.documento_identidad, u.nombres, u.apellidos,
                          u.correo, u.telefono, u.rol, u.estado
                   FROM sesiones_usuario s
                   JOIN usuarios u ON u.id = s.usuario_id
                   WHERE s.token_hash = $1
                     AND s.revoked_at IS NULL
                     AND s.expires_at > NOW()
                     AND u.estado = 'ACTIVO'""",
                token_digest(token),
            )
            if row is None:
                return None
            user = dict(row)
            user["id"] = str(user["id"])
            return user
    except Exception as exc:
        raise RuntimeError("No fue posible validar la sesión en PostgreSQL.") from exc


async def revoke_session(token: str) -> bool:
    """Revoca una sesión activa y devuelve si se modificó alguna fila."""
    if not token:
        return False

    pool = await get_db_pool()
    if pool is None:
        raise RuntimeError("PostgreSQL no está disponible para revocar la sesión.")

    try:
        async with pool.acquire() as conn:
            result = await conn.execute(
                """UPDATE sesiones_usuario
                   SET revoked_at = NOW()
                   WHERE token_hash = $1 AND revoked_at IS NULL""",
                token_digest(token),
            )
            return result != "UPDATE 0"
    except Exception as exc:
        raise RuntimeError("No fue posible revocar la sesión en PostgreSQL.") from exc
