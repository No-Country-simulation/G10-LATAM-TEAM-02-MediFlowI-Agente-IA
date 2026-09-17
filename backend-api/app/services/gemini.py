"""
Servicio de Integración con Google Gemini (Gemini 1.5 Flash)
Extrae entidades clínicas y diagnósticos mediante IA Generativa Multimodal.
Incluye Fallback Híbrido Resiliente: si no hay API Key o falla la red,
conmuta automáticamente al analizador determinista sin interrumpir el servicio.
"""
import os
import json
import logging
from typing import Optional
from app.models.schemas import (
    DocumentoClinicoInput,
    DatosClinicosExtraidos,
    Paciente,
    MedicoSolicitante,
    Medicamento
)

logger = logging.getLogger(__name__)

PROMPT_SISTEMA_EXTRACCION = """
Eres un Agente Clínico Especialista en Triaje y Extracción Médica de Alta Precisión.
Tu tarea es analizar el documento clínico proporcionado y extraer un JSON estricto con los siguientes campos:
{
  "paciente": {
    "nombre": string o null,
    "edad": integer o null,
    "identificacion": string o null
  },
  "medico_solicitante": {
    "nombre": string o null,
    "matricula": string o null,
    "institucion": string o null
  },
  "estudio_realizado": string o null,
  "diagnostico_principal": string (diagnóstico detectado o hallazgo principal),
  "cie10_sugerido": string o null (Código CIE-10 estándar de la OMS, ej. I26.9, I10, E11.9),
  "medicamentos": [
    {"nombre": string, "dosis": string o null, "frecuencia": string o null}
  ] o null
}
Responde ÚNICAMENTE con el objeto JSON válido, sin bloques de código markdown ni texto adicional.
"""

class GeminiClinicalService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.is_active = bool(self.api_key and self.api_key != "tu_gemini_api_key_aqui")
        self.client = None

        if self.is_active:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(
                    model_name=self.model_name,
                    generation_config={"response_mime_type": "application/json"}
                )
                logger.info(f"Gemini AI inicializado exitosamente con modelo '{self.model_name}'")
            except Exception as e:
                logger.warning(f"Error inicializando SDK de Gemini ({e}). Se utilizará fallback determinista.")
                self.is_active = False
        else:
            logger.info("GEMINI_API_KEY no configurada. Modo Fallback determinista activo por defecto.")

    def extraer_con_gemini(self, doc: DocumentoClinicoInput) -> Optional[DatosClinicosExtraidos]:
        """
        Intenta la extracción estructurada mediante Gemini 1.5 Flash.
        Si la API no está configurada o arroja excepción, retorna None para activar el fallback.
        """
        if not self.is_active or not self.client:
            return None

        contenido_texto = doc.documento_texto or ""
        if not contenido_texto.strip() and not doc.documento_base64:
            return None

        try:
            prompt = f"{PROMPT_SISTEMA_EXTRACCION}\n\nDocumento a analizar:\n{contenido_texto}"
            response = self.client.generate_content(prompt)
            raw_json = response.text.strip()
            
            # Limpiar posibles delimitadores markdown si el modelo los incluye
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:]
            if raw_json.endswith("```"):
                raw_json = raw_json[:-3]
            
            data = json.loads(raw_json.strip())
            return DatosClinicosExtraidos.model_validate(data)

        except Exception as err:
            logger.warning(f"Gemini API falló o agotó cuota ({err}). Conmutando a fallback determinista.")
            return None

gemini_service = GeminiClinicalService()
