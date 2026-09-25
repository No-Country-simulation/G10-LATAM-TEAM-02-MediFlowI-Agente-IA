"""
MediFlow — Estado compartido del Agente LangGraph.

AgentState es el objeto que viaja a través de todos los nodos del grafo.
Cada nodo puede leer y escribir campos en este estado.
"""

from typing import Literal

from pydantic import BaseModel, Field


class PacienteState(BaseModel):
    nombre: str | None = None
    edad: int | None = None
    id_paciente: str | None = None
    documento_identidad: str | None = None
    historia_clinica: str | None = None


class MedicoSolicitanteState(BaseModel):
    nombre: str | None = None
    matricula: str | None = None


class DatosExtraidosState(BaseModel):
    paciente: PacienteState | None = None
    medico_solicitante: MedicoSolicitanteState | None = None
    estudio_realizado: str | None = None
    diagnostico_principal: str | None = None
    cie10_sugerido: str | None = None
    hallazgos_clave: list[str] = Field(default_factory=list)


class ClasificacionState(BaseModel):
    tipo_documento: str | None = None
    especialidad: str | None = None
    nivel_prioridad: Literal["Urgente", "Rutina", "Ambiguo"] | None = None
    score_confianza_clasificacion: float = 0.0


class DecisionEnrutamientoState(BaseModel):
    destino_principal: (
        Literal[
            "Cola_Emergencia_Medica",
            "Cola_Rutina",
            "Cola_Auditoria_Humana",
            "Cola_Revision_Ambigua",
        ]
        | None
    ) = None
    requiere_auditoria_humana: bool = False
    justificacion_enrutamiento: str | None = None
    notificacion_generada: dict | None = None


class AlmacenamientoOCIState(BaseModel):
    bucket: str | None = None
    ruta_objeto: str | None = None
    archivo_original: str | None = None
    resultado_json: str | None = None
    nombre_original: str | None = None
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
    documento_texto: str | None = None
    documento_base64: str | None = None
    canal_origen: str = ""
    metadata: dict = Field(default_factory=dict)

    # ── Resultados por nodo ──────────────────────────────────────────────────
    texto_extraido: str | None = None  # Nodo: ingestion
    datos_extraidos: DatosExtraidosState = Field(  # Nodo: extraction
        default_factory=DatosExtraidosState
    )
    clasificacion: ClasificacionState = Field(  # Nodo: classification + confidence
        default_factory=ClasificacionState
    )
    decision_enrutamiento: DecisionEnrutamientoState = Field(  # Nodo: routing
        default_factory=DecisionEnrutamientoState
    )
    almacenamiento_oci: AlmacenamientoOCIState = Field(default_factory=AlmacenamientoOCIState)

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
    error_mensaje: str | None = None
    tiempo_procesamiento_ms: int | None = None

    # ── Trazabilidad ─────────────────────────────────────────────────────────
    nodos_ejecutados: list[str] = Field(default_factory=list)
