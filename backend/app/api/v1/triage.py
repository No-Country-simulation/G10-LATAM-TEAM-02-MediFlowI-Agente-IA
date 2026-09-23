"""
MediFlow — Endpoint POST /triage

Endpoint principal del agente. Recibe documentos clínicos y retorna
el resultado del triaje autónomo.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from pydantic import BaseModel, Field
from typing import Optional
import base64

from app.core.security import require_api_key
from app.core.config import get_settings, Settings
from app.services.triage_service import TriageService
from app.services.llm_service import LLMService
from app.repositories.oci_storage import OCIStorageRepository

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/triage", tags=["triage"])


# ── Modelos de Request/Response (manuales, complementan _generated/) ─────────

class DocumentoClinicoRequest(BaseModel):
    documento_id: str = Field(..., examples=["DOC-CLIN-2026-8942"])
    tipo_archivo: str = Field(..., pattern="^(PDF|IMAGEN|TEXTO|JSON)$")
    documento_texto: Optional[str] = None
    documento_base64: Optional[str] = None
    canal_origen: str = Field(default="", examples=["Guardia_Emergencias"])
    metadata: Optional[dict] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    summary="Procesar y clasificar documento clínico",
    status_code=status.HTTP_200_OK,
)
async def procesar_documento(
    payload: DocumentoClinicoRequest,
    response: Response,
    _auth: str = Depends(require_api_key),
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
        )
    except Exception as exc:
        logger.error("api.triage.error", documento_id=payload.documento_id, error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "ERROR_PROCESAMIENTO",
                "mensaje": "Error interno al procesar el documento.",
                "detalle": str(exc),
            },
        )

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
    _auth: str = Depends(require_api_key),
    settings: Settings = Depends(get_settings),
):
    """Variante del endpoint /triage que acepta upload de archivos binarios (PDF, imagen)."""
    contenido = await archivo.read()
    base64_content = base64.b64encode(contenido).decode("utf-8")

    tipo = "PDF" if archivo.content_type == "application/pdf" else "IMAGEN"

    llm_service = LLMService(settings=settings)
    oci_storage = OCIStorageRepository(settings=settings)
    triage_service = TriageService(settings=settings, llm_service=llm_service, oci_storage=oci_storage)

    resultado = await triage_service.procesar_documento(
        documento_id=documento_id,
        tipo_archivo=tipo,
        documento_base64=base64_content,
        canal_origen=canal_origen,
    )
    if resultado.decision_enrutamiento.requiere_auditoria_humana:
        response.status_code = status.HTTP_207_MULTI_STATUS
    return resultado.model_dump()
