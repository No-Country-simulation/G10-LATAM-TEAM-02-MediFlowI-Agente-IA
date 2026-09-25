"""
MediFlow — Endpoint POST /triage

Endpoint principal del agente. Recibe documentos clínicos y retorna
el resultado del triaje autónomo.
"""

import base64

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings
from app.core.security import require_current_user
from app.repositories.oci_storage import OCIStorageRepository, StoragePersistenceError
from app.repositories.postgres_storage import DatabaseUnavailableError
from app.services.llm_service import LLMService, LLMUnavailableError
from app.services.triage_service import TriageService

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/triage", tags=["triage"])
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_UPLOAD_MIME_TYPES = {"application/pdf", "image/jpeg", "image/jpg", "image/png"}


def _detectar_tipo_archivo(contenido: bytes) -> str | None:
    """Detecta PDF/imagen mediante firmas binarias, sin confiar sólo en Content-Type."""
    if contenido.startswith(b"%PDF-"):
        return "PDF"
    if contenido.startswith(b"\x89PNG\r\n\x1a\n"):
        return "IMAGEN"
    if contenido.startswith(b"\xff\xd8\xff"):
        return "IMAGEN"
    return None


# ── Modelos de Request/Response (manuales, complementan _generated/) ─────────


class DocumentoClinicoRequest(BaseModel):
    documento_id: str = Field(..., examples=["DOC-CLIN-2026-8942"])
    tipo_archivo: str = Field(..., pattern="^(PDF|IMAGEN|TEXTO|JSON)$")
    documento_texto: str | None = None
    documento_base64: str | None = None
    canal_origen: str = Field(default="", examples=["Guardia_Emergencias"])
    metadata: dict | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "",
    summary="Procesar y clasificar documento clínico",
    status_code=status.HTTP_200_OK,
)
async def procesar_documento(
    payload: DocumentoClinicoRequest,
    response: Response,
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """
    Endpoint principal del agente MediFlow.

    Recibe un documento clínico, ejecuta el grafo LangGraph y retorna
    el resultado de triaje con clasificación, entidades extraídas y
    decisión de enrutamiento.

    **Casos de prueba obligatorios:**
    - Caso 1 (Rutina): analítica normal → `Cola_Rutina`
    - Caso 2 (Urgente): TEP agudo → `Cola_Emergencia_Medica` + alerta
    - Caso 3 (Ambiguo): documento ilegible → `Cola_Auditoria_Humana`
    """
    logger.info("api.triage.request", documento_id=payload.documento_id)

    # Inicializar servicios (en producción usar DI con singleton)
    llm_service = LLMService(settings=settings)
    oci_storage = OCIStorageRepository(settings=settings)
    triage_service = TriageService(
        settings=settings,
        llm_service=llm_service,
        oci_storage=oci_storage,
    )

    try:
        resultado = await triage_service.procesar_documento(
            documento_id=payload.documento_id,
            tipo_archivo=payload.tipo_archivo,
            documento_texto=payload.documento_texto,
            documento_base64=payload.documento_base64,
            canal_origen=payload.canal_origen,
            metadata=payload.metadata,
            usuario_registro_id=_current_user["id"],
        )
    except DatabaseUnavailableError as exc:
        logger.error(
            "api.triage.postgres_no_disponible", documento_id=payload.documento_id, error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "POSTGRES_NO_DISPONIBLE",
                "mensaje": "No se pudo persistir el documento en PostgreSQL.",
            },
        ) from exc
    except StoragePersistenceError as exc:
        logger.error(
            "api.triage.storage_no_disponible", documento_id=payload.documento_id, error=str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ALMACENAMIENTO_NO_DISPONIBLE",
                "mensaje": "El resultado se registró, pero no se pudo persistir el archivo físico.",
            },
        ) from exc
    except LLMUnavailableError as exc:
        logger.error(
            "api.triage.llm_no_disponible",
            documento_id=payload.documento_id,
            error=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM_NO_DISPONIBLE",
                "mensaje": "No hay un proveedor LLM configurado para ejecutar el triaje.",
            },
        ) from exc
    except Exception as exc:
        logger.error("api.triage.error", documento_id=payload.documento_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ERROR_PROCESAMIENTO",
                "mensaje": "Error interno al procesar el documento.",
                "detalle": str(exc),
            },
        ) from exc

    # Código 207 si requiere auditoría humana
    if resultado.decision_enrutamiento.requiere_auditoria_humana:
        response.status_code = status.HTTP_207_MULTI_STATUS
    else:
        response.status_code = status.HTTP_200_OK

    return resultado.model_dump()


