# AUTO-GENERADO desde specs/openapi.yaml. NO EDITAR.
# Ejecutar make generate.

from __future__ import annotations

from datetime import date
from typing import Any, Literal
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel, SecretStr


class ClasificacionFusionVision(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    tipo_documento: str = Field(..., min_length=1)
    especialidad: str | None = None
    nivel_prioridad: Literal['Urgente', 'Rutina', 'Ambiguo']
    razon_prioridad: str


class AlertaGuardia(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: UUID = Field(
        ...,
        description='Identificador de trazabilidad, también usado como id del evento SSE.',
    )
    documento_id: str
    episodio_id: UUID | None = None
    prioridad: Literal['Urgente', 'Rutina', 'Ambiguo'] | None = None
    fecha: AwareDatetime
    mensaje: str


class DistribucionPrioridadMetrics(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    Rojo: int = Field(..., description='Documentos Urgente; presentación roja.', ge=0)
    Amarillo: int = Field(
        ...,
        description='Documentos Ambiguo; incertidumbre documental, no gravedad intermedia.',
        ge=0,
    )
    Verde: int = Field(..., description='Documentos Rutina; presentación verde.', ge=0)


class TasaHitl(RootModel[float]):
    root: float = Field(
        ...,
        description='Porcentaje histórico 100*N/D, dos decimales con empate hacia arriba; null si D=0, cero si N=0 y D>0.',
        ge=0.0,
        le=100.0,
    )


class TiempoPromedioIaSegundos(RootModel[float]):
    root: float = Field(
        ...,
        description='Promedio del tiempo persistido admisible en segundos, tres decimales con empate hacia arriba; null sin tiempos, cero registrado válido; puede ser anterior/sintético, no promedio por nodo ni latencia HTTP.',
        ge=0.0,
    )


class MetricsResponse(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    distribucion_prioridad: DistribucionPrioridadMetrics
    tasa_hitl: TasaHitl | None = Field(
        ...,
        description='Porcentaje histórico 100*N/D, dos decimales con empate hacia arriba; null si D=0, cero si N=0 y D>0.',
    )
    tiempo_promedio_ia_segundos: TiempoPromedioIaSegundos | None = Field(
        ...,
        description='Promedio del tiempo persistido admisible en segundos, tres decimales con empate hacia arriba; null sin tiempos, cero registrado válido; puede ser anterior/sintético, no promedio por nodo ni latencia HTTP.',
    )


class DocumentoClinico(BaseModel):
    documento_id: str = Field(
        ...,
        description='Identificador único del documento',
        examples=['DOC-CLIN-2026-8942'],
    )
    tipo_archivo: Literal['PDF', 'IMAGEN', 'TEXTO', 'JSON'] = Field(
        ..., examples=['PDF']
    )
    documento_texto: str | None = Field(
        None,
        description='Contenido en texto plano (si ya está extraído)',
        examples=['HOSPITAL SANTA LUCIA - INFORME DE ESTUDIO RADIOLOGICO...'],
    )
    documento_base64: str | None = Field(
        None, description='Contenido del archivo en base64 (para PDF/imagen)'
    )
    canal_origen: str = Field(
        '',
        description='Sistema o canal que originó el documento',
        examples=['Guardia_Emergencias'],
    )
    metadata: dict[str, Any] | None = Field(
        None, description='Metadatos adicionales del documento'
    )


class PendingTriageItem(BaseModel):
    documento_id: str = Field(..., examples=['DOC-2026-0001'])
    episodio_id: UUID | None = None
    fecha_ingesta: AwareDatetime
    tiempo_espera_minutos: int | None = Field(None, examples=[25])
    estado: str = Field(..., examples=['pendiente_auditoria'])
    canal_origen: str | None = Field(None, examples=['Admision'])
    especialidad_sugerida: str | None = Field(None, examples=['Cardiologia'])
    nivel_prioridad: str | None = Field(None, examples=['Urgente'])
    confianza_ia: float | None = Field(None, examples=[0.42])
    motivo_hitl: str | None = None
    diagnostico_preliminar: str | None = None
    codigo_cie10: str | None = None
    paciente: dict[str, Any] | None = None


class ResolveTriageRequest(BaseModel):
    decision: Literal['aprobar', 'reclasificar', 'rechazar']
    justificacion_clinica: str = Field(..., max_length=2000, min_length=5)
    categoria_destino: str | None = None
    prioridad_sugerida: str | None = None


class ResolveTriageResponse(BaseModel):
    id: str
    documento_id: str
    episodio_id: str | None = None
    coordinador_id: str
    decision: str
    justificacion_clinica: str
    nuevo_estado: str
    created_at: AwareDatetime
    mensaje: str | None = None


class AuditEventItem(BaseModel):
    id: str
    documento_id: str
    episodio_id: str | None = None
    usuario_id: str | None = None
    evento: str
    descripcion: str
    metadata: dict[str, Any] | None = None
    created_at: AwareDatetime


class Paciente(BaseModel):
    nombre: str | None = Field(None, examples=['Carlos Eduardo Mendes'])
    edad: int | None = Field(None, examples=[52])
    id_paciente: str | None = None
    documento_identidad: str | None = None
    historia_clinica: str | None = None


class MedicoSolicitante(BaseModel):
    nombre: str | None = Field(None, examples=['Dra. Renata Silveira'])
    matricula: str | None = Field(None, examples=['145892'])


class MedicamentoPrescrito(BaseModel):
    medicamento: str = Field(
        ...,
        description='Nombre del fármaco prescrito (genérico o comercial).',
        examples=['Paracetamol'],
    )
    dosis: str | None = Field(
        None, description='Dosis administrada y unidad de medida.', examples=['500 mg']
    )
    frecuencia: str | None = Field(
        None,
        description='Pauta o intervalo de administración.',
        examples=['cada 8 horas'],
    )
    via_administracion: str | None = Field(
        None, description='Vía anatómica de administración.', examples=['oral']
    )


class Notificacion(BaseModel):
    canal: str = Field(..., examples=['Alerta_Guardia_Medica'])
    mensaje: str = Field(
        ..., examples=['ALERTA URGENTE: Informe crítico de TEP Agudo...']
    )


class DecisionEnrutamiento(BaseModel):
    destino_principal: Literal[
        'Cola_Emergencia_Medica',
        'Cola_Rutina',
        'Farmacia_Hospitalaria',
        'Cola_Auditoria_Humana',
        'Cola_Revision_Ambigua',
    ] = Field(..., examples=['Cola_Emergencia_Medica'])
    requiere_auditoria_humana: bool = Field(..., examples=[False])
    justificacion_enrutamiento: str = Field(
        ..., examples=['Hallazgo crítico de alta gravedad detectado.']
    )
    notificacion_generada: Notificacion | None = None


class AlmacenamientoOCI(BaseModel):
    bucket: str | None = Field(None, examples=['mediflow-documentos-clinicos'])
    ruta_objeto: str | None = Field(
        None, examples=['urgentes/DOC-CLIN-2026-8942/resultado.json']
    )
    archivo_original: str | None = None
    resultado_json: str | None = None
    nombre_original: str | None = None
    status_backup: Literal['exito', 'error', 'pendiente'] | None = Field(
        None, examples=['exito']
    )


class DecisionAuditoria(BaseModel):
    decision: Literal['aprobar', 'rechazar', 'reclasificar']
    nueva_clasificacion: dict[str, Any] | None = None
    datos_corregidos: dict[str, Any] | None = None
    comentario: str | None = None


class PrioridadTriaje(RootModel[Literal['Urgente', 'Rutina', 'Ambiguo']]):
    root: Literal['Urgente', 'Rutina', 'Ambiguo'] = Field(
        ...,
        description='Nivel de prioridad clínica asignado por el agente de triaje.\n- **Urgente**: requiere atención inmediata o enrutamiento a emergencias.\n- **Rutina**: flujo normal de procesamiento médico.\n- **Ambiguo**: documento ilegible o con baja confianza; deriva a auditoría humana (HITL).\n',
        examples=['Urgente'],
    )


class HealthResponse(BaseModel):
    status: Literal['ok', 'unavailable'] = Field(..., examples=['ok'])
    version: str = Field(..., examples=['1.0.0'])
    postgres_disponible: bool = Field(..., examples=[True])
    llm_disponible: bool | None = Field(None, examples=[True])
    oci_disponible: bool | None = Field(None, examples=[True])


class Usuario(BaseModel):
    id: UUID
    documento_identidad: str = Field(..., pattern='^\\d{8}$')
    nombres: str
    apellidos: str
    correo: str | None = None
    telefono: str | None = None
    rol: Literal['ADMINISTRADOR', 'OPERADOR', 'AUDITOR', 'SUPERVISOR']
    estado: Literal['ACTIVO', 'INACTIVO']
    created_at: str | None = None


class UsuarioCrear(BaseModel):
    documento_identidad: str = Field(..., pattern='^\\d{8}$')
    password: SecretStr = Field(..., min_length=12)
    nombres: str
    apellidos: str
    correo: str | None = None
    telefono: str | None = None
    rol: Literal['ADMINISTRADOR', 'OPERADOR', 'AUDITOR', 'SUPERVISOR'] = 'OPERADOR'
    estado: Literal['ACTIVO', 'INACTIVO'] = 'ACTIVO'


class ConfiguracionSistema(BaseModel):
    storage_mode: Literal['LOCAL', 'OCI']
    oci_configured: bool
    llm_provider: str
    llm_configured: bool
    database_url_configured: bool


class PacienteRegistrar(BaseModel):
    tipo_documento: Literal['DNI', 'CE', 'PASAPORTE']
    numero_documento: str
    historia_clinica: str | None = None
    nombres: str
    apellidos: str
    fecha_nacimiento: date | None = None
    sexo: Literal['M', 'F', 'OTRO'] | None = None
    telefono: str | None = None
    correo: str | None = None


class PacienteRegistrado(PacienteRegistrar):
    id: UUID
    nombre_completo: str
    created_at: str | None = None


class DiagnosticoEntidad(BaseModel):
    texto: str = Field(..., examples=['Tromboembolismo Pulmonar Agudo'])
    cie10: str | None = Field(None, examples=['I26.9'])
    es_principal: bool = False


class ProcedimientoEntidad(BaseModel):
    texto: str = Field(..., examples=['Tomografía de Tórax con contraste'])
    codigo: str | None = None


class MedicamentoEntidad(BaseModel):
    nombre: str = Field(..., examples=['Heparina'])
    dosis: str | None = Field(None, examples=['80 UI/kg'])
    frecuencia: str | None = Field(None, examples=['Infusión IV continua'])


class DetalleError(BaseModel):
    error: str
    mensaje: str | None = None
    detalle: str | None = None


class ValidationError(BaseModel):
    loc: list[str | int]
    msg: str
    type: str
    input: Any | None = None
    ctx: dict[str, Any] | None = None


class HTTPValidationError(BaseModel):
    detail: list[ValidationError]


class Clasificacion(BaseModel):
    tipo_documento: Literal[
        'Informe Clínico',
        'Evolución Clínica',
        'Epicrisis',
        'Receta Médica',
        'Orden Médica',
        'Orden de Procedimiento',
        'Solicitud de Interconsulta',
        'Informe de Laboratorio',
        'Informe de Estudio por Imágenes',
        'Informe Quirúrgico',
        'Consentimiento Informado',
        'Certificado Médico',
        'Referencia y Contrarreferencia',
        'Registro de Vacunación',
        'Otro',
        'Desconocido',
        'Error',
        'Documento Clínico',
    ] = Field(
        ...,
        description='Catálogo clínico más los valores de compatibilidad que devuelve actualmente la API: Desconocido (sin texto), Error (fallo de clasificación) y Documento Clínico (registro histórico sin tipo). No admite texto arbitrario.',
        examples=['Informe de Estudio por Imágenes'],
    )
    especialidad: str | None = Field(None, examples=['Radiologia / Neumonologia'])
    nivel_prioridad: PrioridadTriaje
    score_confianza_clasificacion: float = Field(..., examples=[0.99], ge=0.0, le=1.0)


class DatosExtraidos(BaseModel):
    paciente: Paciente | None = None
    medico_solicitante: MedicoSolicitante | None = None
    estudio_realizado: str | None = Field(
        None, examples=['Tomografia de Torax con contraste']
    )
    diagnostico_principal: str | None = Field(
        None, examples=['Tromboembolismo Pulmonar Agudo (TEP)']
    )
    cie10_sugerido: str | None = Field(None, examples=['I26.9'])
    cie10_descripcion: str | None = Field(
        None,
        description='Descripción nosológica del catálogo CIE-10 versionado, separada del diagnóstico original.',
        examples=['Embolia pulmonar sin mención de corazón pulmonar agudo'],
    )
    hallazgos_clave: list[str] | None = None
    medicamentos: list[MedicamentoPrescrito] | None = Field(
        None,
        description='Lista de medicamentos prescritos extraídos estructuradamente del documento.',
    )


class ResultadoTriaje(BaseModel):
    metodo_extraccion: (
        Literal['TEXT_EXTRACTION', 'MULTIMODAL_VISION', 'LOCAL_OCR', 'FALLBACK_AUDIT']
        | None
    ) = Field(
        None,
        description='Método registrado por la ingesta, también persistido en metadata.',
    )
    documento_base64: None = Field(
        None,
        description='El contenido binario se libera del estado al terminar ingesta; el original se conserva por el servicio de almacenamiento.',
    )
    status: Literal[
        'recibido',
        'procesando',
        'procesado',
        'pendiente_auditoria',
        'rechazado',
        'no_soportado',
        'error',
    ] = Field(..., examples=['procesado'])
    documento_id: str = Field(..., examples=['DOC-CLIN-2026-8942'])
    clasificacion: Clasificacion
    datos_extraidos: DatosExtraidos
    decision_enrutamiento: DecisionEnrutamiento
    almacenamiento_oci: AlmacenamientoOCI | None = None
    tiempo_procesamiento_ms: int | None = Field(None, examples=[1240])
    created_at: str | None = Field(
        None,
        description='Fecha de registro disponible al consultar documentos persistidos.',
    )


class EntidadesMedicas(BaseModel):
    diagnosticos: list[DiagnosticoEntidad] | None = Field(
        None, description='Lista de diagnósticos identificados en el documento'
    )
    procedimientos: list[ProcedimientoEntidad] | None = Field(
        None, description='Procedimientos o estudios médicos mencionados'
    )
    medicamentos: list[MedicamentoEntidad] | None = Field(
        None,
        description='Medicamentos mencionados con dosis y frecuencia cuando están disponibles',
    )
    hallazgos_criticos: list[str] | None = Field(
        None, description='Hallazgos marcados como críticos o urgentes por el agente'
    )
    score_ner: float | None = Field(
        None,
        description='Puntuación de confianza del proceso de extracción de entidades',
        examples=[0.87],
        ge=0.0,
        le=1.0,
    )


class ErrorResponse(BaseModel):
    detail: str | DetalleError


class ListaDocumentosResponse(BaseModel):
    total: int
    items: list[ResultadoTriaje]


class ResultadoFusionVision(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    texto_extraido: str = Field(..., min_length=1)
    datos_extraidos: DatosExtraidos
    clasificacion: ClasificacionFusionVision
