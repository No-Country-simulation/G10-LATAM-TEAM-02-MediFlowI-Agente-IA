"""
MediFlow — API de Gestión de Pacientes (Módulo 2: RF-06, RF-07, RF-08, RF-09).

Maneja el registro, búsqueda, actualización y consulta del historial de
documentos asociados a un paciente.
"""

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, field_validator

from app.core.security import require_current_user
from app.repositories import patient_repository

router = APIRouter(prefix="/patients", tags=["Gestión de Pacientes"])


def _serialize_temporal(value: Any) -> str | None:
    """Serializa fechas/timestamps sin asumir que una columna opcional existe."""
    if value is None:
        return None
    isoformat = getattr(value, "isoformat", None)
    return str(isoformat()) if callable(isoformat) else str(value)


class PatientCreateRequest(BaseModel):
    tipo_documento: str = Field("DNI", description="Tipo de documento (DNI, CE, PASAPORTE)")
    numero_documento: str = Field(..., description="Número de documento de identidad")
    historia_clinica: str | None = Field(None, description="Número de historia clínica")
    nombres: str = Field(..., description="Nombres del paciente")
    apellidos: str = Field(..., description="Apellidos del paciente")
    fecha_nacimiento: str | None = Field(
        None, description="Fecha de nacimiento en formato YYYY-MM-DD"
    )
    sexo: str | None = Field(None, description="Sexo (M, F, OTRO; opcional)")
    telefono: str | None = Field(None, description="Teléfono de contacto")
    correo: str | None = Field(None, description="Correo electrónico")

    @field_validator("numero_documento")
    @classmethod
    def validate_numero_documento(cls, v: str) -> str:
        v_clean = v.strip()
        if not v_clean:
            raise ValueError("El número de documento no puede estar vacío.")
        return v_clean

    @field_validator("tipo_documento")
    @classmethod
    def validate_tipo_doc(cls, v: str) -> str:
        v_upper = v.upper().strip()
        if v_upper not in {"DNI", "CE", "PASAPORTE"}:
            raise ValueError("Tipo de documento no válido. Permitidos: DNI, CE, PASAPORTE.")
        return v_upper


class PatientUpdateRequest(BaseModel):
    tipo_documento: str | None = None
    numero_documento: str | None = None
    historia_clinica: str | None = None
    nombres: str | None = None
    apellidos: str | None = None
    fecha_nacimiento: str | None = None
    sexo: str | None = None
    telefono: str | None = None
    correo: str | None = None


@router.get("", summary="RF-07 — Búsqueda y listado de pacientes")
async def listar_pacientes(
    search: str | None = Query(
        None, description="Buscar por DNI, Historia Clínica o Nombres/Apellidos"
    ),
    _user: dict = Depends(require_current_user),
):
    """Retorna la lista de pacientes registrados con soporte para búsqueda (RF-07)."""
    patients = await patient_repository.list_patients(search=search)
    formatted = []
    for p in patients:
        formatted.append(
            {
                "id": str(p["id"]),
                "tipo_documento": p.get("tipo_documento", "DNI"),
                "numero_documento": p.get("numero_documento"),
                "historia_clinica": p.get("historia_clinica"),
                "nombres": p.get("nombres"),
                "apellidos": p.get("apellidos"),
                "nombre_completo": f"{p.get('nombres')} {p.get('apellidos')}",
                "fecha_nacimiento": str(p.get("fecha_nacimiento"))
                if p.get("fecha_nacimiento")
                else None,
                "sexo": p.get("sexo"),
                "telefono": p.get("telefono"),
                "correo": p.get("correo"),
                "created_at": _serialize_temporal(p.get("created_at")),
            }
        )
    return {"total": len(formatted), "items": formatted}


