"""
MediFlow — Estado compartido del Agente LangGraph.

AgentState es el objeto que viaja a través de todos los nodos del grafo.
Cada nodo puede leer y escribir campos en este estado.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class PacienteState(BaseModel):
    nombre: Optional[str] = None
    edad: Optional[int] = None
    id_paciente: Optional[str] = None
    documento_identidad: Optional[str] = None
    historia_clinica: Optional[str] = None


class MedicoSolicitanteState(BaseModel):
    nombre: Optional[str] = None
    matricula: Optional[str] = None


class DatosExtraidosState(BaseModel):
    paciente: Optional[PacienteState] = None
    medico_solicitante: Optional[MedicoSolicitanteState] = None
    estudio_realizado: Optional[str] = None
    diagnostico_principal: Optional[str] = None
    cie10_sugerido: Optional[str] = None
    hallazgos_clave: list[str] = Field(default_factory=list)


class ClasificacionState(BaseModel):
    tipo_documento: Optional[str] = None
    especialidad: Optional[str] = None
    nivel_prioridad: Optional[Literal["Urgente", "Rutina", "Ambiguo"]] = None
    score_confianza_clasificacion: float = 0.0


class DecisionEnrutamientoState(BaseModel):
    destino_principal: Optional[Literal[
        "Cola_Emergencia_Medica",
        "Cola_Rutina",
        "Cola_Auditoria_Humana",
        "Cola_Revision_Ambigua",
    ]] = None
    requiere_auditoria_humana: bool = False
    justificacion_enrutamiento: Optional[str] = None
    notificacion_generada: Optional[dict] = None


class AlmacenamientoOCIState(BaseModel):
    bucket: Optional[str] = None
    ruta_objeto: Optional[str] = None
    archivo_original: Optional[str] = None
    resultado_json: Optional[str] = None
    nombre_original: Optional[str] = None
    status_backup: Literal["exito", "error", "pendiente"] = "pendiente"


class AgentState(BaseModel):
    """
    Estado global que fluye entre todos los nodos del grafo LangGraph.

    Estructura:
        Entrada  → [ingestion] → [extraction] → [classification]
                → [confidence] → [conditional_edge] → [routing]
                → Resultado final
    """

    # ── Datos de entrada ────────────────────────────────────────────────────
    documento_id: str
    tipo_archivo: str
    documento_texto: Optional[str] = None
    documento_base64: Optional[str] = None
    canal_origen: str = ""
    metadata: dict = Field(default_factory=dict)

    # ── Resultados por nodo ──────────────────────────────────────────────────
    texto_extraido: Optional[str] = None          # Nodo: ingestion
    datos_extraidos: DatosExtraidosState = Field(  # Nodo: extraction
        default_factory=DatosExtraidosState
    )
    clasificacion: ClasificacionState = Field(     # Nodo: classification + confidence
        default_factory=ClasificacionState
    )
    decision_enrutamiento: DecisionEnrutamientoState = Field(  # Nodo: routing
        default_factory=DecisionEnrutamientoState
    )
    almacenamiento_oci: AlmacenamientoOCIState = Field(
        default_factory=AlmacenamientoOCIState
    )

    # ── Control de flujo ─────────────────────────────────────────────────────
    status: Literal[
        "recibido",
        "procesando",
        "procesado",
        "pendiente_auditoria",
        "rechazado",
        "no_soportado",
        "error",
    ] = "recibido"
    error_mensaje: Optional[str] = None
    tiempo_procesamiento_ms: Optional[int] = None

    # ── Trazabilidad ─────────────────────────────────────────────────────────
    nodos_ejecutados: list[str] = Field(default_factory=list)
