---

description: "Task list for Frontend de Login - Pantalla de Inicio de Sesión"
---

# Tasks: Frontend de Login - Pantalla de Inicio de Sesión

**Input**: Design documents from `/specs/004-login-frontend/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: TDD obligatorio según constitución v1.2.0. Tests se escriben ANTES de implementación.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/`
- Config files at `frontend/` root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install Tailwind CSS, testing dependencies, and configure project

- [x] T001 Install Tailwind CSS v3, PostCSS, and Autoprefixer: `npm install -D tailwindcss@3 postcss autoprefixer` in `frontend/`
- [x] T002 Install testing dependencies: `npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom` in `frontend/`
- [x] T003 [P] Create `frontend/tailwind.config.js` with content paths (`./src/**/*.{html,js,ts,jsx,tsx}`), `corePlugins: { preflight: false }` (coexist with Bootstrap), theme extend with colors and fonts from prototype `src-codigo-modulos/Modulo-Login/Codigo/tailwind.config.js`
- [x] T004 [P] Create `frontend/postcss.config.js` with `tailwindcss` and `autoprefixer` plugins
- [x] T005 [P] Add `@tailwind base; @tailwind components; @tailwind utilities;` at the top of `frontend/src/index.css`
- [x] T006 [P] Add vitest test environment config to `frontend/vite.config.ts` (test: { environment: 'jsdom', globals: true, setupFiles: ['./src/test-setup.ts'] })
- [x] T007 [P] Create `frontend/src/test-setup.ts` with `import '@testing-library/jest-dom'`

**Checkpoint**: Tailwind CSS installed and configured, testing dependencies ready

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Assets and shared styles that MUST be ready before any user story

- [x] T008 [P] Copy logo image from prototype to `frontend/src/assets/login/logo.png` (reference: `src-codigo-modulos/Modulo-Login/Codigo/logo-1.png`)
- [x] T009 [P] Create `frontend/src/assets/login/line.svg` (separator line, reference: prototype `line.svg`)
- [x] T010 [P] Create `frontend/src/styles/login.css` with decorative orb styles, Quicksand/Montserrat font imports, and animation keyframes (reference: `src-codigo-modulos/Modulo-Login/Codigo/tailwind.css`)

**Checkpoint**: Assets and styles ready, user story implementation can begin

---

## Phase 3: User Story 1 - Usuario visualiza la pantalla de login (Priority: P1) MVP

**Goal**: Renderizar la pantalla de login con branding, formulario DNI/contraseña, y botón "Iniciar sesión" usando Tailwind CSS

**Independent Test**: Navegar a `/login` y verificar que la pantalla renderiza con logo, título "Bienvenido", campos DNI y contraseña, botón submit, sin credenciales hardcodeadas

### Tests for User Story 1

> **TDD**: Write tests FIRST, ensure they FAIL before implementation

- [x] T011 [P] [US1] Create test `frontend/src/pages/Login.test.tsx`: verify Login renders without crashing, contains title "Bienvenido", subtitle, logo image with alt "MediFlow", DNI input with label, password input with label, submit button "Iniciar sesión"
- [x] T012 [P] [US1] Create test `frontend/src/pages/Login.test.tsx` (add cases): verify no `defaultValue` on inputs (no hardcoded credentials), verify `autoComplete` attributes are correct ("username" for DNI, "current-password" for password), verify inputs are navigable (tab order)

### Implementation for User Story 1

- [x] T013 [P] [US1] Create `frontend/src/components/login/TestimonialSection.tsx`: presentational component with blockquote, cite, and cargo. Uses Tailwind classes. `hidden md:flex` for responsive hide on mobile
- [x] T014 [P] [US1] Create `frontend/src/components/login/LoginForm.tsx`: visual form with DNI input (type="text", inputMode="numeric", maxLength=8), password input, submit button. Props: `onSubmit`, `isSubmitting`, `error`. Controlled inputs via props. No `defaultValue`. Tailwind classes for styling
- [x] T015 [US1] Rewrite `frontend/src/pages/Login.tsx`: container with two-column grid layout (testimonial + form), decorative orbs (absolute positioned, aria-hidden), branding text "SISTEMA AUTÓNOMO DE TRIAJE Y ENRUTAMIENTO CLÍNICO", logo import. Uses Tailwind classes. No Bootstrap classes. No hardcoded credentials. No dev-only panel

**Checkpoint**: Login screen renders with all visual elements, no hardcoded data

---

## Phase 4: User Story 2 - Usuario completa el formulario e intenta iniciar sesión (Priority: P1)

**Goal**: Validación de campos, estado de carga, manejo de errores, y llamada a `useAuth().login()`

**Independent Test**: Llenar formulario, presionar submit, verificar validación de vacíos, estado de carga, y manejo de error con mock de `useAuth`

### Tests for User Story 2

- [x] T016 [P] [US2] Create test `frontend/src/components/login/LoginForm.test.tsx`: verify submit button is disabled when `isSubmitting=true`, verify error message displays when `error` prop is non-empty with `aria-live="polite"`
- [x] T017 [US2] Add to `frontend/src/pages/Login.test.tsx`: mock `useAuth` login function, verify form requires non-empty fields (HTML5 validation), verify calling login on submit with DNI and password values, verify isSubmitting state toggles, verify error display on failed login, verify redirect to `/dashboard` on success

### Implementation for User Story 2

