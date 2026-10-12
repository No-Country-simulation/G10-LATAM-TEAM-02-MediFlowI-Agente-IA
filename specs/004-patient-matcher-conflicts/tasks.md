# Tasks: Nodo de Resolución de Identidad y Conflictos DNI/HC en Pipeline

**Input**: `specs/004-patient-matcher-conflicts/spec.md`, `specs/004-patient-matcher-conflicts/plan.md`  
**Feature Branch**: `004-patient-matcher-conflicts` (desarrollado en rama de trabajo `dev-wilmer-gulcochia`)  
**Status**: Completed (100% Tests Passed - 153/153 Green)  

---

## Dependencies & User Story Order

```mermaid
flowchart TD
    Setup[Phase 1: Setup & Prerrequisitos] --> Foundational[Phase 2: Modelos & Test Harness]
    Foundational --> US1[Phase 3: US1 - Cotejo y Resolución de Identidad (P1)]
    US1 --> US2[Phase 4: US2 - Enrutamiento a Cola_Revision_Ambigua (P2)]
    US2 --> US3[Phase 5: US3 - Inyección de Metadata e Integración Pipeline (P3)]
    US3 --> Polish[Phase 6: Verificación y Cero Regresiones (Regla de Oro)]
```

---

## Phase 1: Setup & Prerrequisitos

- [x] T001 Verificar la estructura de agentes en `backend/app/agent/` y repositorios en `backend/app/repositories/patient_repository.py`.
- [x] T002 [P] Configurar el archivo de suite de pruebas unitarias en `backend/tests/test_patient_matcher.py`.

---

## Phase 2: Foundational & Modelos Base

- [x] T003 [P] Implementar modelo Pydantic `ResultadoMatchingPaciente` en `backend/app/agent/patient_matcher.py`.
- [x] T004 Implementar fixtures y mocks asíncronos para `patient_repository.resolver_paciente_por_identificadores` y `AgentState` en `backend/tests/test_patient_matcher.py`.

---

## Phase 3: User Story 1 (Priority: P1) — Cotejo de Identificadores y Detección de Conflictos

**Goal**: Cotejar DNI e Historia Clínica extraídos contra PostgreSQL y clasificar el resultado en `asociado`, `sin_coincidencia` o `conflicto` sin inferir por nombres.  
**Independent Test**: `test_patient_matching_same_patient`, `test_patient_matching_conflict`, `test_patient_matching_no_match`, `test_patient_matching_single_identifier`, `test_patient_matching_db_error` pasando en verde con mock de repositorio.

- [x] T005 [P] [US1] Escribir tests unitarios para `verificar_identidad_paciente` (`test_matching_same_patient`, `test_matching_conflict`, `test_matching_no_match`, `test_matching_single_identifier`, `test_matching_db_resilience`) en `backend/tests/test_patient_matcher.py`.
- [x] T006 [US1] Implementar función asíncrona `verificar_identidad_paciente(dni: str | None, historia_clinica: str | None) -> ResultadoMatchingPaciente` en `backend/app/agent/patient_matcher.py`.
- [x] T007 [US1] Validar ejecución de tests de US1: `pytest backend/tests/test_patient_matcher.py -k "test_matching"` asegurando 100% en verde.

---

## Phase 4: User Story 2 (Priority: P2) — Enrutamiento Automático a `Cola_Revision_Ambigua`

**Goal**: Forzar en `backend/app/agent/nodes/routing.py` el destino a `Cola_Revision_Ambigua` con `requiere_auditoria_humana = True` y `status = "pendiente_auditoria"` cuando se detecte discrepancia de identidad.  
**Independent Test**: `test_routing_node_handles_identity_conflict` y `test_routing_node_standard_when_no_conflict` pasando en verde.

- [x] T008 [P] [US2] Escribir tests unitarios para el nodo `routing.py` ante presencia del flag `discrepancia_identidad_detectada` en `backend/tests/test_patient_matcher.py`.
- [x] T009 [US2] Modificar `_calcular_destino` y `node_routing` en `backend/app/agent/nodes/routing.py` para priorizar la discrepancia de identidad sobre cualquier otra regla de enrutamiento ordinario.
- [x] T010 [US2] Validar ejecución de tests de US2: `pytest backend/tests/test_patient_matcher.py -k "test_routing"` asegurando 100% en verde.

---

## Phase 5: User Story 3 (Priority: P3) — Inyección de Metadata e Integración en Pipeline

**Goal**: Integrar la verificación en el nodo `extraction.py`, inyectar la metadata del conflicto (`discrepancia_identidad_detectada`, `motivo_ambiguedad`, `dni_detectado`, `hc_detectada`) y validar en el pipeline completo del agente.  
**Independent Test**: `test_extraction_integrates_identity_conflict` y casos de pipeline en `backend/tests/test_agent_cases.py` pasando en verde.

- [x] T011 [P] [US3] Escribir tests de integración para pipeline con conflicto DNI/HC en `backend/tests/test_patient_matcher.py` y `backend/tests/test_agent_cases.py`.
- [x] T012 [US3] Integrar llamada a `verificar_identidad_paciente` en `backend/app/agent/nodes/extraction.py` para adjuntar `id_paciente` si es asociado o inyectar flags de conflicto en `metadata`.
- [x] T013 [US3] Validar ejecución de tests de US3: `pytest backend/tests/test_patient_matcher.py backend/tests/test_agent_cases.py -v` asegurando 100% en verde.

---

## Phase 6: Verificación y Calidad Final (Regla de Oro de MediFlow)

- [x] T014 Ejecutar la suite completa de pruebas de matching y agente: `pytest backend/tests/test_patient_matcher.py backend/tests/test_agent_cases.py backend/tests/test_sdd_pipeline.py -v`.
- [x] T015 Ejecutar la suite general del backend para asegurar cero regresiones: `pytest backend/tests/ -v`.
- [x] T016 Registrar progreso en `tasks.md`, preparar commit atómico y documentar PR para Issue #29 (`[IA-02]`).
