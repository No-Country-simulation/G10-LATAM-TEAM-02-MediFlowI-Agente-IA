"""
MediFlow — Endpoints de Configuración del Sistema (/api/v1/settings).

Permite consultar y cambiar la configuración activa (ej. modo de almacenamiento LOCAL u OCI).
Las preferencias se persisten en la base de datos PostgreSQL (tabla configuracion_sistema).
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings, Settings
from app.core.security import require_api_key

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])

_memoria_config: dict[str, str] = {"modo_almacenamiento": "LOCAL"}


class ConfigRequest(BaseModel):
    storage_mode: str = Field(..., pattern="^(LOCAL|OCI)$", description="Modo de almacenamiento: LOCAL u OCI")


class ConfigResponse(BaseModel):
    storage_mode: str
    oci_configured: bool
    llm_provider: str
    llm_configured: bool
    database_url_configured: bool


async def _obtener_modo_almacenamiento_db(settings: Settings) -> str:
    """Lee el modo de almacenamiento desde PostgreSQL o memoria local."""
    db_url = getattr(settings, "database_url", "")
    if db_url:
        try:
            import asyncpg
            url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            conn = await asyncpg.connect(url)
            val = await conn.fetchval(
                "SELECT valor FROM configuracion_sistema WHERE clave = 'modo_almacenamiento'"
            )
            await conn.close()
            if val:
                return val.upper()
        except Exception as exc:
            logger.warning("settings.db_read.fallback", error=str(exc))

    return _memoria_config.get("modo_almacenamiento", "LOCAL")


async def _guardar_modo_almacenamiento_db(settings: Settings, modo: str) -> None:
    """Guarda el modo de almacenamiento en PostgreSQL y memoria."""
    _memoria_config["modo_almacenamiento"] = modo
    db_url = getattr(settings, "database_url", "")
    if db_url:
        try:
            import asyncpg
            url = db_url.replace("postgresql+asyncpg://", "postgresql://")
            conn = await asyncpg.connect(url)
            await conn.execute(
                """
                INSERT INTO configuracion_sistema (clave, valor, descripcion, updated_at)
                VALUES ('modo_almacenamiento', $1, 'Modo de almacenamiento activo: LOCAL u OCI', NOW())
                ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor, updated_at = NOW()
                """,
                modo,
            )
            await conn.close()
            logger.info("settings.db_write.exito", modo=modo)
        except Exception as exc:
            logger.error("settings.db_write.error", error=str(exc))


@router.get("", response_model=ConfigResponse, summary="Obtener configuración del sistema")
async def obtener_configuracion(
    _auth: str = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
):
    modo = await _obtener_modo_almacenamiento_db(settings)
    from app.services.llm_service import LLMService
    llm_service = LLMService(settings)

    return ConfigResponse(
        storage_mode=modo,
        oci_configured=settings.oci_configured,
        llm_provider=llm_service.proveedor,
        llm_configured=settings.llm_configured,
        database_url_configured=bool(settings.database_url),
    )


@router.post("", response_model=ConfigResponse, summary="Actualizar configuración del sistema")
async def actualizar_configuracion(
    payload: ConfigRequest,
    _auth: str = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
):
    # Validación: Si se elige OCI, verificar que OCI esté configurado en .env
    if payload.storage_mode == "OCI" and not settings.oci_configured:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "OCI_NO_CONFIGURADO",
                "mensaje": (
                    "No se puede activar el modo OCI porque no están configuradas las credenciales "
                    "de Oracle Cloud (OCI_USER_OCID, OCI_TENANCY_OCID, OCI_NAMESPACE, etc.) en el archivo .env."
                ),
            },
        )

    await _guardar_modo_almacenamiento_db(settings, payload.storage_mode)

    from app.services.llm_service import LLMService
    llm_service = LLMService(settings)

    return ConfigResponse(
        storage_mode=payload.storage_mode,
        oci_configured=settings.oci_configured,
        llm_provider=llm_service.proveedor,
        llm_configured=settings.llm_configured,
        database_url_configured=bool(settings.database_url),
    )
