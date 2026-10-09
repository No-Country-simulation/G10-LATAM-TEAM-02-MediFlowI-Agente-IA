"""
MediFlow — Módulo de Seguridad y Autenticación.

Maneja el hashing seguro de contraseñas con PBKDF2-HMAC-SHA256,
generación y validación de tokens de sesión y contraseñas.
"""

import bcrypt
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from fastapi import Depends, Header, HTTPException, status

from app.repositories.session_repository import (
    create_session,
    get_active_session_user,
    revoke_session,
)


def hash_password(password: str) -> tuple[str, str]:
    """
    Genera el hash bcrypt de una contraseña.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8"), salt.decode("utf-8")


def verify_password(password: str, stored_hash: str, salt: str = "") -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash almacenado."""
    return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))


async def create_access_token(user_data: dict, expires_delta_hours: int = 12) -> str:
    """Crea y persiste un token de acceso revocable para el usuario."""
    token = f"mf_session_{secrets.token_hex(32)}"
    expiration = datetime.now(UTC) + timedelta(hours=expires_delta_hours)
    await create_session(token, str(user_data["id"]), expiration)
    return token


async def verify_access_token(token: str) -> dict | None:
    """Valida en PostgreSQL un token activo y retorna su usuario."""
    return await get_active_session_user(token)


async def invalidate_access_token(token: str) -> bool:
    """Revoca una sesión persistida (logout)."""
    return await revoke_session(token)


async def require_api_key(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> str:
    """Verifica que la petición incluya una API key válida en la cabecera X-API-Key."""
    from app.core.config import get_settings

    settings = get_settings()

    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o no proporcionada en la cabecera X-API-Key.",
        )
    return x_api_key


async def require_current_user(
    authorization: str | None = Header(None),
) -> dict:
    """Retorna el usuario de una sesión Bearer activa o rechaza la solicitud."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer no proporcionado en la cabecera Authorization.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    try:
        user = await verify_access_token(token)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El servicio de autenticación no está disponible temporalmente.",
        ) from exc
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión no válida o expirada. Por favor, inicie sesión nuevamente.",
        )
    return user


def require_roles(*allowed_roles: str) -> Callable:
    """Crea una dependencia que exige uno de los roles indicados."""

    async def role_dependency(current_user: dict = Depends(require_current_user)) -> dict:
        if current_user.get("rol") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No cuenta con permisos para realizar esta acción.",
            )
        return current_user

    return role_dependency
