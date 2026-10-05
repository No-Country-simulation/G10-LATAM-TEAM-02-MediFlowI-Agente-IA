# Implementation Plan: Repositorio Asíncrono episode_repository con asyncpg

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-05 | **Spec**: [specs/003-episode-repository/spec.md](./spec.md)

**Input**: Feature specification from `specs/003-episode-repository/spec.md`

---

## Summary

Implementar el repositorio asíncrono `backend/app/repositories/episode_repository.py` utilizando `asyncpg` para encapsular todas las operaciones de acceso y persistencia relacional sobre la tabla `episodios_clinicos` y la consulta agregada optimizada sobre la vista SQL `v_episodios_detalle`. Se proveerán métodos atómicos para creación de episodios, búsqueda por ID/código, transición de estados de atención, asignación de profesionales médicos y listado con filtros clínicos, integrando manejo de resiliencia con `DatabaseUnavailableError` y logs estructurados con `structlog`.

---

## Technical Context

**Language/Version**: Python 3.13 / FastAPI  
**Primary Dependencies**: `asyncpg` (driver asíncrono PostgreSQL), `structlog` (logging estructurado), `uuid` (identificadores estándar)  
**Storage**: PostgreSQL 17 (`mediflow_dev`) — Tabla `episodios_clinicos` y Vista `v_episodios_detalle`  
**Testing**: `pytest`, `pytest-asyncio`, `unittest.mock` (simulación asíncrona de conexión `asyncpg`)  
**Target Platform**: Linux / Docker  
**Project Type**: Backend Web Service / Repository Layer  
**Performance Goals**: Consultas de detalle y listados agregados < 20ms en base de datos local  
**Constraints**: No mutar la base de datos de desarrollo durante pruebas unitarias; 100% pruebas en verde antes de finalizar  
**Scale/Scope**: Módulo de persistencia clínica para soporte del flujo hospitalario de triaje y admisión  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance Assessment | Status |
|---|---|---|
| **I. Test-First y Puerta de Calidad Estricta en Verde** | Suite unitaria dedicada `test_episode_repository.py` con cobertura de todos los métodos y casos borde sin mutar DB. | ✅ PASS |
| **II. Consulta Obligatoria ante Dudas** | Requerimientos y contratos clínicos verificados con el plan y el esquema unificado. | ✅ PASS |
| **III. PostgreSQL Fuente Única de Verdad** | Persistencia estricta en `episodios_clinicos` y lectura desde `v_episodios_detalle` (edad dinámica en tiempo real). | ✅ PASS |
| **IV. Seguridad y RBAC** | Mapeo de operadores y médicos con sus roles y especialidades en consultas agregadas. | ✅ PASS |
| **V. Trazabilidad Médica** | Actualización de timestamps `updated_at` en cada transición de estado. | ✅ PASS |

---

## Project Structure

### Documentation (this feature)

```text
specs/003-episode-repository/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions (Phase 0)
├── data-model.md        # Entities, schema & state machine (Phase 1)
├── quickstart.md        # Validation & verification guide (Phase 1)
├── contracts/           # Repository interface contracts (Phase 1)
│   └── episode-repository-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Actionable task list (Phase 2 - /speckit-tasks)
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── repositories/
│   │   ├── postgres_storage.py    # Pool de asyncpg y DatabaseUnavailableError
│   │   ├── patient_repository.py  # Patrón de referencia existente
│   │   └── episode_repository.py  # [NUEVO] Repositorio asíncrono de episodios
│   ├── models/
│   │   └── episode.py             # Modelos/schemas de datos clínicos (si aplica)
│   └── api/v1/                    # Endpoints que consumirán el repositorio
└── tests/
    └── test_episode_repository.py # [NUEVO] Suite TDD aislada con mocks asyncpg
```

---

## Structure Decision

Se adopta el patrón repositorio modular ya establecido en `patient_repository.py` y `user_repository.py`, reutilizando la gestión de conexiones y pool centralizado en `postgres_storage.py` (`_require_pool`, `DatabaseUnavailableError`).

---

## Complexity Tracking

*No violations to project constitution detected.*
