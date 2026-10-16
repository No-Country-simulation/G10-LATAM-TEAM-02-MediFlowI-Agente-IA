"""
MediFlow — Servicio LLM.

Abstracción sobre el cliente LLM que permite cambiar entre
Google Gemini, OpenAI u otros sin modificar los nodos del agente.
"""

from typing import Any

import structlog

from app.core.config import Settings

logger = structlog.get_logger(__name__)


class LLMUnavailableError(RuntimeError):
    """No existe un proveedor LLM real disponible para procesar documentos."""


class LLMService:
    """
    Servicio unificado de LLM.
    Prioridad: Google Gemini → OpenAI. El mock requiere habilitación explícita.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = None
        self._provider = None
        self._inicializar()

    def _inicializar(self):
        """Inicializa el cliente LLM disponible según configuración."""
        g_key = self._settings.google_api_key
        if g_key and not g_key.startswith("your-"):
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI

                self._client = ChatGoogleGenerativeAI(
                    model=self._settings.gemini_model,
                    google_api_key=g_key,
                    temperature=0.1,  # Baja temperatura para extracción estructurada
                )
                self._provider = "gemini"
                logger.info(
                    "llm.inicializado", provider="gemini", model=self._settings.gemini_model
                )
                return
            except Exception as exc:
                logger.warning("llm.gemini.fallo", error=str(exc))

        o_key = self._settings.openai_api_key
        if o_key and not o_key.startswith("your-"):
            try:
                from langchain_openai import ChatOpenAI

                self._client = ChatOpenAI(
                    model="gpt-4o-mini",
                    api_key=o_key,
                    temperature=0.1,
                )
                self._provider = "openai"
                logger.info("llm.inicializado", provider="openai")
                return
            except Exception as exc:
                logger.warning("llm.openai.fallo", error=str(exc))

        if self._settings.allow_mock_llm:
            self._provider = "mock"
            logger.warning(
                "llm.modo_mock",
                razon="Mock habilitado explícitamente para pruebas controladas.",
            )
            return

        self._provider = "unavailable"
        logger.error("llm.no_disponible", razon="No hay credenciales LLM válidas.")

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
        if self._provider == "unavailable" or self._client is None:
            raise LLMUnavailableError(
                "No hay un proveedor LLM configurado para procesar el documento."
            )

        from langchain_core.messages import HumanMessage

        respuesta = await self._client.ainvoke([HumanMessage(content=prompt)])
        return self._normalizar_contenido(getattr(respuesta, "content", respuesta))

    async def completar_multimodal(
        self, prompt: str, imagenes: list[dict[str, str] | str]
    ) -> str:
        """
        Envía un prompt junto con una o más imágenes (Base64) al LLM multimodal.

        Args:
            prompt: Instrucción o prompt clínico a procesar
            imagenes: Lista de imágenes, donde cada elemento puede ser:
                - dict con {"data_base64": "...", "mime_type": "image/jpeg"}
                - o str con cadena Base64 directa (o data URI)

        Returns:
            Texto de respuesta del LLM (transcripción clínica).

        Raises:
            LLMUnavailableError: Si el LLM no está configurado
            RuntimeError: Si ocurre un error durante la llamada
        """
        if self._provider == "mock":
            return self._respuesta_mock_multimodal(prompt, imagenes)
        if self._provider == "unavailable" or self._client is None:
            raise LLMUnavailableError(
                "No hay un proveedor LLM configurado para procesar el documento."
            )

        from langchain_core.messages import HumanMessage

        content_parts: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for img in imagenes:
            if isinstance(img, dict):
                mime = img.get("mime_type", "image/jpeg")
                b64 = img.get("data_base64") or img.get("data", "")
                url = f"data:{mime};base64,{b64}"
            elif isinstance(img, str):
                if img.startswith("data:"):
                    url = img
                else:
                    url = f"data:image/jpeg;base64,{img}"
            else:
                continue

            content_parts.append({"type": "image_url", "image_url": {"url": url}})

        respuesta = await self._client.ainvoke([HumanMessage(content=content_parts)])
        return self._normalizar_contenido(getattr(respuesta, "content", respuesta))

    def _respuesta_mock_multimodal(
        self, prompt: str, imagenes: list[dict[str, str] | str]
    ) -> str:
        """Respuesta mock para procesamiento multimodal en pruebas controladas."""
        return (
            "DOCUMENTO CLÍNICO FOTOGRAFIADO / ESCANEADO\n"
            "Paciente: Juan Pérez\n"
            "Edad: 45 años\n"
            "DNI: 12345678\n"
            "Diagnóstico: Faringoamigdalitis aguda\n"
            "CIE-10: J03.9\n"
            "Indicaciones: Amoxicilina 500mg cada 8 horas por 7 días."
        )

    @staticmethod
    def _normalizar_contenido(content: object) -> str:
        """Consolida strings, listas y bloques estructurados de LLM en un único str."""
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            partes: list[str] = []
            for parte in content:
                if isinstance(parte, str):
                    partes.append(parte)
                elif isinstance(parte, dict) and "text" in parte:
                    partes.append(str(parte["text"]))
                elif hasattr(parte, "text"):
                    partes.append(str(getattr(parte, "text")))
                elif parte is not None:
                    partes.append(str(parte))
            return "".join(partes)
        if isinstance(content, dict) and "text" in content:
            return str(content["text"])
        if hasattr(content, "text"):
            return str(getattr(content, "text"))
        return str(content)

    def _respuesta_mock(self, prompt: str) -> str:
        """Mock de respuesta LLM para desarrollo sin credenciales."""
        import json
        import re

        prompt_lower = prompt.lower()
        is_extraction = "extrae" in prompt_lower or "diagnostico_principal" in prompt_lower

        # Extraer únicamente el cuerpo del documento para evitar falsos positivos
        # con palabras como 'urgente' o 'emergencias' presentes en las instrucciones del prompt
        cuerpo = prompt_lower
        if "texto del documento:" in prompt_lower:
            cuerpo = prompt_lower.split("texto del documento:")[1]
        elif "documento a analizar:" in prompt_lower:
            cuerpo = prompt_lower.split("documento a analizar:")[1]

        # Extraer identificadores si están presentes en el texto
        dni_match = re.search(r"(?:dni|documento(?:\s+de\s+identidad)?)\s*[:#]?\s*([0-9a-z\-]+)", cuerpo)
        hc_match = re.search(r"(?:hc|historia\s+cl[íi]nica)\s*[:#]?\s*([0-9a-z\-]+)", cuerpo)
        dni_extraido = dni_match.group(1).upper() if dni_match else None
        hc_extraida = hc_match.group(1).upper() if hc_match else None

        # Caso 3: Ambiguo / ilegible
        if any(w in cuerpo for w in ["ilegible", "ambiguo", "???"]):
            if is_extraction:
                return json.dumps(
                    {
                        "paciente": {
                            "nombre": None,
                            "edad": None,
                            "id_paciente": None,
                            "documento_identidad": dni_extraido,
                            "historia_clinica": hc_extraida,
                        },
                        "medico_solicitante": {"nombre": None, "matricula": None},
                        "estudio_realizado": None,
                        "diagnostico_principal": None,
                        "cie10_sugerido": None,
                        "hallazgos_clave": ["Texto fragmentado o ilegible"],
                    }
                )
            return json.dumps(
                {
                    "tipo_documento": "Otro",
                    "especialidad": None,
                    "nivel_prioridad": "Ambiguo",
                    "razon_prioridad": "Texto con baja legibilidad e información insuficiente",
                }
            )

        # Caso 2: Urgencia (TEP / emergencia / crítico)
        if any(
            w in cuerpo
            for w in [
                "tep",
                "tromboembolismo",
                "urgente",
                "crítico",
                "critico",
                "guardia_emergencias",
            ]
        ):
            if is_extraction:
                return json.dumps(
                    {
                        "paciente": {
                            "nombre": "Carlos Eduardo Mendes",
                            "edad": 52,
                            "id_paciente": "PAC-8942",
                            "documento_identidad": dni_extraido,
                            "historia_clinica": hc_extraida,
                        },
                        "medico_solicitante": {
                            "nombre": "Dra. Renata Silveira",
                            "matricula": "145892",
                        },
                        "estudio_realizado": "Tomografía de Tórax con contraste",
                        "diagnostico_principal": "Tromboembolismo Pulmonar Agudo (TEP)",
                        "cie10_sugerido": "I26.9",
                        "hallazgos_clave": [
                            "Defecto de llenado en arteria pulmonar",
                            "TEP agudo detectado",
                            "Correlación clínica urgente",
                        ],
                    }
                )
            return json.dumps(
                {
                    "tipo_documento": "Informe de Estudio por Imágenes",
                    "especialidad": "Radiología / Neumonología",
                    "nivel_prioridad": "Urgente",
                    "razon_prioridad": "Hallazgo de TEP agudo con compromiso vascular urgente detectado",
                }
            )

        # Caso 1 / Default: Rutina
        if is_extraction:
            return json.dumps(
                {
                    "paciente": {
                        "nombre": "Ana García",
                        "edad": 35,
                        "id_paciente": "PAC-0001",
                        "documento_identidad": dni_extraido,
                        "historia_clinica": hc_extraida,
                    },
                    "medico_solicitante": {"nombre": "Dr. Roberto López", "matricula": "98231"},
                    "estudio_realizado": "Hemograma completo",
                    "diagnostico_principal": "Analítica normal sin hallazgos patológicos",
                    "cie10_sugerido": "Z00.0",
                    "hallazgos_clave": ["Parámetros hematológicos normales"],
                }
            )
        return json.dumps(
            {
                "tipo_documento": "Informe de Laboratorio",
                "especialidad": "Medicina General",
                "nivel_prioridad": "Rutina",
                "razon_prioridad": "Analítica normal sin hallazgos de alarma",
            }
        )

    @property
    def disponible(self) -> bool:
        return self._provider not in {None, "unavailable"}

    @property
    def proveedor(self) -> str:
        return self._provider or "desconocido"
