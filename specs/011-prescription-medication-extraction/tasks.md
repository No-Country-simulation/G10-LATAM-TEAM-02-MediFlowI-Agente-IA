# Tasks: Extracción Estructurada de Medicamentos Prescritos y Enrutamiento a Farmacia Hospitalaria

**Input**: Design documents from `specs/011-prescription-medication-extraction/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/openapi.contract.yaml`, `quickstart.md`)  
**Prerequisites**: `plan.md`, `spec.md`, `data-model.md`, `contracts/`, `constitution.md`  
**Organization**: Tareas agrupadas por fases y por historias de usuario (US1, US2, US3) para habilitar ejecución y validación independiente bajo TDD estricto.

---

## Phase 1: Setup (Shared Infrastructure & Contracts)

**Purpose**: Sincronización del contrato OpenAPI y fixtures de prueba para farmacoterapia.

- [X] T001 Actualizar esquema OpenAPI en specs/components/schemas.yaml con MedicamentoPrescrito y DatosExtraidos.properties.medicamentos
- [X] T002 [P] Configurar fixtures de prueba con prescripciones médicas en backend/tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modelado Pydantic v2 en el estado del agente LangGraph requerido por todas las historias de usuario.

**⚠️ CRITICAL**: Ninguna tarea de las historias de usuario puede comenzar antes de completar esta fase.

- [X] T003 [P] Implementar modelo MedicamentoPrescritoState y ampliar DatosExtraidosState con campo medicamentos en backend/app/agent/state.py
- [X] T004 [P] Definir lista canónica MEDICAMENTOS_CONTROLADOS para estupefacientes y psicofármacos en backend/app/agent/clinical_catalog.py

**Checkpoint**: Modelos de estado tipados y listos. El desarrollo de las historias de usuario puede proceder.

---

## Phase 3: User Story 1 - Extracción de Pauta Farmacológica Completa en Recetas Médicas (Priority: P1) 🎯 MVP

**Goal**: Extraer de forma estructurada los medicamentos prescritos (nombre, dosis, frecuencia y vía) en recetas médicas y derivar automáticamente a `Farmacia_Hospitalaria`.

**Independent Test**: Procesar una receta médica digitalizada con prescripción explícita (ej. *"Amoxicilina 500 mg cada 8 horas vía oral"*) y verificar que `datos_extraidos.medicamentos` contenga la entidad estructurada y el destino asignado sea `Farmacia_Hospitalaria`.

### Tests for User Story 1 (TDD - Test First) ⚠️
- [X] T005 [P] [US1] Escribir prueba unitaria TDD para parsing de respuesta LLM con lista de medicamentos en backend/tests/test_agent_cases.py
- [X] T006 [P] [US1] Escribir prueba unitaria TDD para enrutamiento a Farmacia_Hospitalaria al detectar prescripciones en backend/tests/test_destinos_triaje_unit.py

### Implementation for User Story 1
- [X] T007 [US1] Ampliar plantilla _EXTRACTION_PROMPT con especificación de medicamentos en backend/app/agent/nodes/extraction.py
- [X] T008 [US1] Implementar deserialización de medicamentos en función _parsear_respuesta en backend/app/agent/nodes/extraction.py
- [X] T009 [US1] Actualizar función _calcular_destino y node_routing para derivar a Farmacia_Hospitalaria con prescripciones activas en backend/app/agent/nodes/routing.py

**Checkpoint**: User Story 1 completamente funcional y verificable como MVP independiente.

---

## Phase 4: User Story 2 - Tolerancia a Prescripciones con Datos Parciales o Abreviaturas Clínicas (Priority: P2)

**Goal**: Permitir prescripciones con dosis, frecuencia o vía no especificadas (nulas) sin errores y garantizar deduplicación de medicamentos entre bloques de texto.

**Independent Test**: Procesar un documento clínico extenso dividido en múltiples bloques con prescripciones repetidas o posología parcial, verificando que los medicamentos se unifiquen sin duplicados y los valores ausentes queden en `None`.

### Tests for User Story 2 (TDD - Test First) ⚠️
- [X] T010 [P] [US2] Escribir prueba unitaria TDD para consolidación deduplicada de medicamentos entre bloques en backend/tests/test_agent_cases.py
- [X] T011 [P] [US2] Escribir prueba unitaria TDD para tolerancia a valores opcionales nulos en backend/tests/test_agent_cases.py

