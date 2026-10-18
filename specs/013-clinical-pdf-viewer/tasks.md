# Tasks: Visor Interactivo y Robusto de Documentos PDF Clínicos con Skeleton Loader y Zoom

**Input**: Design documents from `specs/013-clinical-pdf-viewer/`
**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/document-viewer.contract.md](./contracts/document-viewer.contract.md), [quickstart.md](./quickstart.md)

**Tests**: De acuerdo con el Principio I de la Constitución de MediFlow (TDD Obligatorio y Test-First), se incluyen tareas explícitas de pruebas automatizadas antes de la implementación de cada historia de usuario.

**Organization**: Las tareas están agrupadas por historia de usuario para permitir la implementación y verificación independiente de cada incremento.

## Format: `[ID] [P?] [Story] Description with file path`

- **[P]**: Ejecutable en paralelo (archivos independientes o sin dependencias de tareas no completadas).
- **[Story]**: Historia de usuario a la que pertenece ([US1], [US2], [US3]).
- Rutas exactas incluidas en cada descripción.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificación de línea base del entorno y definición de tipos comunes

- [X] T001 Verificar la suite de pruebas del frontend en verde (87 tests pasando) ejecutando `npm test` en `frontend/`
- [X] T002 [P] Crear interfaces de TypeScript (`DocumentViewerProps`, `ViewerLoadingState`, `DocumentViewerState`) en `frontend/src/components/documents/DocumentViewer.types.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura compartida para visualización y soporte de pruebas de Fullscreen

**⚠️ CRITICAL**: Ninguna historia de usuario debe comenzarse antes de completar esta fase.

- [X] T003 Configurar mocks para la API de Pantalla Completa (`requestFullscreen`, `exitFullscreen`) y eventos en `frontend/src/test-setup.ts`
- [X] T004 [P] Definir componentes auxiliares de presentación e íconos hospitalarios en `frontend/src/components/documents/DocumentViewer.tsx`

**Checkpoint**: Base de pruebas y contratos de tipado listos.

---

## Phase 3: User Story 1 - Visualización Fluida con Indicador de Carga Animado (Priority: P1) 🎯 MVP

**Goal**: Proveer retroalimentación visual inmediata al usuario clínico mediante un Skeleton Loader animado con Tailwind mientras se carga el documento PDF, realizando la transición suave cuando el documento esté listo.

**Independent Test**: Cargar un documento PDF y verificar que el Skeleton Loader (`role="status"`, `animate-pulse`) se renderiza inmediatamente y desaparece al emitirse el evento de carga exitosa.

### Tests for User Story 1 (TDD) ⚠️
- [X] T005 [P] [US1] Escribir pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` que verifiquen el renderizado inicial del Skeleton Loader al abrir un PDF y su posterior reemplazo por el elemento embebido al dispararse el evento `load`.

### Implementation for User Story 1
- [X] T006 [US1] Implementar el componente visual de Skeleton Loader clínico con Tailwind CSS (`animate-pulse`) simulando la estructura del expediente en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T007 [US1] Implementar la lógica del contenedor embebido (`<object>` / `<iframe>`) con listener `onLoad` y transición reactiva de `loadingState` en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T008 [US1] Ejecutar suite de pruebas de US1 para validar transición a verde en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`.

**Checkpoint**: User Story 1 (MVP) completamente funcional y testeada de forma independiente.

---

## Phase 4: User Story 2 - Control de Ampliación y Alternancia a Pantalla Completa (Priority: P2)

**Goal**: Permitir al personal médico ajustar el zoom (acercar, alejar, restablecer a 100%) y alternar a pantalla completa mediante la Full Screen API nativa y fallback CSS sin perder nitidez.

**Independent Test**: Accionar los botones de zoom in/out/reset y el botón de pantalla completa, verificando que la escala visual responde correctamente y la vista se expande a la totalidad de la pantalla.

### Tests for User Story 2 (TDD) ⚠️
- [X] T009 [P] [US2] Escribir pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` para los controles de Zoom In, Zoom Out, Reset (100%) en documentos PDF e imágenes, y la alternancia de pantalla completa con `requestFullscreen`/`exitFullscreen`.

