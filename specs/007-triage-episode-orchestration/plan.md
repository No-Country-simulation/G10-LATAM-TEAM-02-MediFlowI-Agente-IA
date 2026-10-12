# Implementation Plan: Orquestación de Triaje con Creación y Vinculación Automática de Episodios Clínicos

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-triage-episode-orchestration/spec.md`

## Summary

Orquestar en `triage_service.py` la gestión automática de episodios clínicos hospitalarios tras la ejecución del agente LangGraph:
1. Una vez resuelta la asociación del paciente, verificar si tiene un episodio clínico activo.
2. Si no tiene episodio activo, invocar `episode_repository.create_episode(...)` con la prioridad y hallazgos extraídos.
3. Vincular el `episodio_id` resultante en la tabla `documentos_triaje` a través de `PostgresStorageRepository`.
4. Registrar el evento inmutable `DOCUMENTO_ASOCIADO_A_EPISODIO` en `trazabilidad_eventos` mediante `AuditRepository.registrar_evento_trazabilidad(...)`.
5. Proteger la entrega del resultado con manejo resiliente ante fallas de persistencia del episodio, complementando con cobertura unitaria y E2E.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, LangGraph, Pydantic v2, asyncpg, structlog
**Storage**: PostgreSQL 17 (`episodios_clinicos`, `documentos_triaje`, `trazabilidad_eventos`, `pacientes`)
**Testing**: pytest (`test_triage_api.py`, `test_e2e_hospital_flow.py`), HTTPX TestClient
**Target Platform**: Linux / Docker Server
**Project Type**: Backend AI Orchestration & Clinical REST Service
**Performance Goals**: < 150ms de sobrecarga de orquestación por documento de triaje
**Constraints**:
- PostgreSQL como fuente única de verdad clínica.
- Integración desacoplada entre repositorios existentes (`episode_repository`, `audit_repository`, `postgres_storage`).
- Resiliencia hospitalaria: errores en el subsistema secundario de episodios no interrumpen el triaje completado.
- Cero regresiones y 100% de pruebas en verde sin mutar `mediflow_dev`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Test-First y Puerta de Calidad Estricta en Verde**: Se implementarán pruebas unitarias del servicio de triaje y actualización del flujo E2E hospitalario antes de dar por cerrada la tarea.
- [x] **II. Consulta Obligatoria ante Dudas**: El alcance técnico corresponde con exactitud a la Tarea 3.3 (Issue #34) validada con el usuario.
- [x] **III. PostgreSQL como Fuente Única de Verdad Clínica**: Los episodios clínicos, la FK en documentos de triaje y la bitácora de trazabilidad persisten en PostgreSQL.
- [x] **IV. Seguridad y Control de Acceso por Roles**: Operaciones de admisión y triaje preservan la autoría con `usuario_registro_id` / `operador_ingreso_id`.
- [x] **V. Trazabilidad Médica Inmutable**: Toda vinculación genera el evento inmutable `DOCUMENTO_ASOCIADO_A_EPISODIO` en `trazabilidad_eventos`.

## Project Structure

### Documentation (this feature)

```text
specs/007-triage-episode-orchestration/
├── spec.md              # Especificación funcional
├── plan.md              # Este archivo (Plan técnico de arquitectura)
├── research.md          # Decisiones de diseño y patrones de resiliencia
├── data-model.md        # Entidades, estados y relaciones SQL/Pydantic
├── quickstart.md        # Guía de validación y comandos de prueba
├── contracts/           # Contratos de interfaces
│   └── triage-episode-contract.yaml
└── checklists/
    └── requirements.md  # Checklist de calidad de requisitos
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── services/
│   │   ├── triage_service.py     # Orquestación de episodios tras LangGraph y resolución de paciente
│   │   └── ...
│   ├── repositories/
│   │   ├── episode_repository.py # Consulta de episodios activos y create_episode
│   │   ├── audit_repository.py   # Registro de evento DOCUMENTO_ASOCIADO_A_EPISODIO
│   │   ├── postgres_storage.py   # Persistencia de episodio_id en documentos_triaje
│   │   └── ...
│   └── ...
└── tests/
    ├── test_triage_api.py        # Pruebas de integración de orquestación en TriageService
    └── test_e2e_hospital_flow.py # Flujo E2E hospitalario con admisión, episodio y auditoría
```

**Structure Decision**: La integración se centraliza en `TriageService.procesar_documento(...)` aprovechando los métodos existentes de `episode_repository` y `AuditRepository`, añadiendo la sincronización de la columna `episodio_id` en `PostgresStorageRepository.guardar_resultado(...)`.

## Complexity Tracking

> **No violations identified**: No se agregan nuevas dependencias externas ni capas adicionales. Se conectan repositorios preexistentes mediante orquestación asíncrona estándar de Python.
