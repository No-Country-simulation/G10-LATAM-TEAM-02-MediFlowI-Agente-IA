"""Contexto efímero por invocación, separado del estado y metadatos del cliente."""

import json
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from app._generated.models import ResultadoFusionVision


@cache
def _esquema_fusion_json() -> str:
    """Contrato nativo sin anotaciones redundantes; conserva tipos y restricciones."""

    def limpiar(value):
        if isinstance(value, dict):
            return {
                key: limpiar(item)
                for key, item in value.items()
                if key not in {"title", "description", "default", "examples"}
            }
        if isinstance(value, list):
            return [limpiar(item) for item in value]
        return value

    schema = limpiar(ResultadoFusionVision.model_json_schema())
    classification = schema["$defs"]["ClasificacionFusionVision"]
    if "especialidad" not in classification["required"]:
        classification["required"].append("especialidad")
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def esquema_fusion() -> dict[str, Any]:
    """Copia por petición para evitar que el SDK modifique el esquema compartido."""
    return json.loads(_esquema_fusion_json())


@dataclass
class ContextoTriaje:
    # Cliente inyectado: también admite dobles de prueba del protocolo LLM.
    llm_service: Any = field(default=None, repr=False)
    fusion_intentada: bool = False
    fusion_resultado: ResultadoFusionVision | None = field(default=None, repr=False)
