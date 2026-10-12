"""Esquemas Pydantic v2 para el módulo de Coordinación y Auditoría Médica (HITL)."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DecisionAuditoriaEnum(str, Enum):
    APROBAR = "aprobar"
    RECLASIFICAR = "reclasificar"
    RECHAZAR = "rechazar"


class ResolveTriageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: DecisionAuditoriaEnum = Field(
        ...,
        description="Decisión médica formal del coordinador (aprobar, reclasificar, rechazar)",
    )
    justificacion_clinica: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Justificación médica y criterio clínico para la resolución del caso",
        examples=["Se valida concordancia diagnóstica y se aprueba derivación a Cardiología"],
    )
    categoria_destino: str | None = Field(
        None,
        max_length=100,
        description="Nueva categoría o servicio clínico asignado si la decisión es reclasificar",
        examples=["Farmacia_Hospitalaria", "Observacion_Urgencias", "Cardiologia"],
    )
    prioridad_sugerida: str | None = Field(
        None,
        max_length=50,
        description="Ajuste de prioridad o nivel de urgencia clínico",
        examples=["ALTA", "MEDIA", "BAJA", "URGENTE", "RUTINA"],
    )


class ResolveTriageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    documento_id: str
    episodio_id: str | None = None
    coordinador_id: str
    decision: str
    justificacion_clinica: str
    nuevo_estado: str
    created_at: datetime
    mensaje: str = "Resolución médica registrada exitosamente."

    @field_validator("id", "episodio_id", "coordinador_id", mode="before")
    @classmethod
    def serialize_uuid(cls, v: Any) -> str | None:
        return str(v) if v is not None else None


class PendingTriageItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    documento_id: str
    episodio_id: str | None = None
    fecha_ingesta: datetime
    tiempo_espera_minutos: int = 0
    estado: str
    canal_origen: str = "Admision"
    especialidad_sugerida: str | None = None
    nivel_prioridad: str | None = None
    confianza_ia: float | None = None
    motivo_hitl: str | None = None
    diagnostico_preliminar: str | None = None
    codigo_cie10: str | None = None
    paciente: dict[str, Any] | None = None

    @field_validator("episodio_id", mode="before")
    @classmethod
    def serialize_uuid(cls, v: Any) -> str | None:
        return str(v) if v is not None else None


class AuditEventItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    documento_id: str
    episodio_id: str | None = None
    usuario_id: str | None = None
    evento: str
    descripcion: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    @field_validator("id", "episodio_id", "usuario_id", mode="before")
    @classmethod
    def serialize_uuid(cls, v: Any) -> str | None:
        return str(v) if v is not None else None
