"""
MediFlow — Endpoints GET /documents y PATCH /documents/{id}

Consulta de documentos procesados y registro de decisiones de auditoría humana (HITL).
"""

from typing import Literal

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.core.security import require_current_user, require_roles
from app.repositories.postgres_storage import PostgresStorageRepository

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"])


class DecisionAuditoriaRequest(BaseModel):
    decision: Literal["aprobar", "rechazar", "reclasificar"]
    nueva_clasificacion: dict | None = None
    datos_corregidos: dict | None = None
    comentario: str | None = None


def _as_json_value(value, default):
    """Normaliza columnas JSONB y valores serializados usados por datos históricos."""
    if value is None:
        return default
    if not isinstance(value, str):
        return value
    try:
        import json

        return json.loads(value)
    except (TypeError, ValueError):
        return default


def _serialize_temporal(value) -> str | None:
    """Serializa timestamps opcionales provenientes de asyncpg."""
    if value is None:
        return None
    isoformat = getattr(value, "isoformat", None)
    return str(isoformat()) if callable(isoformat) else str(value)


def _format_document_row(row: dict) -> dict:
    """Convierte una fila canónica de PostgreSQL al contrato público de triaje."""
    if isinstance(row.get("clasificacion"), dict):
        return dict(row)

    created_at = _serialize_temporal(row.get("created_at"))

    return {
        "status": row.get("status") or "pendiente_auditoria",
        "documento_id": row.get("documento_id"),
        "tipo_archivo": row.get("tipo_archivo"),
        "canal_origen": row.get("canal_origen") or "",
        "texto_extraido": row.get("texto_extraido") or "",
        "nombre_archivo": row.get("nombre_original"),
        "clasificacion": {
            "tipo_documento": row.get("tipo_documento") or "Documento Clínico",
            "especialidad": row.get("especialidad") or "General",
            "nivel_prioridad": row.get("nivel_prioridad") or "Rutina",
            "score_confianza_clasificacion": row.get("score_confianza") or 0,
        },
        "datos_extraidos": {
            "paciente": {
                "nombre": row.get("paciente_nombre"),
                "edad": row.get("paciente_edad"),
                "documento_identidad": row.get("paciente_id_externo"),
            },
            "medico_solicitante": {
                "nombre": row.get("medico_nombre"),
                "matricula": row.get("medico_matricula"),
            },
            "estudio_realizado": row.get("estudio_realizado"),
            "diagnostico_principal": row.get("diagnostico_principal"),
            "cie10_sugerido": row.get("cie10_sugerido"),
            "hallazgos_clave": _as_json_value(row.get("hallazgos_clave"), []),
        },
        "decision_enrutamiento": {
            "destino_principal": row.get("destino_principal") or "Cola_Rutina",
            "requiere_auditoria_humana": bool(row.get("requiere_auditoria_humana")),
            "justificacion_enrutamiento": (row.get("justificacion_enrutamiento") or ""),
            "notificacion_generada": _as_json_value(row.get("notificacion_generada"), None),
        },
        "almacenamiento_oci": {
            "bucket": row.get("oci_bucket"),
            "ruta_objeto": row.get("oci_ruta_objeto"),
            "status_backup": row.get("oci_status") or "pendiente",
            "archivo_original": row.get("archivo_original"),
            "resultado_json": row.get("resultado_json"),
            "nombre_original": row.get("nombre_original"),
            "proveedor": row.get("storage_provider"),
        },
        "nodos_ejecutados": _as_json_value(row.get("nodos_ejecutados"), []),
        "metadata": _as_json_value(row.get("metadata"), {}),
        "error_mensaje": row.get("error_mensaje"),
        "tiempo_procesamiento_ms": row.get("tiempo_procesamiento_ms") or 0,
        "created_at": created_at,
    }