### Implementation for User Story 2
- [X] T012 [US2] Implementar deduplicación por clave compuesta normalizada en _consolidar_datos en backend/app/agent/nodes/extraction.py
- [X] T013 [US2] Añadir validación defensiva en _parsear_respuesta para descartar entradas sin nombre de fármaco en backend/app/agent/nodes/extraction.py

**Checkpoint**: User Stories 1 y 2 completamente operativas e interoperables.

---

## Phase 5: User Story 3 - Discriminación de Documentos sin Prescripciones y Fármacos Controlados (Priority: P3)

**Goal**: Mantener lista vacía en documentos diagnósticos sin derivar a Farmacia, y forzar retención de auditoría médica HITL ante fármacos controlados.

**Independent Test**: Procesar un informe ecográfico (medicamentos vacíos, cola de rutina) y una receta con opioides o psicotrópicos (destino `Farmacia_Hospitalaria` con `requiere_auditoria_humana = True`).

### Tests for User Story 3 (TDD - Test First) ⚠️
- [X] T014 [P] [US3] Escribir prueba unitaria TDD para documentos diagnósticos sin prescripciones en backend/tests/test_agent_cases.py
- [X] T015 [P] [US3] Escribir prueba unitaria TDD para detección de medicamentos controlados y activación de auditoría en backend/tests/test_destinos_triaje_unit.py

### Implementation for User Story 3
- [X] T016 [US3] Implementar detección automática de MEDICAMENTOS_CONTROLADOS en node_routing en backend/app/agent/nodes/routing.py
- [X] T017 [US3] Asegurar precedencia absoluta de Cola_Emergencia_Medica sobre Farmacia_Hospitalaria ante cuadros urgentes en backend/app/agent/nodes/routing.py

**Checkpoint**: Las 3 Historias de Usuario completadas, cubriendo el 100% de los requerimientos y casos límite.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación integral de contratos, suites completas de regresión y validación E2E.

- [X] T018 [P] Verificar sincronización del contrato OpenAPI y modelos generados en backend/tests/test_openapi_contract.py
- [X] T019 Ejecutar suite completa de regresión con pytest asegurando 100% pruebas en verde sin mutar mediflow_dev
- [X] T020 Validar flujo smoke test descrito en specs/011-prescription-medication-extraction/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies
1. **Setup (Phase 1)**: Puede iniciar de inmediato.
2. **Foundational (Phase 2)**: Depende de Phase 1. Bloquea todas las historias de usuario.
3. **User Story 1 (Phase 3)**: Depende de Foundational (Phase 2). Constituye el MVP.
4. **User Story 2 (Phase 4)**: Depende de Foundational (Phase 2) y extiende la consolidación de US1.
5. **User Story 3 (Phase 5)**: Depende de Foundational (Phase 2) y enriquece las reglas de enrutamiento de US1.
6. **Polish (Phase 6)**: Depende de la finalización de US1, US2 y US3.

### Parallel Opportunities
- **Setup**: `T001` y `T002` pueden ejecutarse en paralelo (archivos independientes).
- **Foundational**: `T003` (`state.py`) y `T004` (`clinical_catalog.py`) pueden implementarse en paralelo.
- **TDD Tests**: Todas las pruebas marcadas con `[P]` (`T005`, `T006`, `T010`, `T011`, `T014`, `T015`, `T018`) pueden desarrollarse en paralelo antes de la implementación de código.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (`T001`-`T002`) y Foundational (`T003`-`T004`).
2. Escribir pruebas unitarias TDD de US1 (`T005`-`T006`).
3. Implementar extracción y enrutamiento básico (`T007`-`T009`).
4. **Validar MVP**: Confirmar extracción de fármacos y derivación a `Farmacia_Hospitalaria`.

### Incremental Delivery
1. Añadir robustez posológica y deduplicación entre bloques (US2: `T010`-`T013`).
2. Añadir control de sustancias fiscalizadas y precedencia de urgencias (US3: `T014`-`T017`).
3. Auditoría final y regresión completa (Polish: `T018`-`T020`).
