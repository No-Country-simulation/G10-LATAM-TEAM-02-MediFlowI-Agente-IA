"""
MediFlow — Seguridad: validación de API Key.

Implementación simple de autenticación por cabecera X-API-Key.
Para producción, considerar JWT o OAuth2.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import get_settings

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(_api_key_header)) -> str:
    """
    Dependency de FastAPI que valida la API Key en cada request.

    Uso:
        @router.post("/triage")
        async def endpoint(deps: str = Depends(require_api_key)):
            ...
    """
    settings = get_settings()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "API_KEY_AUSENTE", "mensaje": "Se requiere la cabecera X-API-Key."},
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "API_KEY_INVALIDA", "mensaje": "La API Key proporcionada no es válida."},
        )

    return api_key
