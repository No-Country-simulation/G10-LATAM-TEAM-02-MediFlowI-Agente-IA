"""
MediFlow — Módulo de Seguridad y Autenticación.

Maneja el hashing seguro de contraseñas con PBKDF2-HMAC-SHA256,
generación y validación de tokens de sesión y contraseñas.
"""

import hashlib
import os
import secrets
from typing import Callable, Dict, Optional, Tuple
from datetime import datetime, timezone, timedelta
from fastapi import Depends, Header, HTTPException, status

# Tokens simples en memoria para sesiones activas (o JWT fallback)
_ACTIVE_SESSIONS: Dict[str, dict] = {}


def generate_salt() -> str:
    """Genera un salt aleatorio en formato hexadecimal (32 caracteres)."""
    return secrets.token_hex(16)


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Genera el hash PBKDF2-HMAC-SHA256 de una contraseña.
    Retorna la tupla (password_hash, salt).
    """
    if not salt:
        salt = generate_salt()
    
    password_bytes = password.encode('utf-8')
    salt_bytes = salt.encode('utf-8')
    
    dk = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
    return dk.hex(), salt


def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifica si una contraseña en texto plano coincide con el hash almacenado."""
    calculated_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calculated_hash, stored_hash)


def create_access_token(user_data: dict, expires_delta_hours: int = 12) -> str:
    """Crea un token de acceso seguro para la sesión del usuario."""
    token = f"mf_session_{secrets.token_hex(32)}"
    expiration = datetime.now(timezone.utc) + timedelta(hours=expires_delta_hours)
    
    _ACTIVE_SESSIONS[token] = {
        "user": user_data,
        "expires_at": expiration
    }
    return token


def verify_access_token(token: str) -> Optional[dict]:
    """Valida un token de sesión activo. Retorna los datos del usuario o None."""
    if not token or token not in _ACTIVE_SESSIONS:
        return None
    
    session = _ACTIVE_SESSIONS[token]
    if datetime.now(timezone.utc) > session["expires_at"]:
        del _ACTIVE_SESSIONS[token]
        return None
    
    return session["user"]


def invalidate_access_token(token: str) -> bool:
    """Invalida/destruye una sesión activa (Logout)."""
    if token in _ACTIVE_SESSIONS:
        del _ACTIVE_SESSIONS[token]
        return True
    return False


async def require_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key_query: Optional[str] = None
) -> str:
    """Verifica que la petición incluya una API key válida."""
    from app.core.config import get_settings
    settings = get_settings()
    
    key = x_api_key or api_key_query
    if not key or key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida o no proporcionada en la cabecera X-API-Key."
        )
    return key


async def require_current_user(
    authorization: Optional[str] = Header(None),
) -> dict:
    """Retorna el usuario de una sesión Bearer activa o rechaza la solicitud."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer no proporcionado en la cabecera Authorization.",
        )

    token = authorization.removeprefix("Bearer ").strip()
    user = verify_access_token(token)
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
