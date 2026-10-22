"""Pruebas unitarias del resolvedor de identidad clínica de pacientes (US-14).

Ejercita las ramas de ``verificar_identidad_paciente`` mockeando el repositorio:
sin identificadores, asociación unívoca, conflicto de identidad y manejo
resiliente de fallos de base de datos.
"""

from unittest.mock import AsyncMock

import pytest

from app.agent import patient_matcher
from app.agent.patient_matcher import verificar_identidad_paciente
from app.repositories.postgres_storage import DatabaseUnavailableError


async def test_sin_identificadores_devuelve_sin_coincidencia():
    resultado = await verificar_identidad_paciente(None, "   ")
    assert resultado.estado == "sin_coincidencia"
    assert resultado.es_conflicto is False
    assert "Sin identificadores" in resultado.motivo


async def test_paciente_asociado_univocamente(monkeypatch):
    monkeypatch.setattr(
        patient_matcher.patient_repository,
        "resolver_paciente_por_identificadores",
        AsyncMock(return_value={"estado": "asociado", "paciente": {"id": "P-1"}}),
    )
    resultado = await verificar_identidad_paciente("12345678", "HC-001")
    assert resultado.estado == "asociado"
    assert resultado.paciente == {"id": "P-1"}
    assert resultado.es_conflicto is False


async def test_conflicto_de_identidad(monkeypatch):
    monkeypatch.setattr(
        patient_matcher.patient_repository,
        "resolver_paciente_por_identificadores",
        AsyncMock(return_value={"estado": "conflicto", "paciente": None}),
    )
    resultado = await verificar_identidad_paciente("12345678", "HC-999")
    assert resultado.estado == "conflicto"
    assert resultado.es_conflicto is True
    assert resultado.paciente is None


async def test_sin_coincidencia_en_bd(monkeypatch):
    monkeypatch.setattr(
        patient_matcher.patient_repository,
        "resolver_paciente_por_identificadores",
        AsyncMock(return_value={"estado": "sin_coincidencia", "paciente": None}),
    )
    resultado = await verificar_identidad_paciente("00000000", None)
    assert resultado.estado == "sin_coincidencia"
    assert resultado.es_conflicto is False


async def test_base_de_datos_no_disponible_es_resiliente(monkeypatch):
    monkeypatch.setattr(
        patient_matcher.patient_repository,
        "resolver_paciente_por_identificadores",
        AsyncMock(side_effect=DatabaseUnavailableError("sandbox caído")),
    )
    resultado = await verificar_identidad_paciente("12345678", None)
    assert resultado.estado == "sin_coincidencia"
    assert "Base de datos no disponible" in resultado.motivo


async def test_error_inesperado_es_resiliente(monkeypatch):
    monkeypatch.setattr(
        patient_matcher.patient_repository,
        "resolver_paciente_por_identificadores",
        AsyncMock(side_effect=RuntimeError("boom")),
    )
    resultado = await verificar_identidad_paciente("12345678", "HC-001")
    assert resultado.estado == "sin_coincidencia"
    assert "Error inesperado" in resultado.motivo