@router.get("/unlinked-documents", summary="Obtener lista de documentos disponibles para asociar")
async def listar_documentos_disponibles(
    _user: dict = Depends(require_current_user),
):
    """Retorna los documentos clínicos disponibles para vincular a un paciente."""
    docs = await patient_repository.get_unlinked_documents()
    formatted = []
    for d in docs:
        formatted.append(
            {
                "id": str(d.get("id")),
                "documento_id": d.get("documento_id"),
                "tipo_documento": d.get("tipo_documento") or "Documento Clínico",
                "tipo_archivo": d.get("tipo_archivo") or "PDF",
                "paciente_nombre": d.get("paciente_nombre") or "Pendiente Asignación",
                "created_at": _serialize_temporal(d.get("created_at")),
            }
        )
    return {"total": len(formatted), "items": formatted}


@router.post("", summary="RF-06 — Registro de nuevo paciente", status_code=status.HTTP_201_CREATED)
async def registrar_paciente(
    payload: PatientCreateRequest,
    _user: dict = Depends(require_current_user),
):
    """RF-06: Registra un nuevo paciente en la base de datos (PostgreSQL)."""
    existing = await patient_repository.get_patient_by_doc(payload.numero_documento)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un paciente registrado con el número de documento {payload.numero_documento}.",
        )

    if payload.historia_clinica:
        existing_hc = await patient_repository.get_patient_by_hc(payload.historia_clinica)
        if existing_hc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un paciente con la Historia Clínica {payload.historia_clinica}.",
            )

    try:
        f_nac = date.fromisoformat(payload.fecha_nacimiento) if payload.fecha_nacimiento else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha_nacimiento inválido. Utilice AAAA-MM-DD.",
        ) from None

    created = await patient_repository.create_patient(
        {
            "tipo_documento": payload.tipo_documento,
            "numero_documento": payload.numero_documento,
            "historia_clinica": payload.historia_clinica,
            "nombres": payload.nombres,
            "apellidos": payload.apellidos,
            "fecha_nacimiento": f_nac,
            "sexo": payload.sexo,
            "telefono": payload.telefono,
            "correo": payload.correo,
        }
    )

    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar el paciente en la base de datos.",
        )

    return {
        "message": "Paciente registrado exitosamente.",
        "paciente": {
            "id": str(created["id"]),
            "tipo_documento": created["tipo_documento"],
            "numero_documento": created["numero_documento"],
            "historia_clinica": created.get("historia_clinica"),
            "nombres": created["nombres"],
            "apellidos": created["apellidos"],
            "nombre_completo": f"{created['nombres']} {created['apellidos']}",
            "fecha_nacimiento": str(created.get("fecha_nacimiento"))
            if created.get("fecha_nacimiento")
            else None,
            "sexo": created.get("sexo"),
            "telefono": created.get("telefono"),
            "correo": created.get("correo"),
            "created_at": _serialize_temporal(created.get("created_at")),
        },
    }


@router.get("/{id}", summary="Obtener detalle de paciente")
async def obtener_paciente(
    id: str,
    _user: dict = Depends(require_current_user),
):
    """Consulta los datos detallados de un paciente por su ID."""
    patient = await patient_repository.get_patient_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró el paciente con ID {id}."
        )

    return {
        "id": str(patient["id"]),
        "tipo_documento": patient.get("tipo_documento"),
        "numero_documento": patient.get("numero_documento"),
        "historia_clinica": patient.get("historia_clinica"),
        "nombres": patient.get("nombres"),
        "apellidos": patient.get("apellidos"),
        "nombre_completo": f"{patient.get('nombres')} {patient.get('apellidos')}",
        "fecha_nacimiento": str(patient.get("fecha_nacimiento"))
        if patient.get("fecha_nacimiento")
        else None,
        "sexo": patient.get("sexo"),
        "telefono": patient.get("telefono"),
        "correo": patient.get("correo"),
        "created_at": _serialize_temporal(patient.get("created_at")),
    }


