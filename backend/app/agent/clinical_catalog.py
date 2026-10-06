"""Catálogos canónicos de documentos clínicos y códigos CIE-10."""

from __future__ import annotations

import json
import re
import unicodedata
from collections.abc import Mapping
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import TypedDict


class ResultadoValidacionCIE10(TypedDict):
    valido: bool
    codigo: str | None
    descripcion: str | None


@lru_cache(maxsize=1)
def _catalogo_cie10() -> Mapping[str, str]:
    """Carga una sola vez el catálogo versionado; nunca consulta servicios externos."""
    path = Path(__file__).with_name("data") / "cie10_catalog.json"
    catalogo = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalogo, dict) or not catalogo:
        raise ValueError("El catálogo CIE-10 debe contener códigos y descripciones.")
    for codigo, descripcion in catalogo.items():
        if (
            not re.fullmatch(r"[A-Z][0-9]{2}(?:\.[0-9])?", codigo)
            or not isinstance(descripcion, str)
            or not descripcion.strip()
        ):
            raise ValueError(f"Entrada inválida en el catálogo CIE-10: {codigo!r}")
    return MappingProxyType(catalogo)


def validar_y_completar_cie10(codigo: str) -> ResultadoValidacionCIE10:
    """Valida pertenencia exacta tras normalizar mayúsculas, bordes y punto decimal.

    Acepta categorías de tres caracteres y subcategorías de cuatro, como I219.
    No realiza coincidencias aproximadas ni infiere códigos a partir del diagnóstico.
    Un código ausente, mal formado o inexistente devuelve campos nulos.
    """
    invalido: ResultadoValidacionCIE10 = {
        "valido": False,
        "codigo": None,
        "descripcion": None,
    }
    if not isinstance(codigo, str):
        return invalido
    canonico = codigo.strip().upper()
    if not re.fullmatch(r"[A-Z][0-9]{2}(?:\.?[0-9])?", canonico):
        return invalido
    if len(canonico) == 4:
        canonico = f"{canonico[:3]}.{canonico[3]}"
    descripcion = _catalogo_cie10().get(canonico)
    if descripcion is None:
        return invalido
    return {"valido": True, "codigo": canonico, "descripcion": descripcion}


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