### Implementation for User Story 2
- [X] T010 [US2] Implementar la barra de herramientas superior accesible (`role="toolbar"`) con botones de Zoom In, Zoom Out e indicador de porcentaje reactivo con reseteo al 100% en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T011 [US2] Implementar el controlador de Pantalla Completa con la Fullscreen API y fallback CSS (`fixed inset-0 z-50`), sincronizando el evento `fullscreenchange` en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T012 [US2] Ejecutar suite de pruebas de US2 para validar paso a verde en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`.

**Checkpoint**: User Stories 1 y 2 integradas y operando de forma independiente.

---

## Phase 5: User Story 3 - Descarga Directa y Manejo Resiliente de Fallos (Priority: P3)

**Goal**: Proporcionar descarga directa del archivo PDF original desde la barra de herramientas y desplegar una tarjeta de contingencia clínica clara ante fallos de renderizado embebido.

**Independent Test**: Simular error de carga en el PDF para verificar que se muestra la alerta clínica de contingencia con enlace de descarga directa y botón de apertura en nueva pestaña.

### Tests for User Story 3 (TDD) ⚠️
- [X] T013 [P] [US3] Escribir pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` para el botón de descarga directa de archivo original y la presentación de la tarjeta de contingencia en caso de fallo de renderizado o timeout.

### Implementation for User Story 3
- [X] T014 [US3] Implementar el botón de descarga directa de archivo original con preservación del nombre del documento en la barra de herramientas en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T015 [US3] Implementar el componente de error y contingencia clínica con opciones de descarga y apertura externa segura en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T016 [US3] Ejecutar suite de pruebas de US3 para validar paso a verde en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`.

**Checkpoint**: Todas las historias de usuario (US1, US2, US3) implementadas y verificadas con pruebas en verde.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación de responsividad, eliminación de clases legadas y compilación limpia

- [X] T017 [P] Erradicar cualquier clase residual de Bootstrap en `DocumentViewer.tsx` reemplazándola por clases de Tailwind CSS en `frontend/src/components/documents/DocumentViewer.tsx`.
- [X] T018 [P] Verificar responsividad clínica (tablets 768px y monitores 1080p/4K) y ejecutar suite completa de pruebas del frontend (`npm test`) en `frontend/`.
- [X] T019 Ejecutar verificación estricta de compilación TypeScript y Vite (`npm run build`) en `frontend/`.
- [X] T020 Validar los escenarios del archivo `quickstart.md` en `specs/013-clinical-pdf-viewer/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sin dependencias, inicio inmediato.
- **Foundational (Phase 2)**: Depende de Phase 1. Bloquea el inicio de las historias de usuario.
- **User Story 1 (Phase 3 - P1 MVP)**: Depende de Foundational (Phase 2).
- **User Story 2 (Phase 4 - P2)**: Depende de Foundational (Phase 2). Puede desarrollarse secuencialmente tras US1.
- **User Story 3 (Phase 5 - P3)**: Depende de Foundational (Phase 2).
- **Polish (Phase 6)**: Depende de la finalización de US1, US2 y US3.

### User Story Dependencies

- **US1 (P1)**: Foco en carga y Skeleton Loader; no depende de US2 ni US3.
- **US2 (P2)**: Foco en interacción (zoom y pantalla completa); se monta sobre el contenedor del visor establecido en US1.
- **US3 (P3)**: Foco en descarga directa y resiliencia; se monta sobre la barra de herramientas y el manejo de errores.

---

## Parallel Execution Opportunities

- **T001** y **T002**: Pueden ejecutarse en paralelo durante Setup.
- **T003** y **T004**: Mocks de prueba y definición de clases base en paralelo.
- **T005**, **T009**, **T013**: Las pruebas de cada historia de usuario pueden prepararse en paralelo una vez completada la fase fundamental.
- **T017** y **T018**: Limpieza de Tailwind y pruebas responsivas en paralelo en la fase final.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001 - T002) y Foundational (T003 - T004).
2. Implementar User Story 1 (T005 - T008).
3. Validar de forma independiente: Skeleton loader animado + carga fluida de PDF.

### Incremental Delivery
1. Extender con User Story 2: Zoom y Pantalla Completa (T009 - T012).
2. Extender con User Story 3: Descarga y Contingencia (T013 - T016).
3. Pulir con Tailwind CSS clínico y compilar con 0 errores (T017 - T020).
