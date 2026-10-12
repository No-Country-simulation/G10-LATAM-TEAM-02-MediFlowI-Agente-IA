---
description: "Task list for Endpoints REST de Coordinación y Auditoría Médica (HITL)"
---

# Tasks: Endpoints REST de Coordinación y Auditoría Médica (HITL)

**Input**: Design documents from `/specs/006-coordination-audit-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/coordination-api.yaml, quickstart.md

**Tests**: TDD approach strictly required per MediFlow Constitution (Write tests first, ensure failure, then implement to green).
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Exact file paths included in every task

---

## Phase 1: Setup & Schemas

**Purpose**: Definir esquemas Pydantic v2 y configuración base para la API de coordinación.

- [x] T001 [P] Crear esquemas Pydantic v2 de entrada y salida para coordinación en `backend/app/schemas/coordination.py`
- [x] T002 [P] Exportar esquemas de coordinación en `backend/app/schemas/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Extender `AuditRepository` con métodos de consulta y preparar el router base en FastAPI.

**⚠️ CRITICAL**: Must complete before user story endpoints are wired.

- [x] T003 Implementar método `obtener_triajes_pendientes` con filtros en `backend/app/repositories/audit_repository.py`
- [x] T004 [P] Implementar método `obtener_eventos_documento` en `backend/app/repositories/audit_repository.py`
- [x] T005 [P] Crear router base `backend/app/api/v1/coordination.py` con dependencias de seguridad `Depends(require_roles("COORDINADOR", "ADMINISTRADOR"))`
- [x] T006 Registrar `coordination.router` en `backend/app/main.py` bajo el prefijo `/api/v1`

**Checkpoint**: Base de datos y router base listos para recibir endpoints de historias de usuario.

---

## Phase 3: User Story 1 - Bandeja de Casos Pendientes HITL (Priority: P1) 🎯 MVP

**Goal**: Permitir a coordinadores y administradores consultar triajes pendientes con filtros por especialidad y tiempo de espera.
**Independent Test**: Ejecutar pruebas en `backend/tests/test_coordination_api.py` verificando HTTP 200 con roles autorizados y HTTP 403 con roles no autorizados para `GET /api/v1/coordination/pending`.

### Tests for User Story 1 ⚠️

- [x] T007 [P] [US1] Escribir tests de autorización RBAC y consulta de pendientes para `GET /api/v1/coordination/pending` en `backend/tests/test_coordination_api.py`

### Implementation for User Story 1

- [x] T008 [US1] Implementar endpoint `GET /api/v1/coordination/pending` en `backend/app/api/v1/coordination.py`
- [x] T009 [US1] Añadir manejo de errores (503 si la BD no está disponible, validación de parámetros) en `backend/app/api/v1/coordination.py`

**Checkpoint**: User Story 1 completa y verificada de forma independiente.

---

## Phase 4: User Story 2 - Resolución y Dictamen Clínico HITL (Priority: P1)

**Goal**: Registrar la resolución médica con dictamen formal (`aprobar`, `reclasificar`, `rechazar`), reasignación y justificación clínica obligatoria.
**Independent Test**: Ejecutar pruebas en `backend/tests/test_coordination_api.py` verificando registro inmutable en `auditorias_coordinacion` y evento de trazabilidad para `POST /api/v1/coordination/resolve/{documento_id}`.

### Tests for User Story 2 ⚠️

- [x] T010 [P] [US2] Escribir tests de resolución HITL, validación de justificación clínica y RBAC para `POST /api/v1/coordination/resolve/{documento_id}` en `backend/tests/test_coordination_api.py`

### Implementation for User Story 2

- [x] T011 [US2] Implementar endpoint `POST /api/v1/coordination/resolve/{documento_id}` en `backend/app/api/v1/coordination.py`
- [x] T012 [US2] Integrar actualización de estado del documento y persistencia inmutable en `backend/app/api/v1/coordination.py` delegando en `AuditRepository`

**Checkpoint**: User Stories 1 y 2 completamente operativas.

---

## Phase 5: User Story 3 - Trazabilidad y Consulta de Eventos (Priority: P2)

**Goal**: Permitir consultar la bitácora inmutable de eventos y dictámenes médicos de un documento de triaje.
**Independent Test**: Consultar `GET /api/v1/coordination/audit/{documento_id}` y verificar historial cronológico devuelto con HTTP 200.

### Tests for User Story 3 ⚠️

- [x] T013 [P] [US3] Escribir tests para consulta de eventos de auditoría en `backend/tests/test_coordination_api.py`

### Implementation for User Story 3

- [x] T014 [US3] Implementar endpoint `GET /api/v1/coordination/audit/{documento_id}` en `backend/app/api/v1/coordination.py`

**Checkpoint**: Todas las historias de usuario (US1, US2, US3) implementadas y testeadas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Sincronización de contratos OpenAPI, robustez y verificación de calidad integral.

- [x] T015 [P] Sincronizar endpoints y esquemas de coordinación en `specs/openapi.yaml`
- [ ] T016 Ejecutar suite completa `pytest backend/tests/ -v` asegurando 100% pruebas en verde sin mutar `mediflow_dev`
- [ ] T017 Ejecutar validaciones de `quickstart.md` para verificar contratos y respuestas semánticas
