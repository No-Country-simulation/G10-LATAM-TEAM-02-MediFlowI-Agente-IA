"""
MediFlow — Servicio LLM.

Abstracción sobre el cliente LLM que permite cambiar entre
Google Gemini, OpenAI u otros sin modificar los nodos del agente.
"""

import structlog
from app.core.config import Settings

logger = structlog.get_logger(__name__)


class LLMService:
    """
    Servicio unificado de LLM.
    Prioridad: Google Gemini → OpenAI (fallback) → Mock (dev sin credenciales).
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = None
        self._provider = None
        self._inicializar()

    def _inicializar(self):
        """Inicializa el cliente LLM disponible según configuración."""
        if self._settings.google_api_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                self._client = ChatGoogleGenerativeAI(
                    model=self._settings.gemini_model,
                    google_api_key=self._settings.google_api_key,
                    temperature=0.1,  # Baja temperatura para extracción estructurada
                )
                self._provider = "gemini"
                logger.info("llm.inicializado", provider="gemini", model=self._settings.gemini_model)
                return
            except Exception as exc:
                logger.warning("llm.gemini.fallo", error=str(exc))

        if self._settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                self._client = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=self._settings.openai_api_key,
                    temperature=0.1,
                )
                self._provider = "openai"
                logger.info("llm.inicializado", provider="openai")
                return
            except Exception as exc:
                logger.warning("llm.openai.fallo", error=str(exc))

        # Sin credenciales: modo mock (solo para desarrollo)
        self._provider = "mock"
        logger.warning("llm.modo_mock", razon="Sin credenciales configuradas")

    async def completar(self, prompt: str) -> str:
        """
        Envía un prompt al LLM y retorna la respuesta como string.

        Args:
            prompt: Texto del prompt a enviar

        Returns:
            Texto de respuesta del LLM

        Raises:
            RuntimeError: Si el LLM no está disponible
        """
        if self._provider == "mock":
            return self._respuesta_mock(prompt)

        from langchain_core.messages import HumanMessage
        respuesta = await self._client.ainvoke([HumanMessage(content=prompt)])
        return respuesta.content

    def _respuesta_mock(self, prompt: str) -> str:
        """Mock de respuesta LLM para desarrollo sin credenciales."""
        import json
        prompt_lower = prompt.lower()
        is_extraction = "extrae" in prompt_lower or "diagnostico_principal" in prompt_lower

        # Extraer únicamente el cuerpo del documento para evitar falsos positivos
        # con palabras como 'urgente' o 'emergencias' presentes en las instrucciones del prompt
        cuerpo = prompt_lower
        if "texto del documento:" in prompt_lower:
            cuerpo = prompt_lower.split("texto del documento:")[1]
        elif "documento a analizar:" in prompt_lower:
            cuerpo = prompt_lower.split("documento a analizar:")[1]

        # Caso 3: Ambiguo / ilegible
        if any(w in cuerpo for w in ["ilegible", "ambiguo", "???"]):
            if is_extraction:
                return json.dumps({
                    "paciente": {"nombre": None, "edad": None, "id_paciente": None},
                    "medico_solicitante": {"nombre": None, "matricula": None},
                    "estudio_realizado": None,
                    "diagnostico_principal": None,
                    "cie10_sugerido": None,
                    "hallazgos_clave": ["Texto fragmentado o ilegible"],
                })
            return json.dumps({
                "tipo_documento": "Otro",
                "especialidad": None,
                "nivel_prioridad": "Ambiguo",
                "razon_prioridad": "Texto con baja legibilidad e información insuficiente",
            })

        # Caso 2: Urgencia (TEP / emergencia / crítico)
        if any(w in cuerpo for w in ["tep", "tromboembolismo", "urgente", "crítico", "critico", "guardia_emergencias"]):
            if is_extraction:
                return json.dumps({
                    "paciente": {"nombre": "Carlos Eduardo Mendes", "edad": 52, "id_paciente": "PAC-8942"},
                    "medico_solicitante": {"nombre": "Dra. Renata Silveira", "matricula": "145892"},
                    "estudio_realizado": "Tomografía de Tórax con contraste",
                    "diagnostico_principal": "Tromboembolismo Pulmonar Agudo (TEP)",
                    "cie10_sugerido": "I26.9",
                    "hallazgos_clave": ["Defecto de llenado en arteria pulmonar", "TEP agudo detectado", "Correlación clínica urgente"],
                })
            return json.dumps({
                "tipo_documento": "Informe de Estudio por Imagenes",
                "especialidad": "Radiología / Neumonología",
                "nivel_prioridad": "Urgente",
                "razon_prioridad": "Hallazgo de TEP agudo con compromiso vascular urgente detectado",
            })

        # Caso 1 / Default: Rutina
        if is_extraction:
            return json.dumps({
                "paciente": {"nombre": "Ana García", "edad": 35, "id_paciente": "PAC-0001"},
                "medico_solicitante": {"nombre": "Dr. Roberto López", "matricula": "98231"},
                "estudio_realizado": "Hemograma completo",
                "diagnostico_principal": "Analítica normal sin hallazgos patológicos",
                "cie10_sugerido": "Z00.0",
                "hallazgos_clave": ["Parámetros hematológicos normales"],
            })
        return json.dumps({
            "tipo_documento": "Analítica de Laboratorio",
            "especialidad": "Medicina General",
            "nivel_prioridad": "Rutina",
            "razon_prioridad": "Analítica normal sin hallazgos de alarma",
        })

    @property
    def disponible(self) -> bool:
        return self._provider != "mock"

    @property
    def proveedor(self) -> str:
        return self._provider or "desconocido"
