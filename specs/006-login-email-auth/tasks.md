# Tasks: Autenticación por Correo y Gestión Global de Sesión Hospitalaria

**Input**: Design documents from `specs/006-login-email-auth/`  
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/auth-contracts.yaml`, `quickstart.md`  
**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (`[US1]`, `[US2]`, `[US3]`)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificación de configuración inicial y preparación de contratos

- [X] T001 Sincronizar directorio de feature en `.specify/feature.json` apuntando a `specs/006-login-email-auth`
- [X] T002 [P] Validar contrato OpenAPI de autenticación en `specs/006-login-email-auth/contracts/auth-contracts.yaml`
- [X] T003 [P] Verificar disponibilidad de dependencias de frontend y testing en `frontend/package.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Estructuras compartidas de persistencia de sesiones y esquemas de usuario en PostgreSQL

**⚠️ CRITICAL**: Prerrequisitos de infraestructura para todos los flujos de autenticación

- [X] T004 [P] Validar estructura de tabla `usuarios` y columna `especialidad_medica` en `backend/alembic/versions/o8p808522kl4_implement_unified_db_proposal.py`
- [X] T005 [P] Validar estructura de tabla `sesiones_usuario` con columnas `token_hash`, `expires_at` y `revoked_at` en `backend/alembic/versions/m6n606300ij2_add_persistent_user_sessions.py`
- [X] T006 [P] Asegurar funciones criptográficas de verificación de contraseñas y digest SHA-256 de tokens en `backend/app/core/security.py`

**Checkpoint**: Base de datos y módulo de seguridad listos para soportar los flujos de usuario.

---

## Phase 3: User Story 1 - Inicio de Sesión Exclusivo por Correo Electrónico (Priority: P1) 🎯 MVP

**Goal**: Permitir al usuario iniciar sesión solicitando exclusivamente correo electrónico y contraseña, con validación de formato, retroalimentación de errores y botón deshabilitado cuando los campos estén vacíos.

**Independent Test**: Navegar a `/login`, verificar que sólo se solicitan correo y contraseña, que el botón está deshabilitado si faltan datos, que correos inválidos muestran mensaje de error y que datos válidos envían la solicitud.

### Tests for User Story 1

- [X] T007 [P] [US1] Escribir pruebas unitarias del formulario de login cubriendo etiquetas de correo, deshabilitación de botón y formato inválido en `frontend/src/pages/Login.test.tsx`
- [X] T008 [P] [US1] Escribir pruebas de integración de actualización del campo de texto evitando renderizado del nombre en `frontend/src/pages/Login.test.tsx`

### Implementation for User Story 1

- [X] T009 [P] [US1] Actualizar `LoginForm` para exponer exclusivamente campo CORREO (tipo `email`, placeholder `"email@example.com"`) y CONTRASEÑA con botón deshabilitado en `frontend/src/components/login/LoginForm.tsx`
- [X] T010 [US1] Implementar manejador `handleInputChange` en `frontend/src/components/login/LoginForm.tsx` para propagar el valor tecleado y no el nombre del campo a los handlers
- [X] T011 [US1] Actualizar estado y validación por expresión regular (`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`) de correo electrónico en `frontend/src/pages/Login.tsx`
- [X] T012 [US1] Conectar mensajes de error por campo mediante props `error` a los inputs respectivos en `frontend/src/pages/Login.tsx`
- [X] T013 [P] [US1] Adaptar cliente API `loginUser` para enviar payload `{ correo, password }` cuando el identificador contiene formato de email en `frontend/src/api/auth.api.ts`
- [X] T014 [US1] Permitir recepción opcional de `correo` en el modelo Pydantic `LoginRequest` en `backend/app/api/v1/auth.py`
- [X] T015 [US1] Conectar búsqueda de usuario por correo mediante `get_user_by_email` en el endpoint `POST /api/v1/auth/login` en `backend/app/api/v1/auth.py`

**Checkpoint**: User Story 1 completada y funcional como MVP independiente.

---

## Phase 4: User Story 2 - Obtención y Persistencia Global Segura del Perfil de Usuario (Priority: P1)

**Goal**: Obtener en la respuesta de login y almacenar de manera global en memoria cliente los 8 datos del usuario (`id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol`, `estado`), persistiendo sólo el token en `localStorage` y rehidratando la sesión en recargas con `/auth/me`.

**Independent Test**: Iniciar sesión exitosamente, inspeccionar `useAuth().user` verificando la presencia de los 8 atributos requeridos, recargar el navegador (`F5`) y confirmar que la sesión se mantiene intacta desde `/auth/me`.

### Tests for User Story 2

