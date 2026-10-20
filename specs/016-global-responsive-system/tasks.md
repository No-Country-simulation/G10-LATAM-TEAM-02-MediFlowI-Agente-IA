# Tasks: Sistema Global de Diseño Adaptable y Responsive

**Input**: Design documents from `specs/016-global-responsive-system/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `contracts/ui-layout-contract.md`  
**Approach**: TDD / Test-First per MediFlow Constitution Principle I  

## Format: `- [ ] [TaskID] [P?] [Story?] Description with file path`

---

## Phase 1: Setup (Infrastructure & Responsive Tokens)

**Purpose**: Asegurar las reglas globales de Tailwind y viewport sin desbordamiento horizontal.

- [x] T001 Verificar y configurar directivas de viewport y bloqueo de desbordamiento horizontal en `frontend/src/index.css`
- [x] T002 [P] Declarar tokens de diseño responsive y breakpoints clínicos en `frontend/tailwind.config.js`

---

## Phase 2: Foundational (Layout Shell & Drawer Infrastructure)

**Purpose**: Infraestructura central del layout que soporta la navegación adaptable en todos los módulos.

- [x] T003 Crear pruebas de navegación móvil y apertura/cierre de drawer en `frontend/src/tests/components/layout/ResponsiveLayout.test.tsx`
- [x] T004 Implementar cabecera móvil, estado `isMobileSidebarOpen` y backdrop en `frontend/src/components/layout/MainLayout.tsx`
- [x] T005 Adaptar `frontend/src/components/layout/Sidebar.tsx` para comportarse como drawer retráctil en `< 1024px` con botón de cierre accesible

**Checkpoint**: Shell adaptable y drawer móvil 100% operativos.

---

## Phase 3: User Story 1 - Navegación Principal y Shell Adaptable (Priority: P1) 🎯 MVP

**Goal**: Permitir navegación sin solapamientos ni desbordamientos en móviles, tablets y escritorios.

- [x] T006 [US1] Ajustar espaciado dinámico del contenedor principal (`main`) en `frontend/src/components/layout/MainLayout.tsx`
- [x] T007 [US1] Asegurar cierre automático del drawer al hacer clic en rutas de navegación en `frontend/src/components/layout/Sidebar.tsx`
- [x] T008 [US1] Ejecutar pruebas unitarias de layout y drawer con `npm test -- src/tests/components/layout/ResponsiveLayout.test.tsx`

**Checkpoint**: Navegación responsive funcional e independientemente verificable.

---

## Phase 4: User Story 2 - Tablas Clínicas y Controles de Paginación en Vistas Compactas (Priority: P1)

**Goal**: Tablas clínicas con scroll horizontal contenido y paginación apilable en móviles.

- [x] T009 [P] [US2] Adaptar contenedor y paginación apilable (`flex-col sm:flex-row`) con área de toque de 40px en `frontend/src/components/documents/DocumentTable.tsx`
- [x] T010 [P] [US2] Optimizar barras de filtros y tabla responsive en `frontend/src/pages/Documents.tsx`
- [x] T011 [P] [US2] Asegurar contenedor `overflow-x-auto` y botones táctiles en `frontend/src/pages/UsersManagementView.tsx`
- [x] T012 [P] [US2] Asegurar contenedor `overflow-x-auto` y filtros en `frontend/src/pages/PatientsManagementView.tsx`
- [x] T013 [US2] Actualizar y ejecutar pruebas de tabla y paginación en `frontend/src/tests/components/documents/DocumentTable.test.tsx`

**Checkpoint**: Todas las tablas clínicas operan con fluidez en dispositivos móviles y tablets.

---

## Phase 5: User Story 3 - Parrillas Bento y Métricas del Dashboard Adaptables (Priority: P2)

**Goal**: Reorganización de tarjetas de triaje e indicadores en cuadrícula responsive (1/2/4 columnas).

- [x] T014 [US3] Migrar rejilla de tarjetas KPI y paneles de triaje a Tailwind Grid responsive (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`) en `frontend/src/pages/Dashboard.tsx`
- [x] T015 [US3] Adaptar tarjetas de métricas en cabecera de pacientes en `frontend/src/pages/PatientsManagementView.tsx`
- [x] T016 [US3] Verificar renderizado en pruebas existentes de Dashboard en `frontend/src/pages/Dashboard.test.tsx`

**Checkpoint**: Dashboard y KPIs visualmente estables en resoluciones desde 360px hasta 1920px.

---

## Phase 6: User Story 4 - Visor Documental y Comparador Clínico Dividido (Priority: P2)

**Goal**: Vista dividida adaptable (apilada en pantallas menores a 1200px) en detalle documental y auditoría.

- [x] T017 [US4] Implementar layout de 2 columnas en desktop y apilado en tablet/móvil en `frontend/src/pages/DocumentDetail.tsx`
- [x] T018 [US4] Reorganizar vista dividida y panel de toma de decisiones en `frontend/src/pages/AuditDetail.tsx`
- [x] T019 [US4] Adaptar barra de controles y contenedor del visor de PDF/imágenes en `frontend/src/components/documents/DocumentViewer.tsx`

**Checkpoint**: Visor clínico y auditoría usables en tablets de ronda médica.

---

## Phase 7: User Story 5 - Modales, Formularios y Banners de Alerta Táctiles (Priority: P3)

**Goal**: Modales acotados a `max-h-[90vh]` con scroll vertical interno y alertas no intrusivas.

- [x] T020 [P] [US5] Ajustar clases de modales de paciente (Crear/Editar/Documentos) con `max-h-[90vh]` y scroll interno en `frontend/src/pages/PatientsManagementView.tsx`
- [x] T021 [P] [US5] Optimizar anclaje y anchura responsiva de alertas flotantes en `frontend/src/components/common/EmergencyAlertToast.tsx`
- [x] T022 [US5] Ejecutar pruebas de toasts y modales en `frontend/src/tests/components/common/EmergencyAlertToast.test.tsx`

**Checkpoint**: Formularios, modales y alertas operan sin cortes por teclado virtual en pantallas táctiles.

---

## Phase 8: Polish & Verificación de Calidad Global (Constitution Gates)

**Purpose**: Asegurar 0 regresiones y 100% de pruebas en verde.

- [x] T023 Ejecutar suite completa de pruebas de frontend con `npm test` en `frontend/`
- [x] T024 Compilación limpia de TypeScript y Vite con `npm run build` en `frontend/`
- [x] T025 Ejecutar pruebas de backend con `.venv\Scripts\pytest.exe` en `backend/` para verificar cero regresiones
