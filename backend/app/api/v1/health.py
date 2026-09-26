"""MediFlow — Health check endpoint."""

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.repositories.postgres_storage import get_db_pool

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado del servicio", include_in_schema=True)
async def health_check():
    """Verifica que el servicio está operativo y sus dependencias disponibles."""
    settings = get_settings()
    pool = await get_db_pool()
    postgres_disponible = False
    if pool is not None:
        try:
            async with pool.acquire() as connection:
                postgres_disponible = await connection.fetchval("SELECT 1") == 1
        except Exception:
            postgres_disponible = False

    payload = {
        "status": "ok" if postgres_disponible else "unavailable",
        "version": settings.app_version,
        "postgres_disponible": postgres_disponible,
        "llm_disponible": settings.llm_configured,
        "oci_disponible": settings.oci_configured,
    }
    if not postgres_disponible:
        return JSONResponse(status_code=503, content=payload)
    return payload
