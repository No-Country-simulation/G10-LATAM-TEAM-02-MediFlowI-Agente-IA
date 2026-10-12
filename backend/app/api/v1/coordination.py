"""MediFlow — Router de Coordinación y Auditoría Médica (HITL).

Endpoints protegidos exclusivos para roles COORDINADOR y ADMINISTRADOR
para la supervisión, resolución médica de triajes retenidos y consulta de trazabilidad.
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import require_roles
from app.repositories.audit_repository import AuditRepository
from app.repositories.postgres_storage import DatabaseUnavailableError
from app.schemas.coordination import (
    AuditEventItemResponse,
    PendingTriageItemResponse,
    ResolveTriageRequest,
    ResolveTriageResponse,
)

logger = structlog.get_logger(__name__)

router = APIRouter(
    prefix="/coordination",
    tags=["Coordinación y Auditoría Médica (HITL)"],
    dependencies=[Depends(require_roles("COORDINADOR", "ADMINISTRADOR"))],
)


@router.get(
    "/pending",
    response_model=list[PendingTriageItemResponse],
    summary="Bandeja de triajes pendientes de auditoría HITL",
    description="Retorna la lista de triajes retenidos que requieren revisión médica humana.",
)
async def obtener_pendientes(
    especialidad: Annotated[str | None, Query(description="Filtro opcional por especialidad")] = None,
    minutos_espera: Annotated[int | None, Query(ge=0, description="Filtro por tiempo mínimo de espera")] = None,
    limit: Annotated[int, Query(ge=1, le=100, description="Límite de resultados")] = 50,
    offset: Annotated[int, Query(ge=0, description="Desplazamiento de paginación")] = 0,
) -> list[PendingTriageItemResponse]:
    """Consulta los documentos de triaje pendientes de resolución HITL."""
    try:
        rows = await AuditRepository.obtener_triajes_pendientes(
            especialidad=especialidad,
            minutos_espera=minutos_espera,
            limit=limit,
            offset=offset,
        )
        return [PendingTriageItemResponse.model_validate(r) for r in rows]
    except DatabaseUnavailableError as exc:
        logger.error("coordination.pending.db_unavailable", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL no está disponible para consultar la bandeja de pendientes.",
        ) from exc


@router.post(
    "/resolve/{documento_id}",
    response_model=ResolveTriageResponse,
    summary="Resolución médica de triaje HITL",
    description="Registra el dictamen médico formal, reasignación y justificación clínica de un caso en revisión.",
)
async def resolver_triaje(
    documento_id: str,
    payload: ResolveTriageRequest,
    current_user: dict = Depends(require_roles("COORDINADOR", "ADMINISTRADOR")),
) -> ResolveTriageResponse:
    """Registra la resolución médica inmutable de un triaje retenido."""
    try:
        resultado = await AuditRepository.resolver_triaje(
            documento_id=documento_id,
            coordinador_id=current_user.get("id"),
            decision=payload.decision.value,
            justificacion=payload.justificacion_clinica,
            categoria_destino=payload.categoria_destino,
            prioridad_sugerida=payload.prioridad_sugerida,
        )
        return ResolveTriageResponse.model_validate(resultado)
    except ValueError as exc:
        logger.warning("coordination.resolve.not_found", documento_id=documento_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Documento de triaje no encontrado: {documento_id}",
        ) from exc
    except DatabaseUnavailableError as exc:
        logger.error("coordination.resolve.db_unavailable", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL no está disponible para persistir la resolución médica.",
        ) from exc


@router.get(
    "/audit/{documento_id}",
    response_model=list[AuditEventItemResponse],
    summary="Historial de eventos de trazabilidad del documento",
    description="Retorna la bitácora inmutable de eventos hospitalarios y auditorías para un documento.",
)
async def obtener_historial_auditoria(
    documento_id: str,
) -> list[AuditEventItemResponse]:
    """Consulta la cronología inmutable de eventos de un documento."""
    try:
        rows = await AuditRepository.obtener_eventos_documento(documento_id=documento_id)
        return [AuditEventItemResponse.model_validate(r) for r in rows]
    except DatabaseUnavailableError as exc:
        logger.error("coordination.audit.db_unavailable", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PostgreSQL no está disponible para consultar el historial de auditoría.",
        ) from exc
