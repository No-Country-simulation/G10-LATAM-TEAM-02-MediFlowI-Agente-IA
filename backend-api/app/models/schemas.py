"""
Modelos Pydantic v2 alineados 100% con specs/openapi.yaml y schemas/
"""
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class TipoArchivoEnum(str, Enum):
    PDF = "PDF"
    IMAGEN = "IMAGEN"
    TEXTO = "TEXTO"
    JSON = "JSON"


class NivelPrioridadEnum(str, Enum):
    Rutina = "Rutina"
    Prioritario = "Prioritario"
    Urgente = "Urgente"


class DestinoPrincipalEnum(str, Enum):
    Cola_Emergencia_Medica = "Cola_Emergencia_Medica"
    Cola_Auditoria_Humana = "Cola_Auditoria_Humana"
    Farmacia_Hospitalaria = "Farmacia_Hospitalaria"
    Historia_Clinica_Electronica = "Historia_Clinica_Electronica"
    Auditoria_Autorizaciones = "Auditoria_Autorizaciones"


class StatusTriajeEnum(str, Enum):
    procesado = "procesado"
    pendiente_auditoria = "pendiente_auditoria"
    error = "error"


class StatusBackupEnum(str, Enum):
    exito = "exito"
    pendiente = "pendiente"
    fallido = "fallido"


# --- Entradas ---
class DocumentoClinicoInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    documento_id: str = Field(..., description="ID único del documento", examples=["DOC-CLIN-2026-8942"])
    tipo_archivo: TipoArchivoEnum = Field(..., description="Tipo de archivo", examples=[TipoArchivoEnum.PDF])
    documento_texto: Optional[str] = Field(None, description="Contenido textual")
    documento_base64: Optional[str] = Field(None, description="Contenido base64 si es PDF o imagen")
    canal_origen: str = Field(..., description="Canal de procedencia", examples=["Guardia_Emergencias"])


# --- Entidades Clínicas ---
class Paciente(BaseModel):
    nombre: Optional[str] = None
    nome: Optional[str] = None
    edad: Optional[int] = None
    identificacion: Optional[str] = None

    @property
    def nombre_completo(self) -> str:
        return self.nombre or self.nome or "Desconocido"


class MedicoSolicitante(BaseModel):
    nombre: Optional[str] = None
    matricula: Optional[str] = None
    institucion: Optional[str] = None


class Medicamento(BaseModel):
    nombre: str
    dosis: Optional[str] = None
    frecuencia: Optional[str] = None


class DatosClinicosExtraidos(BaseModel):
    paciente: Paciente
    medico_solicitante: Optional[MedicoSolicitante] = None
    estudio_realizado: Optional[str] = None
    diagnostico_principal: str
    cie10_sugerido: Optional[str] = None
    medicamentos: Optional[List[Medicamento]] = None


# --- Clasificación y Enrutamiento ---
class ClasificacionDocumento(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    tipo_documento: str = Field(..., examples=["Informe de Estudio por Imagenes"])
    especialidad: str = Field(..., examples=["Radiologia / Neumonologia"])
    nivel_prioridad: NivelPrioridadEnum = Field(..., examples=[NivelPrioridadEnum.Urgente])
    score_confianza_clasificacion: float = Field(..., ge=0.0, le=1.0, examples=[0.99])


class NotificacionAlerta(BaseModel):
    canal: str
    mensaje: str


class DecisionEnrutamiento(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    destino_principal: DestinoPrincipalEnum
    requiere_auditoria_humana: bool
    justificacion_enrutamiento: str
    notificacion_generada: Optional[NotificacionAlerta] = None


class AlmacenamientoOCI(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    bucket: str = "mediflow-documentos-clinicos"
    ruta_objeto: str
    status_backup: StatusBackupEnum = StatusBackupEnum.exito


# --- Salida Final ---
class RespuestaTriaje(BaseModel):
    status: StatusTriajeEnum
    documento_id: str
    clasificacion: ClasificacionDocumento
    datos_extraidos: DatosClinicosExtraidos
    decision_enrutamiento: DecisionEnrutamiento
    almacenamiento_oci: AlmacenamientoOCI
