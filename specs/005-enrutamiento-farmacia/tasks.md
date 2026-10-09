---

description: "Task list template for feature implementation"
---

# Tasks: Enrutamiento a Farmacia Hospitalaria

**Input**: Design documents from `/specs/005-enrutamiento-farmacia/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/routing-contract.md

**Tests**: The examples below include test tasks. Tests are REQUIRED por la Regla de Oro #3 de MediFlow (0 Regresiones).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

*(No aplica para esta funcionalidad ya que el entorno y el agente base ya existen)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

*(No aplica - la funcionalidad se inserta directamente en el pipeline de enrutamiento existente)*

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Enrutamiento automático de recetas (Priority: P1) 🎯 MVP

**Goal**: Asignar documentos clasificados como receta médica o con diagnóstico de farmacoterapia a la bandeja de Farmacia_Hospitalaria de forma automática.

**Independent Test**: Verificar mediante pytest que un documento mockeado con esos parámetros resulta en `Farmacia_Hospitalaria` y `requiere_auditoria_humana = False`.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T001 [US1] Modificar `backend/tests/test_destinos_triaje_unit.py` para agregar tests que verifiquen el enrutamiento exitoso de "Receta_Medica" y diagnósticos de farmacoterapia exclusiva hacia Farmacia.

### Implementation for User Story 1

- [X] T002 [US1] Modificar `_calcular_destino` en `backend/app/agent/nodes/routing.py` para implementar las Reglas 4 (Dispensación Estándar) del routing-contract.md.

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 - Retención de medicamentos controlados (Priority: P1)

**Goal**: Retener obligatoriamente (HITL) cualquier receta que contenga estupefacientes o controlados basándose en la bandera de metadata.

**Independent Test**: Verificar mediante pytest que si `medicamentos_controlados` es `True`, la decisión final exige auditoría humana y cambia el status del estado.

### Tests for User Story 2 ⚠️

- [X] T003 [US2] Modificar `backend/tests/test_destinos_triaje_unit.py` para agregar pruebas que garanticen que `medicamentos_controlados=True` dispara `requiere_auditoria_humana=True`.
- [X] T004 [US2] Modificar `backend/tests/test_destinos_triaje_unit.py` para verificar que la prioridad "Urgente" y las discrepancias de identidad (Issue #29) toman precedencia clínica sobre Farmacia.

### Implementation for User Story 2

- [X] T005 [US2] Modificar `_calcular_destino` en `backend/app/agent/nodes/routing.py` para implementar la Regla 3 (Control Farmacológico Estricto) del routing-contract.md, leyendo de `state.metadata`.
- [X] T006 [US2] Actualizar el nodo en `backend/app/agent/nodes/routing.py` para asegurar que el `status_final` del grafo cambie a `"pendiente_auditoria"` cuando se requiera.

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently y sin generar regresiones en urgencias.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T007 Ejecutar suite completa `pytest backend/` para garantizar 0 regresiones globales (Regla de Oro).
- [X] T008 [P] Verificar que linting y formateo pasen (`ruff check`, `black`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **User Story 1 (P1)**: Debe realizarse primero (el "camino feliz" de la Farmacia).
- **User Story 2 (P1)**: Depende de US1 ya que añade la restricción de seguridad clínica sobre el enrutamiento base creado en US1.
- **Polish (Final Phase)**: Validar todo en conjunto.

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD).
- Implementación del contrato de ruteo después de los tests.

---

## Parallel Example: User Story 1 & 2

*(Al tratarse de modificaciones secuenciales en el mismo archivo `routing.py`, el paralelismo está limitado. Un desarrollador debería hacer ambos User Stories de manera secuencial).*

---

## Implementation Strategy

### Incremental Delivery

1. Añadir tests de receta normal -> Modificar `routing.py` -> Validar (MVP listo).
2. Añadir tests de controlados/urgencias -> Modificar `routing.py` para precedencias -> Validar.
3. Pase a Pull Request en `dev-henry-suarez`.
