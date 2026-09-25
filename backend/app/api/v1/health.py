"""MediFlow — Health check endpoint."""

from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado del servicio", include_in_schema=True)
async def health_check():
    """Verifica que el servicio está operativo y sus dependencias disponibles."""
    settings = get_settings()
    return {
        "status": "ok",
        "version": settings.app_version,
        "llm_disponible": settings.llm_configured,
        "oci_disponible": settings.oci_configured,
    }
