# Tasks: Visualización Estructurada de Medicamentos Prescritos, Vías de Administración y Robustez del Visor Clínico

**Input**: Design documents from `specs/014-prescription-medication-viewer/`  
**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [contracts/medication-contract.json](contracts/medication-contract.json)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Preparación de tipos base y contratos compartidos entre cliente y servidor.

- [x] T001 [P] Definir la interfaz TypeScript `Medication` y extender `ClinicalDocument` en `frontend/src/types/documents.ts`
- [x] T002 [P] Validar el esquema JSON de contrato de prescripción en `specs/014-prescription-medication-viewer/contracts/medication-contract.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Persistencia en base de datos y serialización de backend requeridas para exponer medicamentos hacia el frontend.

- [x] T003 Persistir medicamentos extraídos en el campo JSONB `metadata` durante la operación de inserción/UPSERT en `backend/app/repositories/postgres_storage.py`
- [x] T004 Proyectar `metadata.medicamentos` dentro del payload de `datos_extraidos["medicamentos"]` en `backend/app/api/v1/documents.py`
- [x] T005 [P] Normalizar la entidad `Medication` con mapeo dual (`medicamento` y `nombre`) y vías de administración en `frontend/src/api/documentsApi.ts`

**Checkpoint**: Base de datos, API REST y capa cliente tipadas y sincronizadas.

---

## Phase 3: User Story 1 - Visualización de Prescripciones en Ficha de Detalle (Priority: P1) 🎯 MVP

**Goal**: Permitir a médicos y farmacéuticos visualizar la tabla completa de medicamentos prescritos (fármaco, dosis, frecuencia, vía de administración) en la ficha de detalle clínico (`/documentos/:id`).

**Independent Test**: Acceder a `/documentos/:id` para un documento con receta médica y verificar que se despliega la tabla con encabezado `Medicamentos Prescritos`, ícono `FaPills` y badges de vía, omitiéndose limpiamente si el documento carece de prescripciones.

### Tests para User Story 1

- [x] T006 [P] [US1] Ejecutar prueba de serialización de medicamentos en endpoints de documentos en `backend/tests/test_documents_api.py`
- [x] T007 [P] [US1] Verificar compatibilidad de instanciación multimodal en `backend/tests/test_pipeline_fusion.py`

### Implementación para User Story 1

- [x] T008 [US1] Implementar tarjeta Bento con icono `FaPills` y tabla responsiva de farmacoterapia en `frontend/src/components/triage/ExtractedData.tsx`
- [x] T009 [US1] Añadir insignias estilizadas para vía de administración (`via_administracion`) con Tailwind CSS en `frontend/src/components/triage/ExtractedData.tsx`
- [x] T010 [US1] Implementar renderizado defensivo para omitir la tabla o mostrar estado neutro en ausencia de prescripción en `frontend/src/components/triage/ExtractedData.tsx`

**Checkpoint**: User Story 1 (MVP) completamente funcional e independientemente verificable.

---

## Phase 4: User Story 2 - Visualización en Consola de Triaje y Auditoría Médica (Priority: P2)

**Goal**: Exponer la farmacoterapia extraída en tiempo real en la consola de triaje (`/triaje`) y en el formulario de resolución de auditoría manual HITL (`/auditoria/:id`).

**Independent Test**: Cargar un caso de prueba en la consola interactiva de triaje o ingresar como auditor a `/auditoria/:id` y corroborar que los medicamentos prescritos aparecen en las tarjetas de datos extraídos antes de despachar o rectificar el destino.

### Implementación para User Story 2

- [x] T011 [P] [US2] Implementar tabla de medicamentos prescritos extraídos en tiempo real en `frontend/src/pages/TriageConsoleView.tsx`
- [x] T012 [P] [US2] Incorporar sección de medicamentos prescritos detectados como soporte de validación clínica en `frontend/src/pages/AuditDetail.tsx`
- [x] T013 [US2] Asegurar responsividad móvil y coherencia tipográfica de las tablas de farmacoterapia en `frontend/src/pages/TriageConsoleView.tsx` y `frontend/src/pages/AuditDetail.tsx`

**Checkpoint**: Prescripciones visibles en todos los flujos de toma de decisiones clínicas.

---

## Phase 5: User Story 3 - Robustez Semántica y Accesibilidad en Visor Clínico (Priority: P3)

**Goal**: Desacoplar el encabezado de alerta del cuerpo explicativo en el panel de contingencia de `DocumentViewer.tsx`, garantizando accesibilidad y eliminando ambigüedades en Testing Library.

**Independent Test**: Cargar un recurso PDF o imagen con URL inválida en el visor y constatar que el elemento `<h3>` renderiza el título conciso de error sin duplicar el texto descriptivo del `<p>`.

### Tests para User Story 3

- [x] T014 [P] [US3] Validar suite de pruebas del visor clínico frente a estados de carga y contingencia en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`