- [X] T016 [P] [US2] Escribir prueba de almacenamiento en memoria de los 8 campos de usuario en `frontend/src/pages/Login.test.tsx`
- [X] T017 [P] [US2] Escribir prueba de rehidratación de sesión con llamada a `getCurrentUser` en `frontend/src/pages/Login.test.tsx`

### Implementation for User Story 2

- [X] T018 [P] [US2] Incorporar `u.especialidad_medica` al query SQL de `get_active_session_user` en `backend/app/repositories/session_repository.py`
- [X] T019 [US2] Añadir `"especialidad_medica": user.get("especialidad_medica")` a `user_payload` devuelto por `login` en `backend/app/api/v1/auth.py`
- [X] T020 [US2] Asegurar que `UserResponse` y el endpoint `GET /api/v1/auth/me` serialicen todos los campos clínicos en `backend/app/api/v1/auth.py`
- [X] T021 [P] [US2] Sincronizar contrato de interfaz `User` y `SessionUser` en `frontend/src/context/auth-context.ts`
- [X] T022 [US2] Actualizar `AuthContext` para almacenar en estado de React el usuario completo y guardar exclusivamente `{ access_token }` en `localStorage` en `frontend/src/context/AuthContext.tsx`
- [X] T023 [US2] Implementar efecto de rehidratación con `getCurrentUser` al cargar la aplicación y limpiar sesión en caso de token inválido en `frontend/src/context/AuthContext.tsx`

**Checkpoint**: User Story 2 completada. Sesión global robusta, completa y segura en todo el frontend.

---

## Phase 5: User Story 3 - Cierre e Invalidación Revocable de Sesión en Base de Datos (Priority: P2)

**Goal**: Permitir el cierre de sesión revocando el token activo en la base de datos PostgreSQL (`revoked_at = NOW()`) y limpiando el estado local y `localStorage`.

**Independent Test**: Ejecutar acción de logout, verificar que `mediflow_auth_session` se elimina del navegador y que el token queda registrado con `revoked_at` en `sesiones_usuario`.

### Tests for User Story 3

- [X] T024 [P] [US3] Escribir prueba de limpieza de estado local tras invocar logout en `frontend/src/pages/Login.test.tsx`

### Implementation for User Story 3

- [X] T025 [P] [US3] Validar endpoint de revocación de sesión `POST /api/v1/auth/logout` en `backend/app/api/v1/auth.py`
- [X] T026 [US3] Conectar función `logout` en `AuthContext` invocando `logoutUser`, limpiando estado y redirigiendo a login en `frontend/src/context/AuthContext.tsx`

**Checkpoint**: Ciclo de vida completo de autenticación y cierre de sesión operativo.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificación de calidad global, compilación sin warnings y pruebas en verde

- [X] T027 [P] Eliminar imports no utilizados en componentes de autenticación en `frontend/src/components/auth/SignUpForm.tsx` y `frontend/src/components/common/Alert.tsx`
- [X] T028 Ejecutar suite completa de pruebas unitarias de login con Vitest en `frontend/src/pages/Login.test.tsx`
- [X] T029 Ejecutar compilación de producción TypeScript y Vite (`npm run build`) verificando 0 errores
- [X] T030 Ejecutar validación de los escenarios descritos en `specs/006-login-email-auth/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

```mermaid
flowchart TD
    Phase1[Phase 1: Setup] --> Phase2[Phase 2: Foundational]
    Phase2 --> Phase3[Phase 3: User Story 1 - Login por Correo (MVP)]
    Phase2 --> Phase4[Phase 4: User Story 2 - Perfil Global & Sesión]
    Phase3 --> Phase4
    Phase4 --> Phase5[Phase 5: User Story 3 - Cierre de Sesión]
    Phase5 --> Phase6[Phase 6: Polish & Validación E2E]
```

### User Story Dependencies

- **User Story 1 (P1 - MVP)**: Inicia inmediatamente después de Foundational (Phase 2). Desacoplada e independiente.
- **User Story 2 (P1)**: Extiende el flujo de US1 consumiendo la respuesta de login para poblar el estado global y rehidratarlo vía `/auth/me`.
- **User Story 3 (P2)**: Depende de la existencia de sesiones de US2 para implementar el ciclo de revocación y cierre.

### Parallel Opportunities

- **Setup & Foundational**: T002, T003, T004, T005 y T006 pueden ejecutarse en paralelo.
- **User Story 1**: T007 y T008 (tests) pueden escribirse en paralelo. T009 y T013 pueden implementarse en paralelo.
- **User Story 2**: T016 y T017 (tests) pueden ejecutarse en paralelo. T018 (backend repo) y T021 (frontend types) pueden ejecutarse en paralelo.
- **Polish**: T027, T028 y T029 pueden ejecutarse concurrentemente.
