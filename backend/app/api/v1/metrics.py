"""API-04: observación agregada autenticada de documentos de triaje."""

from fastapi import APIRouter, Depends

from app._generated.models import MetricsResponse
from app.core.openapi import error_responses
from app.core.security import require_current_user
from app.repositories import metrics_repository

router = APIRouter(prefix="/metrics", tags=["metrics"], responses=error_responses(401, 503))


@router.get("", response_model=MetricsResponse, summary="Consultar métricas agregadas de documentos de triaje")
async def obtener_metricas_triaje(_current_user: dict = Depends(require_current_user)) -> MetricsResponse:
    """Cualquier sesión activa; errores de autenticación y DB conservan su handler."""
    return await metrics_repository.obtener_metricas()
