# Quickstart: Validación de Orquestación de Episodios Clínicos

**Feature**: `007-triage-episode-orchestration`
**Date**: 2026-10-10

Guía práctica para ejecutar y validar los escenarios de la orquestación de episodios en MediFlow.

## 1. Requisitos Previos

- Entorno virtual de Python activo (`.venv`).
- Variables de entorno cargadas (`.env` con configuración de pruebas).
- Docker de PostgreSQL activo si se ejecutan pruebas contra base de datos local.

## 2. Ejecución de Pruebas Automatizadas

### A. Pruebas Unitarias del Servicio de Triaje y Orquestación

Verifica que `TriageService` consulte episodios activos, cree episodios nuevos si no existen y registre el evento de trazabilidad:

```bash
cd backend
pytest tests/test_triage_api.py -v
```

### B. Pruebas del Repositorio de Episodios

Verifica que `get_active_episode_by_patient` y `create_episode` operen correctamente:

```bash
cd backend
pytest tests/test_episode_repository.py -v
```

### C. Prueba End-to-End Hospitalaria (Flujo Completo)

Ejecuta el flujo hospitalario integral:
1. Alta de paciente.
2. Ingesta de documento por Admisión.
3. Creación y vinculación automática de episodio clínico.
4. Trazabilidad inmutable `DOCUMENTO_ASOCIADO_A_EPISODIO`.
5. Retención HITL y resolución exclusiva por Coordinador/Admin.

```bash
cd backend
pytest tests/test_e2e_hospital_flow.py -v
```

### D. Verificación de Toda la Suite de Pruebas

Para garantizar cero regresiones y cumplimiento de la Regla de Oro:

```bash
cd backend
pytest
```

## 3. Comportamiento Esperado

- 100% de pruebas en verde (`passed`).
- Ningún test debe alterar ni ensuciar los datos de `mediflow_dev`.
- La orquestación debe mantener el tiempo de respuesta del servicio por debajo de los umbrales clínicos.