- [x] T018 [US2] Add state management to `frontend/src/pages/Login.tsx`: `documentoIdentidad`, `password`, `error`, `isSubmitting` useState hooks. Implement `handleSubmit` that validates non-empty fields, calls `login()`, handles success (navigate to `from` path) and error (set error message). Disable button during submit
- [x] T019 [US2] Wire `frontend/src/components/login/LoginForm.tsx` to receive state and handlers from parent: `value` + `onChange` for controlled inputs, `onSubmit` handler, `isSubmitting` for button state, `error` for error display

**Checkpoint**: Form validates, submits, shows loading state, handles errors

---

## Phase 5: User Story 3 - Usuario navega a la opción de registro (Priority: P2)

**Goal**: Enlace "Regístrate" que navega a la ruta de registro

**Independent Test**: Verificar que el enlace "Regístrate" está presente y navega a `/register` al hacer click

### Tests for User Story 3

- [x] T020 [US3] Add to `frontend/src/pages/Login.test.tsx`: verify "Regístrate" button/link is present, verify clicking it calls `navigate('/register')` (mock `useNavigate`)

### Implementation for User Story 3

- [x] T021 [US3] Add "Regístrate" link to `frontend/src/components/login/LoginForm.tsx`: footer with text "¿No tienes una cuenta?" and a button that calls `onRegister` callback. Wire `onRegister` in `Login.tsx` to `navigate('/register')`

**Checkpoint**: Registration link works

---

## Phase 6: User Story 4 - Sección testimonial y branding visual (Priority: P3)

**Goal**: Sección testimonial lateral visible en desktop, oculta en móvil (< 768px)

**Independent Test**: Verificar que TestimonialSection tiene clase `hidden md:flex`, renderiza cita, autor y cargo

### Tests for User Story 4

- [x] T022 [P] [US4] Create test `frontend/src/components/login/TestimonialSection.test.tsx`: verify component renders blockquote with testimonial text, cite with author name "Dr. Alejandro Torres", cargo "Director de Operaciones Clínicas", verify container has `hidden` and `md:flex` classes for responsive behavior

### Implementation for User Story 4

- [x] T023 [US4] Verify and refine `frontend/src/components/login/TestimonialSection.tsx`: ensure content matches prototype (cita: "Simplemente la plataforma que nuestro equipo médico necesitaba para optimizar la atención.", autor: "Dr. Alejandro Torres", cargo: "Director de Operaciones Clínicas"). Ensure `hidden md:flex` responsive classes. Ensure decorative orbs in `Login.tsx` have `aria-hidden="true"`

**Checkpoint**: Testimonial section complete with responsive behavior

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and verification

- [x] T024 [P] Verify zero hardcoded credentials: run `rg -i "password|credencial|token|12345678|admin|MediFlow#" frontend/src/pages/Login.tsx frontend/src/components/login/` and confirm only variable references (no literal values)
- [x] T025 Run `npm run build` in `frontend/` — must complete with 0 TypeScript errors and 0 warnings
- [x] T026 Run `npm run test` (vitest run) in `frontend/` — must have 100% tests in green
- [x] T027 [P] Verify `src-codigo-modulos/Modulo-Login` was NOT modified (git diff should show no changes in that directory)
- [x] T028 [P] Verify no backend files were modified (git diff should show no changes in `backend/`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (Tailwind installed) — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2. MVP critical path.
- **US2 (Phase 4)**: Depends on US1 (Login.tsx exists). Extends with state/submit logic.
- **US3 (Phase 5)**: Depends on US1 (LoginForm exists). Adds register link.
- **US4 (Phase 6)**: Depends on US1 (TestimonialSection exists). Refines responsive.
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: After Foundational — no dependencies on other stories
- **US2 (P1)**: After US1 — extends Login.tsx with state management
- **US3 (P2)**: After US1 — adds link to existing LoginForm
- **US4 (P3)**: After US1 — refines TestimonialSection (already created in US1)

### Within Each User Story

- Tests MUST be written FIRST and FAIL before implementation (TDD)
- Components before page assembly
- Visual structure before interaction logic

### Parallel Opportunities

- T003, T004, T005, T006, T007 can run in parallel (Setup)
- T008, T009, T010 can run in parallel (Foundational)
- T011, T012 can run in parallel (US1 tests)
- T013, T014 can run in parallel (US1 components)
- T016 can run parallel to T017 if different file sections (US2 tests)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T011 - Login renders test in frontend/src/pages/Login.test.tsx"
Task: "T012 - Login no-hardcode test in frontend/src/pages/Login.test.tsx"

# Launch all components for User Story 1 together:
Task: "T013 - TestimonialSection in frontend/src/components/login/TestimonialSection.tsx"
Task: "T014 - LoginForm in frontend/src/components/login/LoginForm.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install Tailwind, testing deps)
2. Complete Phase 2: Foundational (assets, styles)
3. Complete Phase 3: User Story 1 (visual login screen)
4. **STOP and VALIDATE**: `npm run test` + `npm run build` in green
5. Login screen visible with Tailwind CSS

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. US1 → Login screen renders → Validate (MVP!)
3. US2 → Form works (validation, submit, errors) → Validate
4. US3 → Register link works → Validate
5. US4 → Testimonial responsive → Validate
6. Polish → Final verification (build, test, no hardcode, no backend changes)

---

## Notes

- TDD mandatory: tests first, then implementation
- No `defaultValue` on any input — only controlled `value` + `onChange`
- No dev-only panel or credential helper
- Tailwind `preflight: false` to coexist with Bootstrap
- `src-codigo-modulos/` is READ-ONLY reference, never modify
- `backend/` is untouched — frontend-only feature
