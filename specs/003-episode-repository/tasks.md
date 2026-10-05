# Tasks: Repositorio Asíncrono episode_repository para Gestión de Episodios Clínicos

**Input**: `specs/003-episode-repository/spec.md`, `specs/003-episode-repository/plan.md`  
**Feature Branch**: `003-episode-repository` (desarrollado en rama de trabajo `dev-wilmer-gulcochia`)  
**Status**: Completed (100% Tests Passed)  

---

## Dependencies & User Story Order

```mermaid
flowchart TD
    Setup[Phase 1: Setup & Conexión] --> Foundational[Phase 2: TDD Harness & Helpers]
    Foundational --> US1[Phase 3: US1 - Creación de Episodios (P1)]
    US1 --> US2[Phase 4: US2 - Consultas Agregadas v_episodios_detalle (P2)]
    US2 --> US3[Phase 5: US3 - Transición de Estados y Listado (P3)]
    US3 --> Polish[Phase 6: Verificación y Calidad Final]
```

---

## Phase 1: Setup & Prerrequisitos

- [x] T001 Verificar la estructura del módulo en `backend/app/repositories/episode_repository.py` y compatibilidad con `postgres_storage.py`.
- [x] T002 [P] Configurar el archivo de suite de pruebas unitarias aisladas en `backend/tests/test_episode_repository.py`.

---

## Phase 2: Foundational & Helpers Base

- [x] T003 Implementar helper `_require_pool()` en `backend/app/repositories/episode_repository.py` para validar disponibilidad del pool y arrojar `DatabaseUnavailableError`.
- [x] T004 [P] Implementar helper `_database_failure(operation, exc)` con logging estructurado `structlog` en `backend/app/repositories/episode_repository.py`.
- [x] T005 [P] Implementar función generadora de código clínico `_generate_episode_code()` con formato determinista `EP-YYYYMMDD-XXXX` en `backend/app/repositories/episode_repository.py`.
- [x] T006 Implementar fixture y mocks asíncronos de `asyncpg.Pool` y `asyncpg.Connection` en `backend/tests/test_episode_repository.py`.

---

## Phase 3: User Story 1 (Priority: P1) — Creación y Registro Atómico de Episodios

**Goal**: Permitir la inserción atómica de episodios clínicos en la tabla `episodios_clinicos` con código único y estado inicial `ingresado`.  
**Independent Test**: `test_create_episode_success` y `test_create_episode_database_error` pasando en verde con mock de `asyncpg`.

- [x] T007 [US1] Escribir tests unitarios para creación de episodios (`test_create_episode_success`, `test_create_episode_custom_code`, `test_create_episode_missing_pool`) en `backend/tests/test_episode_repository.py`.
- [x] T008 [US1] Implementar función `create_episode(data: dict[str, Any]) -> dict[str, Any]` en `backend/app/repositories/episode_repository.py`.
- [x] T009 [US1] Validar ejecución de tests de US1: `pytest backend/tests/test_episode_repository.py -k "test_create"` asegurando 100% en verde.

---

## Phase 4: User Story 2 (Priority: P2) — Consulta Detallada y Agregada desde `v_episodios_detalle`

**Goal**: Obtener el detalle completo del episodio con datos demográficos del paciente (edad dinámica) y médicos asignados consultando la vista `v_episodios_detalle`.  
**Independent Test**: `test_get_episode_by_id_found`, `test_get_episode_by_id_not_found`, y `test_get_episode_by_code` en verde.

- [x] T010 [US2] Escribir tests unitarios para consultas por ID y código (`test_get_episode_by_id_found`, `test_get_episode_by_id_not_found`, `test_get_episode_by_code`) en `backend/tests/test_episode_repository.py`.
- [x] T011 [US2] Implementar función `get_episode_by_id(episode_id: UUID | str) -> dict[str, Any] | None` consultando `v_episodios_detalle` en `backend/app/repositories/episode_repository.py`.
- [x] T012 [US2] Implementar función `get_episode_by_code(codigo_episodio: str) -> dict[str, Any] | None` consultando `v_episodios_detalle` en `backend/app/repositories/episode_repository.py`.
- [x] T013 [US2] Validar ejecución de tests de US2: `pytest backend/tests/test_episode_repository.py -k "test_get"` asegurando 100% en verde.

---

## Phase 5: User Story 3 (Priority: P3) — Transición de Estados, Asignación y Listado

**Goal**: Permitir la actualización de estados (`ingresado`, `en_triaje`, `atendido`, `derivado`), asignación de médicos y listado paginado con filtros.  
**Independent Test**: `test_update_episode_status`, `test_assign_doctor`, y `test_list_episodes_with_filters` en verde.

- [x] T014 [US3] Escribir tests unitarios para actualización de estado, asignación médica y listado con filtros en `backend/tests/test_episode_repository.py`.
- [x] T015 [US3] Implementar función `update_episode_status(episode_id: UUID | str, nuevo_estado: str) -> bool` en `backend/app/repositories/episode_repository.py`.
- [x] T016 [US3] Implementar función `assign_doctor(episode_id: UUID | str, medico_id: UUID | str, rol: str, especialidad: str | None = None) -> bool` en `backend/app/repositories/episode_repository.py`.
- [x] T017 [US3] Implementar función `list_episodes(estado: str | None = None, nivel_prioridad: str | None = None, paciente_id: UUID | str | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]` en `backend/app/repositories/episode_repository.py`.
- [x] T018 [US3] Validar ejecución de tests de US3: `pytest backend/tests/test_episode_repository.py -k "test_update or test_assign or test_list"` asegurando 100% en verde.

---

## Phase 6: Verificación y Calidad Final (Regla de Oro de MediFlow)

- [x] T019 Ejecutar la suite completa del repositorio: `pytest backend/tests/test_episode_repository.py -v`.
- [x] T020 Ejecutar la suite general de base de datos y migraciones para asegurar cero regresiones: `pytest backend/tests/test_episode_repository.py backend/tests/test_episodios_db.py backend/tests/test_migrations.py -v`.
- [x] T021 Registrar progreso en `tasks.md`, preparar commit atómico y documentar PR para Issue #25 (`[BD-02]`).