@router.post(
    "/upload",
    summary="Procesar documento clínico desde archivo",
    status_code=status.HTTP_200_OK,
)
async def procesar_documento_upload(
    response: Response,
    documento_id: str = Form(...),
    canal_origen: str = Form(default=""),
    archivo: UploadFile = File(...),
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """Variante del endpoint /triage que acepta upload de archivos binarios (PDF, imagen)."""
    if archivo.content_type not in ALLOWED_UPLOAD_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "TIPO_NO_PERMITIDO",
                "mensaje": "Sólo se permiten archivos PDF, JPG y PNG.",
            },
        )

    contenido = await archivo.read(MAX_UPLOAD_SIZE + 1)
    if not contenido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "ARCHIVO_VACIO", "mensaje": "El archivo enviado está vacío."},
        )
    if len(contenido) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error": "ARCHIVO_DEMASIADO_GRANDE",
                "mensaje": "El archivo supera el límite de 10 MB.",
            },
        )

    tipo = _detectar_tipo_archivo(contenido)
    if tipo is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "CONTENIDO_NO_PERMITIDO",
                "mensaje": "El contenido no corresponde a un PDF, JPG o PNG válido.",
            },
        )
    if (archivo.content_type == "application/pdf") != (tipo == "PDF"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail={
                "error": "MIME_INCONSISTENTE",
                "mensaje": "El tipo declarado no coincide con el contenido del archivo.",
            },
        )

    base64_content = base64.b64encode(contenido).decode("utf-8")

    llm_service = LLMService(settings=settings)
    oci_storage = OCIStorageRepository(settings=settings)
    triage_service = TriageService(
        settings=settings, llm_service=llm_service, oci_storage=oci_storage
    )

    try:
        resultado = await triage_service.procesar_documento(
            documento_id=documento_id,
            tipo_archivo=tipo,
            documento_base64=base64_content,
            canal_origen=canal_origen,
            nombre_original=archivo.filename,
            usuario_registro_id=_current_user["id"],
        )
    except DatabaseUnavailableError as exc:
        logger.error("api.triage.postgres_no_disponible", documento_id=documento_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "POSTGRES_NO_DISPONIBLE",
                "mensaje": "No se pudo persistir el documento en PostgreSQL.",
            },
        ) from exc
    except StoragePersistenceError as exc:
        logger.error("api.triage.storage_no_disponible", documento_id=documento_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ALMACENAMIENTO_NO_DISPONIBLE",
                "mensaje": "El resultado se registró, pero no se pudo persistir el archivo físico.",
            },
        ) from exc
    except LLMUnavailableError as exc:
        logger.error(
            "api.triage.llm_no_disponible",
            documento_id=documento_id,
            error=str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "LLM_NO_DISPONIBLE",
                "mensaje": "No hay un proveedor LLM configurado para ejecutar el triaje.",
            },
        ) from exc
    except Exception as exc:
        logger.error("api.triage.upload_error", documento_id=documento_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ERROR_PROCESAMIENTO",
                "mensaje": "Error interno al procesar el documento.",
            },
        ) from exc
    if resultado.decision_enrutamiento.requiere_auditoria_humana:
        response.status_code = status.HTTP_207_MULTI_STATUS
    return resultado.model_dump()
