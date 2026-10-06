# Implementation Plan: Frontend de Login - Pantalla de Inicio de Sesión

**Branch**: `004-login-frontend` | **Date**: 2026-10-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-login-frontend/spec.md`

## Summary

Reemplazar la pantalla de login actual (`src/pages/Login.tsx`, basada en Bootstrap con credenciales hardcodeadas) por una nueva implementación visual usando Tailwind CSS, siguiendo el prototipo de `src-codigo-modulos/Modulo-Login`. La pantalla incluye formulario DNI/contraseña, sección testimonial lateral (oculta en móvil), orbes decorativos de fondo, y branding de MediFlow. Sin tocar backend, sin credenciales hardcodeadas, responsive completo.

## Technical Context

**Language/Version**: TypeScript 6.0 + React 19.2

**Primary Dependencies**: react, react-dom, react-router-dom (existentes); tailwindcss + postcss + autoprefixer (a instalar)

**Storage**: N/A (frontend-only, no se persisten datos nuevos; se reutiliza localStorage existente vía AuthContext)

**Testing**: vitest 5.0 + @testing-library/react (a instalar si no está presente)

**Target Platform**: Web browser (Chrome, Firefox, Edge) — escritorio (1920x1080), tablet (768px), móvil (375px)

**Project Type**: web-app (frontend SPA)

**Performance Goals**: Renderizado de pantalla de login en < 2s desde navegación

**Constraints**: 
- Cero credenciales hardcodeadas (FR-008)
- Tailwind CSS obligatorio (FR-013, FR-014)
- Responsive obligatorio (FR-015)
- TypeScript estricto, 0 errores `tsc --noEmit` (FR-016)
- No modificar backend ni src-codigo-modulos (FR-010, FR-011)

**Scale/Scope**: 1 pantalla (Login), 1 componente, 1 hoja de estilos Tailwind, configuración de Tailwind

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Test-First (TDD) | PASS | Se escriben pruebas vitest antes/durante implementación. `vitest run` + `npm run build` en verde. |
| II. Consulta Obligatoria | PASS | Clarificaciones resueltas en session 2026-10-05 (2 preguntas). |
| III. PostgreSQL Fuente Única | N/A | No se toca backend ni base de datos. |
| IV. RBAC Hospitalario | N/A | El login delega al AuthContext existente; no se alteran roles. |
| V. Trazabilidad Médica | N/A | No aplica a pantalla de login. |
| Frontend Tailwind CSS | PASS | FR-013/FR-014 implementan Tailwind CSS según constitución v1.2.0. |
| Frontend Responsive | PASS | FR-015 garantiza responsive con breakpoints 1920/768/375. |
| TypeScript Estricto | PASS | FR-016 garantiza 0 errores, prohibido `any`. |
| Sin emojis | PASS | FR-012 prohíbe saturación de emojis. |

**Gate Result**: PASS — No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/004-login-frontend/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ui-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── pages/
│   │   └── Login.tsx          # Reescrito con Tailwind CSS
│   ├── components/
│   │   └── login/             # NUEVO: componentes de login
│   │       ├── LoginForm.tsx
│   │       └── TestimonialSection.tsx
│   ├── assets/
│   │   └── login/             # NUEVO: assets del login (logo, imágenes)
│   └── styles/
│       └── login.css          # NUEVO: estilos específicos de login (orbes, animaciones)
├── tailwind.config.js         # NUEVO: configuración Tailwind
├── postcss.config.js          # NUEVO: configuración PostCSS
└── src/
    └── index.css              # Actualizado: directivas @tailwind
```

**Structure Decision**: Web application (frontend-only). Se reutiliza la estructura existente de `frontend/src/`. Se añade `src/components/login/` para sub-componentes del login, `src/assets/login/` para assets, y `src/styles/login.css` para estilos específicos. La configuración de Tailwind va en la raíz del frontend.

## Complexity Tracking

> No violations. Table omitted.