def _aplicar_correcciones(doc: dict, payload: DecisionAuditoriaRequest) -> None:
    """Aplica al resultado persistido únicamente los campos editables por HITL."""
    nueva_clasificacion = payload.nueva_clasificacion or {}
    clasificacion = doc.setdefault("clasificacion", {})
    for campo in ("tipo_documento", "especialidad", "nivel_prioridad"):
        if nueva_clasificacion.get(campo) is not None:
            clasificacion[campo] = nueva_clasificacion[campo]

    if nueva_clasificacion.get("destino") is not None:
        doc.setdefault("decision_enrutamiento", {})["destino_principal"] = nueva_clasificacion[
            "destino"
        ]

    correcciones = payload.datos_corregidos or {}
    datos = doc.setdefault("datos_extraidos", {})
    paciente = correcciones.get("paciente") or {}
    if paciente:
        destino_paciente = datos.setdefault("paciente", {})
        if paciente.get("nombre") is not None:
            destino_paciente["nombre"] = paciente["nombre"]
        if paciente.get("dni") is not None:
            destino_paciente["documento_identidad"] = paciente["dni"]
        if paciente.get("edad") not in (None, ""):
            destino_paciente["edad"] = int(paciente["edad"])

    medico = correcciones.get("medico") or {}
    if medico:
        destino_medico = datos.setdefault("medico_solicitante", {})
        if medico.get("nombre") is not None:
            destino_medico["nombre"] = medico["nombre"]
        if medico.get("cmp") is not None:
            destino_medico["matricula"] = medico["cmp"]

    if correcciones.get("diagnostico") is not None:
        datos["diagnostico_principal"] = correcciones["diagnostico"]
    if correcciones.get("cie10") is not None:
        datos["cie10_sugerido"] = correcciones["cie10"]


@router.get("", summary="Listar documentos procesados")
async def listar_documentos(
    estado: str | None = Query(None, pattern="^(procesado|pendiente_auditoria|error)$"),
    nivel_prioridad: str | None = Query(None, pattern="^(Urgente|Rutina|Ambiguo)$"),
    limit: int = Query(default=20, le=100),
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """Lista documentos procesados desde la fuente única de verdad PostgreSQL."""
    pg = PostgresStorageRepository(settings=settings)
    rows = await pg.listar(status=estado, nivel_prioridad=nivel_prioridad, limit=limit)
    formatted = [_format_document_row(row) for row in rows]
    return {"total": len(formatted), "items": formatted}


@router.get("/{documento_id}/historial", summary="Consultar trazabilidad funcional del documento")
async def obtener_historial_documento(
    documento_id: str,
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """Retorna los eventos de recepción, procesamiento y auditoría del documento."""
    pg = PostgresStorageRepository(settings=settings)
    eventos = await pg.listar_historial(documento_id)
    return {"documento_id": documento_id, "items": eventos}


@router.get("/{documento_id}", summary="Obtener documento por ID")
async def obtener_documento(
    documento_id: str,
    _current_user: dict = Depends(require_current_user),
    settings: Settings = Depends(get_settings),
):
    """Retorna el resultado canónico persistido en PostgreSQL."""
    pg = PostgresStorageRepository(settings=settings)
    row = await pg.obtener_por_id(documento_id)
    if row:
        return _format_document_row(row)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "DOCUMENTO_NO_ENCONTRADO",
            "mensaje": f"No se encontró el documento '{documento_id}'.",
        },
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
    pg = PostgresStorageRepository(settings=settings)
    current_row = await pg.obtener_por_id(documento_id)
    if not current_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "DOCUMENTO_NO_ENCONTRADO",
                "mensaje": f"No se encontró el documento '{documento_id}'.",
            },
        )
    if current_row.get("status") != "pendiente_auditoria":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DOCUMENTO_NO_PENDIENTE",
                "mensaje": "El documento ya no está pendiente de auditoría humana.",
            },
        )

    registered = await pg.registrar_auditoria(
        documento_id=documento_id,
        decision=payload.decision,
        auditor_id=current_user["id"],
        comentario=payload.comentario,
        nueva_clasificacion=payload.nueva_clasificacion,
        datos_corregidos=payload.datos_corregidos,
    )
    if not registered:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "DOCUMENTO_NO_ENCONTRADO"},
        )

    updated_row = await pg.obtener_por_id(documento_id)
    if not updated_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "DOCUMENTO_NO_ENCONTRADO"},
        )
    doc = _format_document_row(updated_row)
    doc["auditoria"] = {
        "decision": payload.decision,
        "auditor_id": current_user["id"],
        "comentario": payload.comentario,
    }

    logger.info(
        "api.auditoria.decision_registrada",
        documento_id=documento_id,
        decision=payload.decision,
        auditor=current_user["id"],
    )
    return doc
