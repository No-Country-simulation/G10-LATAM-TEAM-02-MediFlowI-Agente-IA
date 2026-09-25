"""
MediFlow — Endpoints GET /documents y PATCH /documents/{id}

Consulta de documentos procesados y registro de decisiones de auditoría humana (HITL).
"""

import json
import structlog
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import Optional, Literal

from app.core.security import require_current_user, require_roles
from app.core.config import get_settings, Settings
from app.repositories.oci_storage import OCIStorageRepository
from app.agent.state import AgentState, ClasificacionState

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


class DecisionAuditoriaRequest(BaseModel):
    decision: Literal["aprobar", "rechazar", "reclasificar"]
    nueva_clasificacion: Optional[dict] = None
    comentario: Optional[str] = None


@router.get("", summary="Listar documentos procesados")
async def listar_documentos(
    estado: Optional[str] = Query(None, pattern="^(procesado|pendiente_auditoria|error)$"),
    nivel_prioridad: Optional[str] = Query(None, pattern="^(Urgente|Rutina|Ambiguo)$"),
    limit: int = Query(default=20, le=100),
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """Lista documentos procesados desde PostgreSQL (o fallback a disco local si DB no está activa)."""
    from app.repositories.postgres_storage import PostgresStorageRepository
    pg = PostgresStorageRepository(settings=settings)
    await pg.inicializar()

    if pg.disponible:
        rows = await pg.listar(status=estado, nivel_prioridad=nivel_prioridad, limit=limit)
        formatted = []
        for r in rows:
            formatted.append({
                "status": r.get("status", "procesado"),
                "documento_id": r.get("documento_id"),
                "clasificacion": {
                    "tipo_documento": r.get("tipo_documento", "Documento Clínico"),
                    "especialidad": r.get("especialidad", "General"),
                    "nivel_prioridad": r.get("nivel_prioridad", "Rutina"),
                    "score_confianza_clasificacion": r.get("score_confianza", 0.95),
                },
                "datos_extraidos": {
                    "paciente": {"nombre": r.get("paciente_nombre"), "edad": r.get("paciente_edad")},
                    "medico_solicitante": {"nombre": r.get("medico_nombre"), "matricula": r.get("medico_matricula")},
                    "diagnostico_principal": r.get("diagnostico_principal"),
                    "cie10_sugerido": r.get("cie10_sugerido"),
                    "hallazgos_clave": json.loads(r["hallazgos_clave"]) if r.get("hallazgos_clave") and isinstance(r["hallazgos_clave"], str) else (r.get("hallazgos_clave") or []),
                },
                "decision_enrutamiento": {
                    "destino_principal": r.get("destino_principal", "Cola_Rutina"),
                    "requiere_auditoria_humana": r.get("requiere_auditoria_humana", False),
                    "justificacion_enrutamiento": r.get("justificacion_enrutamiento", ""),
                    "notificacion_generada": json.loads(r["notificacion_generada"]) if r.get("notificacion_generada") and isinstance(r["notificacion_generada"], str) else r.get("notificacion_generada"),
                },
                "almacenamiento_oci": {
                    "bucket": r.get("oci_bucket") or "mediflow-documentos-clinicos",
                    "ruta_objeto": r.get("oci_ruta_objeto") or f"procesados/{r.get('documento_id')}.json",
                    "status_backup": r.get("oci_status") or "exito",
                },
                "tiempo_procesamiento_ms": r.get("tiempo_procesamiento_ms", 35),
                "created_at": r.get("created_at").isoformat() if hasattr(r.get("created_at"), "isoformat") else (str(r.get("created_at")) if r.get("created_at") else None),
            })
        return {"total": len(formatted), "items": formatted}

    # Fallback a archivos en disco / OCI sólo si PostgreSQL NO está disponible
    oci = OCIStorageRepository(settings=settings)
    if nivel_prioridad == "Urgente":
        prefix = "procesados/urgentes/"
    elif nivel_prioridad == "Ambiguo" or estado == "pendiente_auditoria":
        prefix = "auditoria_humana/"
    else:
        prefix = "procesados/"

    claves = await oci.listar_documentos(prefix=prefix)
    documentos = []
    for clave in claves[:limit]:
        raw = await oci.obtener_documento(clave)
        if raw:
            try:
                doc = json.loads(raw)
                if estado and doc.get("status") != estado:
                    continue
                documentos.append(doc)
            except Exception:
                continue

    return {"total": len(documentos), "items": documentos}


@router.get("/{documento_id}", summary="Obtener documento por ID")
async def obtener_documento(
    documento_id: str,
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """Retorna el resultado de triaje de un documento específico."""
    oci = OCIStorageRepository(settings=settings)

    # Buscar en todas las rutas posibles
    for prefix in ["procesados/urgentes/", "procesados/rutina/", "auditoria_humana/"]:
        clave = f"{prefix}{documento_id}.json"
        raw = await oci.obtener_documento(clave)
        if raw:
            return json.loads(raw)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"error": "DOCUMENTO_NO_ENCONTRADO", "mensaje": f"No se encontró el documento '{documento_id}'."},
    )


@router.patch("/{documento_id}", summary="Registrar decisión de auditoría humana (HITL)")
async def registrar_decision_auditoria(
    documento_id: str,
    payload: DecisionAuditoriaRequest,
    current_user: dict = Depends(require_roles("AUDITOR", "ADMINISTRADOR")),
    settings: Settings = Depends(get_settings),
):
    """
    Permite a un auditor clínico aprobar, rechazar o reclasificar
    un documento derivado a auditoría humana.
    """
    oci = OCIStorageRepository(settings=settings)
    clave_original = f"auditoria_humana/{documento_id}.json"
    raw = await oci.obtener_documento(clave_original)

    if not raw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "DOCUMENTO_NO_ENCONTRADO", "mensaje": f"No se encontró '{documento_id}' en auditoría."},
        )

    doc = json.loads(raw)
    doc["auditoria"] = {
        "decision": payload.decision,
        "auditor_id": current_user["id"],
        "comentario": payload.comentario,
    }

    if payload.decision == "aprobar":
        doc["status"] = "procesado"
        doc["decision_enrutamiento"]["requiere_auditoria_humana"] = False
        # Mover a procesados/rutina/
        nueva_clave = f"procesados/rutina/{documento_id}.json"
        await oci.guardar_documento(nueva_clave, json.dumps(doc, ensure_ascii=False))

    elif payload.decision == "reclasificar" and payload.nueva_clasificacion:
        doc["clasificacion"].update(payload.nueva_clasificacion)
        doc["status"] = "procesado"
        await oci.guardar_documento(clave_original, json.dumps(doc, ensure_ascii=False))

    else:  # rechazar
        doc["status"] = "error"
        await oci.guardar_documento(clave_original, json.dumps(doc, ensure_ascii=False))

    logger.info(
        "api.auditoria.decision_registrada",
        documento_id=documento_id,
        decision=payload.decision,
        auditor=current_user["id"],
    )
    return doc
