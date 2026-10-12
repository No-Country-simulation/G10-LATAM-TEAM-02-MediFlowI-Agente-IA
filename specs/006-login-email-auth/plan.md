# Implementation Plan: Autenticación por Correo y Gestión Global de Sesión Hospitalaria

**Branch**: `006-login-email-auth` | **Date**: 2026-10-12 | **Spec**: [specs/006-login-email-auth/spec.md](file:///c:/Users/owl_d/Documents/CURSOS/ORACLE_ONE_AI_FOR_TECH/Hackaton/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/specs/006-login-email-auth/spec.md)

**Input**: Feature specification from `specs/006-login-email-auth/spec.md`

---

## Summary

Implementar y asegurar el flujo de inicio de sesión hospitalario de MediFlow para que solicite **únicamente correo electrónico y contraseña**, garantizando que el estado global de autenticación en el cliente (`AuthContext`) obtenga, almacene y preserve de manera segura los datos completos del perfil de usuario necesarios para la navegación y control de acceso clínico (`id`, `documento_identidad`, `nombres`, `apellidos`, `correo`, `especialidad_medica`, `rol`, `estado`), con tokens Bearer revocables en PostgreSQL (`sesiones_usuario`), almacenamiento seguro en `localStorage` (únicamente del token de acceso) y rehidratación íntegra mediante `/auth/me`.

---

## Technical Context

**Language/Version**: 
- Frontend: TypeScript 5.8+ / React 19 / Vite 8
- Backend: Python 3.12+ / FastAPI / Pydantic v2

**Primary Dependencies**:
- Frontend: React Router v7, Tailwind CSS v3, Axios
- Backend: asyncpg, Structlog, bcrypt/hashlib

**Storage**:
- PostgreSQL 17 (`mediflow_dev`): Tablas `usuarios` y `sesiones_usuario` (con digest irreversible `SHA-256` del token y marca `revoked_at`).

**Testing**:
- Frontend: Vitest con JSDOM y `@testing-library/react` (`npm run test`)
- Backend: Pytest con fixtures asíncronas (`pytest`)

**Target Platform**:
- Web Application (Entorno clínico hospitalario y responsivo para escritorio, tablet y móvil)

**Project Type**:
- Full-stack Web Application (Frontend React desacoplado + Backend FastAPI REST)

**Performance Goals**:
- Tiempo de respuesta de autenticación < 1.5s en condiciones normales
- Rehidratación de sesión cliente < 500ms al recargar página

**Constraints**:
- PostgreSQL es la Fuente Única de Verdad (Regla de Oro de MediFlow).
- Prohibido almacenar contraseñas, hashes o sales en el almacenamiento local del cliente (`localStorage`).
- Control de acceso por roles (RBAC) estricto (`ADMINISTRADOR`, `COORDINADOR`, `OPERADOR`).
- Cero regresiones: 100% de pruebas en verde antes de dar por finalizada la tarea.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principio I (Test-First & Puerta de Calidad Estricta en Verde)**:
  - 16 pruebas unitarias implementadas en `Login.test.tsx` pasando al 100% en verde.
  - Compilación `npm run build` ejecutada con 0 errores de TypeScript.
- [x] **Principio II (Consulta Obligatoria ante Dudas)**:
  - Requisitos claros: el usuario confirmó explícitamente el uso de correo y contraseña, y la persistencia de los 8 atributos de perfil clínico.
- [x] **Principio III (PostgreSQL como Fuente Única de Verdad)**:
  - La verificación de credenciales y la validez de sesión residen en PostgreSQL (`usuarios` y `sesiones_usuario`).
  - No se simulan datos si PostgreSQL está disponible; si cae la BD se retorna HTTP 503.
- [x] **Principio IV (Seguridad y Control de Acceso por Roles - RBAC)**:
  - El perfil recuperado incluye `rol` y `especialidad_medica` para autorizar módulos clínicos (ej. `/auditoria` para coordinadores).
- [x] **Principio V (Trazabilidad y Calidad)**:
  - Tokens revocables con `revoked_at` para soporte de logout inmutable en base de datos.
  - Diseño responsivo en Tailwind CSS sin uso de estilos CSS nativos redundantes.

---

## Project Structure

### Documentation (this feature)

```text
specs/006-login-email-auth/
├── spec.md              # Especificación de requisitos y criterios de éxito
├── plan.md              # Este plan de implementación arquitectónica
├── research.md          # Decisiones de arquitectura y diseño técnico
├── data-model.md        # Modelo relacional, entidades y gestión de tokens
├── quickstart.md        # Guía de validación y escenarios ejecutables
├── checklists/
│   └── requirements.md  # Validación de calidad de la especificación
└── contracts/
    └── auth-contracts.yaml # Especificación OpenAPI de endpoints de autenticación
```

### Source Code Modificado e Involucrado

```text
backend/app/
├── api/v1/
│   └── auth.py                     # Endpoints /auth/login, /auth/logout, /auth/me
├── repositories/
│   ├── session_repository.py       # Persistencia de sesiones y consulta con especialidad_medica
│   └── user_repository.py          # Búsqueda por correo (get_user_by_email) y documento
└── core/
    └── security.py                 # Generación y hash de tokens opacos

frontend/src/
├── api/
│   └── auth.api.ts                 # loginUser (soporte de correo), getCurrentUser, logoutUser
├── context/
│   ├── auth-context.ts             # Tipos SessionUser y AuthContextValue
│   └── AuthContext.tsx             # Estado global de usuario, token y rehidratación
├── components/login/
│   └── LoginForm.tsx               # Formulario de login: CORREO, CONTRASEÑA, botón deshabilitado
├── pages/
│   ├── Login.tsx                   # Controlador de la página, validación de regex de correo
│   └── Login.test.tsx              # Suite de pruebas unitarias (16 tests en verde)
└── common/
    └── Input.tsx                   # Componente base de entrada de texto
```

---

## Complexity Tracking

No se registraron violaciones constitucionales ni desviaciones del stack. La arquitectura se mantiene simple, cohesiva y alineada con los estándares de MediFlow.
