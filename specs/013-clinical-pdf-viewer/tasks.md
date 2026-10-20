# Tasks: Visor Interactivo y Robusto de Documentos PDF Clínicos con Skeleton Loader y Zoom

**Input**: Design documents from `specs/013-clinical-pdf-viewer/`  
**Prerequisites**: [plan.md](./plan.md) (required), [spec.md](./spec.md) (required), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/document-viewer.contract.md](./contracts/document-viewer.contract.md), [quickstart.md](./quickstart.md)  
**Referencia de Plan de Trabajo**: Tarea 5.2 (`plan de trabajo/PLAN_DE_TRABAJO_FRONTEND_REACT.md`)  
**Issue de GitHub**: [FE-14] #71  

**Organization**: Las tareas están agrupadas por fases y por historia de usuario para reflejar el ciclo completo de entrega end-to-end con enfoque TDD / SDD.

---

## Phase 1: Setup & Foundational Infrastructure

**Purpose**: Tipado de contratos cliente/servidor y configuración de pruebas.

- [x] T001 [P] Crear interfaces de TypeScript (`DocumentViewerProps`, `ViewerLoadingState`, `DocumentViewerState`) en `frontend/src/components/documents/DocumentViewer.types.ts`
- [x] T002 [P] Configurar mocks para la API de Pantalla Completa (`requestFullscreen`, `exitFullscreen`) y eventos en `frontend/src/test-setup.ts`
- [x] T003 Exponer el endpoint de streaming binario `GET /api/v1/documents/{documento_id}/file` con cabeceras `inline` y tipado MIME en `backend/app/api/v1/documents.py`
- [x] T004 Proyectar `url_archivo` en `_format_document_row()` y normalizar en `frontend/src/api/documentsApi.ts`

**Checkpoint**: Infraestructura de datos y endpoints lista para alimentar el visor.

---

## Phase 2: User Story 1 - Visualización Fluida con Indicador de Carga Animado (Priority: P1) 🎯 MVP

**Goal**: Proveer retroalimentación visual inmediata al usuario clínico mediante un Skeleton Loader animado con Tailwind mientras se descarga el PDF/imagen, realizando la transición suave cuando el documento esté listo.

**Independent Test**: Abrir un documento clínico y corroborar que el Skeleton Loader (`role="status"`, animación `animate-pulse`) se renderiza de inmediato y se oculta tras el evento `load`.

### Tests para User Story 1 (TDD)
- [x] T005 [P] [US1] Escribir pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` que verifiquen el renderizado inicial del Skeleton Loader al abrir un PDF y su reemplazo por el elemento embebido al dispararse el evento `load`.

### Implementación para User Story 1
- [x] T006 [US1] Implementar el componente visual de Skeleton Loader clínico con Tailwind CSS (`animate-pulse`) simulando la estructura del expediente en `frontend/src/components/documents/DocumentViewer.tsx`.
- [x] T007 [US1] Implementar la lógica del contenedor embebido (`<object>` / `<img>` / `<iframe>`) con listener `onLoad` y transición reactiva de `loadingState` en `frontend/src/components/documents/DocumentViewer.tsx`.

**Checkpoint**: User Story 1 (MVP) completamente funcional y probada.

---

## Phase 3: User Story 2 - Control de Ampliación y Alternancia a Pantalla Completa (Priority: P2)

**Goal**: Permitir al personal médico ajustar el zoom (acercar, alejar, restablecer a 100%) y alternar a pantalla completa mediante la Full Screen API nativa y fallback CSS sin perder nitidez.

**Independent Test**: Accionar los controles de Zoom In (+25%), Zoom Out (-25%), Reset (100%) y el botón de alternancia a pantalla completa, verificando que la escala visual responde correctamente y la vista se expande a la totalidad de la pantalla.

### Tests para User Story 2 (TDD)
- [x] T008 [P] [US2] Escribir pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` para los controles de Zoom In, Zoom Out, Reset (100%) y la alternancia de pantalla completa con `requestFullscreen`/`exitFullscreen`.

### Implementación para User Story 2
- [x] T009 [US2] Implementar la barra de herramientas superior accesible (`role="toolbar"`) con botones de Zoom In, Zoom Out e indicador de porcentaje reactivo con reseteo al 100% en `frontend/src/components/documents/DocumentViewer.tsx`.
- [x] T010 [US2] Implementar el controlador de Pantalla Completa con la Fullscreen API y fallback CSS (`fixed inset-0 z-50`), sincronizando el evento nativo `fullscreenchange` en `frontend/src/components/documents/DocumentViewer.tsx`.

**Checkpoint**: Controles de zoom y modo pantalla completa interactivos y accesibles.

---

## Phase 4: User Story 3 - Descarga Directa y Manejo Resiliente de Fallos (Priority: P3)

**Goal**: Proporcionar descarga directa del archivo original desde la barra de herramientas y desplegar una tarjeta de contingencia clínica clara ante fallos de renderizado embebido.

**Independent Test**: Simular error de carga en el PDF/imagen para verificar que se muestra la alerta clínica de contingencia con enlace de descarga directa y botón de apertura en nueva pestaña.

### Tests para User Story 3 (TDD)
- [x] T011 [P] [US3] Escribir pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` para el botón de descarga directa de archivo original y la presentación de la tarjeta de contingencia en caso de fallo de renderizado.

### Implementación para User Story 3
- [x] T012 [US3] Implementar el botón de descarga directa de archivo original con preservación del nombre del documento en la barra de herramientas en `frontend/src/components/documents/DocumentViewer.tsx`.
- [x] T013 [US3] Implementar el componente de error y contingencia clínica con opciones de descarga y apertura externa segura en `frontend/src/components/documents/DocumentViewer.tsx`.
- [x] T014 [US3] Desacoplar semánticamente el encabezado accesible `<h3>` del cuerpo explicativo `<p>` en el panel de contingencia de `DocumentViewer.tsx`.

**Checkpoint**: Flujo de contingencia clínica y descarga directa 100% resilientes.

---

## Phase 5: Polish, Responsive Design & Quality Gate

**Purpose**: Verificación de responsividad, eliminación de clases legadas y compilación limpia.

- [x] T015 [P] Erradicar clases residuales de Bootstrap en `DocumentViewer.tsx` adoptando exclusivamente Tailwind CSS.
- [x] T016 [P] Verificar responsividad clínica (tablets 768px y monitores 1080p/4K).
- [x] T017 Ejecutar la suite completa de pruebas unitarias de `DocumentViewer.test.tsx` (14/14 pasando en verde).
- [x] T018 Ejecutar verificación estricta de compilación TypeScript y Vite (`npm run build`) validando cero errores.
- [x] T019 Validar el endpoint de streaming binario con llamadas curl reales (`curl -i http://127.0.0.1:8000/api/v1/documents/{id}/file`).
- [x] T020 Sincronizar estado de avance de la Tarea 5.2 en `plan de trabajo/PLAN_DE_TRABAJO_FRONTEND_REACT.md`.
