"""Metadatos de respuestas SDD, sin modificar respuestas HTTP ni validaciones."""

from fastapi import FastAPI, routing
from fastapi.routing import APIRoute

from app._generated.models import ErrorResponse, HTTPValidationError

_ERROR_DESCRIPTIONS = {
    400: "Solicitud inválida, datos duplicados o documento malformado",
    401: "Token Bearer ausente, inválido o expirado",
    403: "Rol sin permisos para esta operación",
    404: "Recurso no encontrado",
    409: "Conflicto con el estado actual del recurso",
    413: "El archivo supera el límite de 10 MB",
    415: "MIME, firma o formato de archivo no permitido",
    422: "Datos de solicitud incompletos o inválidos",
    500: "Error interno del servidor / agente",
    503: "Dependencia requerida no disponible (PostgreSQL, almacenamiento o proveedor LLM)",
}


def error_responses(*codes: int) -> dict:
    """Reutiliza los modelos generados del contrato en las declaraciones del router."""
    return {
        code: {
            "description": _ERROR_DESCRIPTIONS[code],
            "model": HTTPValidationError if code == 422 else ErrorResponse,
        }
        for code in codes
    }


def use_explicit_response_codes(app: FastAPI) -> None:
    """Los routers con responses explícitas controlan sus códigos documentados.

    FastAPI agrega 422 por parámetros/cuerpo, incluso por la cabecera de auth.
    Se quita sólo ese código implícito cuando el router no lo declara. Las rutas
    sin responses explícitas conservan la generación normal de FastAPI.
    No se carga el YAML ni se sustituye el esquema: se conservan modelos,
    descripciones, seguridad, parámetros, contenidos y caché de FastAPI.
    """
    original_openapi = app.openapi

    def openapi() -> dict:
        schema = original_openapi()
        # FastAPI reciente conserva inclusiones de routers sin aplanarlas.
        # En versiones anteriores las rutas ya son APIRoute directamente.
        contexts = getattr(routing, "iter_route_contexts", iter)(app.routes)
        for context in contexts:
            route = getattr(context, "original_route", context)
            if not isinstance(route, APIRoute) or not context.responses:
                continue
            if "422" in {str(code) for code in context.responses}:
                continue
            for method in context.methods:
                operation = schema["paths"].get(context.path_format, {}).get(method.lower())
                if operation:
                    operation["responses"].pop("422", None)
        return schema

    app.openapi = openapi