### Implementación para User Story 3

- [x] T015 [US3] Desacoplar encabezado `<h3>` con mensajes unívocos de error de PDF e imagen en `frontend/src/components/documents/DocumentViewer.tsx`
- [x] T016 [US3] Mantener párrafos explicativos `<p>` y botones accesibles de descarga directa y apertura en nueva pestaña en `frontend/src/components/documents/DocumentViewer.tsx`

**Checkpoint**: Visor clínico accesible, libre de ambigüedades y con 100% de tests en verde.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación integral de calidad, compilación estricta y sincronización de documentación.

- [x] T017 Ejecutar suite completa de frontend (`npm --prefix frontend test -- --run`) asegurando 98/98 tests aprobados en verde
- [x] T018 Ejecutar compilación de producción (`npm --prefix frontend run build`) validando cero errores de TypeScript
- [x] T019 Ejecutar pruebas de regresión de backend (`backend/.venv/bin/pytest backend/tests/test_pipeline_fusion.py backend/tests/test_documents_api.py`)
- [x] T020 Sincronizar estado de avance de la Tarea 2.5 en `plan de trabajo/PLAN_DE_TRABAJO_FRONTEND_REACT.md`

---

## Dependencies & Completion Order

```mermaid
graph TD
    subgraph Phase 1: Setup
        T001[T001: Tipos TS Medication]
        T002[T002: Contrato JSON Schema]
    end

    subgraph Phase 2: Foundational
        T003[T003: Persistencia en postgres_storage]
        T004[T004: Proyección en documents.py]
        T005[T005: Normalización en documentsApi]
    end

    subgraph Phase 3: User Story 1 (P1 - MVP)
        T006[T006: Test documents_api]
        T007[T007: Test pipeline_fusion]
        T008[T008: Tabla ExtractedData]
        T009[T009: Badges de vía de administración]
        T010[T010: Renderizado defensivo]
    end

    subgraph Phase 4: User Story 2 (P2)
        T011[T011: Medicamentos en TriageConsoleView]
        T012[T012: Medicamentos en AuditDetail]
        T013[T013: Responsividad de tablas]
    end

    subgraph Phase 5: User Story 3 (P3)
        T014[T014: Tests DocumentViewer]
        T015[T015: Desacople h3 en DocumentViewer]
        T016[T016: Acciones de contingencia]
    end

    subgraph Phase 6: Polish
        T017[T017: Vitest Green Gate]
        T018[T018: Build TS 0 Errors]
        T019[T019: Pytest Green Gate]
        T020[T020: Sincronización Plan de Trabajo]
    end

    T001 --> T005
    T002 --> T003
    T003 --> T004
    T004 --> T005

    T005 --> T006
    T005 --> T007
    T006 --> T008
    T007 --> T008
    T008 --> T009 --> T010

    T010 --> T011
    T010 --> T012
    T011 --> T013
    T012 --> T013

    T005 --> T015
    T015 --> T016
    T016 --> T014

    T010 --> T017
    T013 --> T017
    T014 --> T017
    T017 --> T018
    T018 --> T019
    T019 --> T020
```

---

## Parallel Execution Opportunities

- **Fase 1**: `T001` (`types/documents.ts`) y `T002` (`contracts/`) completados concurrentemente.
- **Fase 2**: `T005` (`documentsApi.ts`) completado en paralelo con `T003`/`T004`.
- **Fase 3**: `T006` y `T007` (tests de backend) ejecutados y aprobados concurrentemente.
- **Fase 4**: `T011` (`TriageConsoleView.tsx`) y `T012` (`AuditDetail.tsx`) verificados en paralelo.
- **Fase 5**: `T014` y `T015` verificados con suite de 14 tests aprobados.

---

## Implementation Strategy (MVP First)

1. **Incremento 1 (MVP - US1)**: ✅ Concluido — Consulta y verificación de medicamentos y vías de administración en la ficha clínica (`/documentos/:id`).
2. **Incremento 2 (US2)**: ✅ Concluido — Exposición en tiempo real en consola de triaje (`/triaje`) y formulario de resolución médica HITL (`/auditoria/:id`).
3. **Incremento 3 (US3)**: ✅ Concluido — Desacoplamiento semántico en el visor clínico ante contingencias.
4. **Validación Final**: ✅ Concluido — 100% verde en Vitest (98 tests), 0 errores TypeScript en compilación Vite y 100% verde en Pytest (50 tests).
