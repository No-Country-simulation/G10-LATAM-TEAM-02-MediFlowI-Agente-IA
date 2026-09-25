"""Catálogo canónico y normalización de tipos de documentos clínicos."""

from __future__ import annotations

import re
import unicodedata

TIPOS_DOCUMENTO_CLINICO: tuple[str, ...] = (
    "Informe Clínico",
    "Evolución Clínica",
    "Epicrisis",
    "Receta Médica",
    "Orden Médica",
    "Orden de Procedimiento",
    "Solicitud de Interconsulta",
    "Informe de Laboratorio",
    "Informe de Estudio por Imágenes",
    "Informe Quirúrgico",
    "Consentimiento Informado",
    "Certificado Médico",
    "Referencia y Contrarreferencia",
    "Registro de Vacunación",
    "Otro",
)


def _clave(valor: str) -> str:
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", valor)
        if not unicodedata.combining(caracter)
    )
    return re.sub(r"[^a-z0-9]+", " ", sin_acentos.lower()).strip()


_ALIAS: dict[str, str] = {_clave(tipo): tipo for tipo in TIPOS_DOCUMENTO_CLINICO}
_ALIAS.update(
    {
        "analitica de laboratorio": "Informe de Laboratorio",
        "analisis de laboratorio": "Informe de Laboratorio",
        "resultado de laboratorio": "Informe de Laboratorio",
        "laboratorio": "Informe de Laboratorio",
        "informe de estudio por imagenes": "Informe de Estudio por Imágenes",
        "informe de imagenes": "Informe de Estudio por Imágenes",
        "imagenologia": "Informe de Estudio por Imágenes",
        "radiografia": "Informe de Estudio por Imágenes",
        "orden de estudio": "Orden de Procedimiento",
        "solicitud de procedimiento": "Orden de Procedimiento",
        "interconsulta": "Solicitud de Interconsulta",
        "alta medica": "Epicrisis",
        "resumen de alta": "Epicrisis",
        "historia clinica": "Informe Clínico",
        "nota medica": "Evolución Clínica",
        "nota de evolucion": "Evolución Clínica",
        "receta": "Receta Médica",
        "prescripcion medica": "Receta Médica",
        "desconocido": "Otro",
        "error": "Otro",
    }
)


def normalizar_tipo_documento(valor: object) -> str:
    """Convierte variantes del LLM y fuentes legadas a un valor canónico."""
    if not isinstance(valor, str) or not valor.strip():
        return "Otro"
    clave = _clave(valor)
    if clave in _ALIAS:
        return _ALIAS[clave]
    for alias, canonico in sorted(_ALIAS.items(), key=lambda item: len(item[0]), reverse=True):
        if alias and (clave.startswith(f"{alias} ") or f" {alias} " in f" {clave} "):
            return canonico
    return "Otro"


CATALOGO_PARA_PROMPT = " | ".join(TIPOS_DOCUMENTO_CLINICO)