@router.put("/{id}", summary="Actualizar paciente")
async def actualizar_paciente(
    id: str,
    payload: PatientUpdateRequest,
    _user: dict = Depends(require_current_user),
):
    """Actualiza la información de un paciente."""
    existing = await patient_repository.get_patient_by_id(id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Paciente con ID {id} no encontrado."
        )

    data = payload.model_dump(exclude_unset=True)
    if "fecha_nacimiento" in data and data["fecha_nacimiento"]:
        try:
            data["fecha_nacimiento"] = date.fromisoformat(data["fecha_nacimiento"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de fecha_nacimiento inválido. Use AAAA-MM-DD.",
            ) from None

    updated = await patient_repository.update_patient(id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La actualización no fue confirmada por PostgreSQL.",
        )
    return {
        "message": "Paciente actualizado exitosamente.",
        "paciente": {
            "id": str(updated["id"]),
            "tipo_documento": updated.get("tipo_documento"),
            "numero_documento": updated.get("numero_documento"),
            "historia_clinica": updated.get("historia_clinica"),
            "nombres": updated.get("nombres"),
            "apellidos": updated.get("apellidos"),
            "nombre_completo": f"{updated.get('nombres')} {updated.get('apellidos')}",
            "fecha_nacimiento": str(updated.get("fecha_nacimiento"))
            if updated.get("fecha_nacimiento")
            else None,
            "sexo": updated.get("sexo"),
            "telefono": updated.get("telefono"),
            "correo": updated.get("correo"),
        },
    }


@router.get("/{id}/documents", summary="RF-08 & RF-09 — Historial de documentos del paciente")
async def listar_documentos_paciente(
    id: str,
    _user: dict = Depends(require_current_user),
):
    """
    RF-08 — Retorna el árbol/lista de documentos clínicos asociados al paciente.
    RF-09 — Incluye los datos extraídos por la IA (nombre, edad, DNI/HC).
    """
    patient = await patient_repository.get_patient_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró el paciente con ID {id}."
        )

    docs = await patient_repository.get_patient_documents(id)
    formatted_docs = []
    for d in docs:
        formatted_docs.append(
            {
                "id": str(d["id"]),
                "documento_id": d.get("documento_id"),
                "tipo_archivo": d.get("tipo_archivo"),
                "canal_origen": d.get("canal_origen"),
                "status": d.get("status"),
                "tipo_documento": d.get("tipo_documento"),
                "especialidad": d.get("especialidad"),
                "nivel_prioridad": d.get("nivel_prioridad"),
                "score_confianza": d.get("score_confianza"),
                "datos_extraidos_ia": {
                    "nombre_detectado": d.get("paciente_nombre"),
                    "edad_detectada": d.get("paciente_edad"),
                    "dni_hc_detectado": d.get("paciente_id_externo"),
                    "medico_nombre": d.get("medico_nombre"),
                    "diagnostico": d.get("diagnostico_principal"),
                    "cie10": d.get("cie10_sugerido"),
                },
                "destino_principal": d.get("destino_principal"),
                "created_at": _serialize_temporal(d.get("created_at")),
            }
        )

    return {
        "paciente_id": id,
        "nombre_completo": f"{patient['nombres']} {patient['apellidos']}",
        "numero_documento": patient["numero_documento"],
        "historia_clinica": patient.get("historia_clinica"),
        "total_documentos": len(formatted_docs),
        "documentos": formatted_docs,
    }


@router.post(
    "/{id}/documents/{documento_id}/associate", summary="RF-08 — Asociar documento a paciente"
)
async def asociar_documento(
    id: str,
    documento_id: str,
    _user: dict = Depends(require_current_user),
):
    """RF-08: Asocia manualmente un documento clínico a un paciente."""
    patient = await patient_repository.get_patient_by_id(id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Paciente {id} no encontrado."
        )

    success = await patient_repository.associate_document_to_patient(id, documento_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el documento {documento_id}; no se creó ninguna asociación ficticia.",
        )

    return {"message": f"Documento {documento_id} asociado exitosamente al paciente."}
