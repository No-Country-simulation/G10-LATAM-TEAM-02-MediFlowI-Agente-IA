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
        if "extrae" in prompt.lower() or "paciente" in prompt.lower():
            return json.dumps({
                "paciente": {"nombre": "Mock Paciente", "edad": 40, "id_paciente": None},
                "medico_solicitante": {"nombre": None, "matricula": None},
                "estudio_realizado": "Estudio Mock",
                "diagnostico_principal": None,
                "cie10_sugerido": None,
                "hallazgos_clave": [],
            })
        return json.dumps({
            "tipo_documento": "Analítica de Laboratorio",
            "especialidad": "Medicina General",
            "nivel_prioridad": "Rutina",
            "razon_prioridad": "Mock automático",
        })

    @property
    def disponible(self) -> bool:
        return self._provider != "mock"

    @property
    def proveedor(self) -> str:
        return self._provider or "desconocido"
