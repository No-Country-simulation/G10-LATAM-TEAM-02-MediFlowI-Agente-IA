# Tasks: Soporte Integral para Carga y Visualización de Imágenes WebP en Visor Clínico

**Input**: Design documents from `specs/012-webp-clinical-viewer/`  
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/ui-contracts.md`, `quickstart.md`  

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos independientes, sin dependencias no resueltas).
- **[Story]**: Identificador de la historia de usuario correspondiente (`[US1]`, `[US2]`, `[US3]`, `[US4]`).
- Todas las rutas especificadas son relativas a la raíz del repositorio.

---

## Phase 1: Setup (Infraestructura y Verificación Base)

**Propósito**: Validar el entorno de desarrollo y la configuración de pruebas antes de modificar componentes clínicos.

- [X] T001 Verificar la configuración del entorno de pruebas y ejecución base en `frontend/package.json` y `frontend/vite.config.ts`

---

## Phase 2: Foundational (Prerrequisitos de Pruebas Unitarias)

**Propósito**: Establecer el andamiaje de pruebas unitarias para garantizar el flujo Test-First exigido por la Constitución de MediFlow.

- [X] T002 Crear el archivo inicial de pruebas unitarias con mocks e importaciones base en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`

**Punto de Control**: Estructura de pruebas lista para recibir aserciones de historias de usuario.

---

## Phase 3: User Story 1 - Carga y Selección de Documentos Médicos en Formato WebP (Priority: P1) 🎯 MVP

**Meta**: Permitir a los usuarios seleccionar y arrastrar archivos `.webp` (`image/webp`) en el uploader de documentos sin advertencias de formato inválido.

**Criterio de Prueba Independiente**:
Seleccionar o arrastrar un archivo `.webp` en `DocumentUploader`; debe ser aceptado, mostrar su peso/nombre y no presentar alertas de formato no permitido.

### Tareas de Implementación

- [X] T003 [US1] Añadir `image/webp` a `ALLOWED_TYPES`, actualizar regex de extensiones a `\.(pdf|jpg|jpeg|png|webp)$/i`, agregar `.webp,image/webp` al atributo `accept` y actualizar texto descriptivo en `frontend/src/components/documents/DocumentUploader.tsx`

**Punto de Control**: User Story 1 completamente operativa y verificable de manera aislada.

---

## Phase 4: User Story 2 - Visualización y Renderizado Clínico de Imágenes WebP con Adaptación y Zoom (Priority: P1)

**Meta**: Renderizar imágenes WebP dentro de `DocumentViewer` con soporte responsive, pantalla completa y controles ergonómicos de zoom (50% a 250%).

**Criterio de Prueba Independiente**:
Abrir un documento clínico con URL `.webp`; debe renderizarse en la etiqueta `<img>` con ajuste proporcional y responder a los controles de acercar, alejar y restablecer tamaño.

### Tareas de Implementación

- [X] T004 [US2] Implementar controles de zoom (+, -, restablecer), estado `zoomLevel` y contención responsive con scroll en `frontend/src/components/documents/DocumentViewer.tsx`

**Punto de Control**: User Story 2 completamente funcional y combinable con la carga de archivos.

---

## Phase 5: User Story 3 - Manejo Resiliente de Errores ante Archivos Corruptos o Fallo de Decodificación (Priority: P2)

**Meta**: Presentar una alerta clínica amigable, descriptiva y con opción de apertura externa cuando el archivo WebP esté dañado o el navegador no pueda decodificarlo.

**Criterio de Prueba Independiente**:
Simular fallo de carga en la imagen disparando el evento `onError`; el visor debe ocultar la imagen rota y desplegar la tarjeta de alerta médica con botón para abrir el enlace original.

### Tareas de Implementación

- [X] T005 [US3] Agregar estado `imageError`, manejador `onError` en `<img>`, reseteo automático al cambiar `fileUrl` y tarjeta de alerta médica con opción de apertura externa en `frontend/src/components/documents/DocumentViewer.tsx`

**Punto de Control**: User Story 3 protege la experiencia clínica ante inconsistencias binarias o de red.

---

## Phase 6: User Story 4 - Verificación Automatizada y Pruebas Unitarias Robustas (Priority: P2)

**Meta**: Desarrollar la suite completa de pruebas unitarias que verifique exhaustivamente todos los escenarios de `DocumentViewer` y `DocumentUploader`.

**Criterio de Prueba Independiente**:
Ejecutar `vitest run src/tests/components/documents/DocumentViewer.test.tsx` y comprobar que el 100% de las aserciones pasan en verde.

### Tareas de Implementación

- [X] T006 [US4] Implementar pruebas unitarias completas de renderizado WebP, controles de zoom, activación de estado de error por `onError`, reseteo de error ante nueva URL y estado vacío en `frontend/src/tests/components/documents/DocumentViewer.test.tsx`

**Punto de Control**: Cobertura automatizada completa y verificación empírica en verde.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Propósito**: Asegurar la calidad integral, cero regresiones y compilación TypeScript limpia en todo el frontend.

- [X] T007 Ejecutar compilación TypeScript (`tsc -b && vite build`) y verificar 0 errores en `frontend/`
- [X] T008 [P] Validar los escenarios interactivos de uso definidos en `specs/012-webp-clinical-viewer/quickstart.md`

---

## Dependencies & Execution Order

### Dependencias entre Fases

- **Setup (Fase 1)**: Sin dependencias, inicio inmediato.
- **Foundational (Fase 2)**: Depende de Fase 1; prepara el archivo de pruebas antes de la lógica.
- **User Story 1 (Fase 3)**: Puede implementarse tras Fase 2; modifica `DocumentUploader.tsx`.
- **User Story 2 (Fase 4)**: Modifica `DocumentViewer.tsx` agregando renderizado y zoom.
- **User Story 3 (Fase 5)**: Modifica `DocumentViewer.tsx` agregando manejo de error resiliente.
- **User Story 4 (Fase 6)**: Valida `DocumentViewer.tsx` y `DocumentUploader.tsx` con Vitest.
- **Polish (Fase 7)**: Depende de la finalización de todas las historias anteriores.

---

## Parallel Opportunities

- **T003 [US1]** (`DocumentUploader.tsx`) y **T004/T005 [US2/US3]** (`DocumentViewer.tsx`) modifican archivos distintos y pueden desarrollarse en paralelo tras la fase fundacional.
- **T006 [US4]** puede ejecutarse en paralelo o inmediatamente después de las modificaciones de UI.
- **T008** puede validarse en paralelo tras la compilación limpia de **T007**.

---

## Implementation Strategy (MVP Incremental)

1. **MVP**: Fase 1 + Fase 2 + Fase 3 (US1: Soporte de subida y arrastre de archivos `.webp` en uploader).
2. **Incremento 2**: Fase 4 (US2: Renderizado WebP con zoom y contención en visor).
3. **Incremento 3**: Fase 5 (US3: Manejo de errores y decodificación corrupta).
4. **Incremento 4**: Fase 6 + Fase 7 (US4: Suite de pruebas unitarias en verde y build de producción).
