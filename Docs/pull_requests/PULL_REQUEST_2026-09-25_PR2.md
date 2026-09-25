# 2. 🚀 Pull Request #2 — 25/09/2026

Este documento registra los Pull Requests generados el día **25/09/2026** para el proyecto **MediFlow**.

---

## 🔀 2. PR #2 — Módulo 1: Autenticación, Usuarios (DNI 8 Cifras) & Control de Acceso RBAC

### 📌 Datos del Pull Request
- **Título del PR**: `feat(auth): modulo 1 autenticacion por DNI 8 cifras, gestion de usuarios y control de acceso RBAC`
- **Número de PR**: 2 (PR #2 del día 25/09/2026)
- **Fecha**: 25/09/2026
- **Autor**: Erick Pariona
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [`Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO2.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO2.md)

---

### 📋 Resumen del PR

Este Pull Request implementa de forma completa el **Módulo 1 de MediFlow (Autenticación, Usuarios y Control de Acceso por Roles - RF-01 al RF-05)**. Habilita la autenticación de los trabajadores mediante número de documento de identidad de 8 cifras (DNI por el momento) y contraseña, la gestión CRUD de usuarios desde el rol `ADMINISTRADOR` (creación, edición, activación/desactivación y asignación de roles) y la restricción RBAC de pestañas e interfaces para los 4 actores principales: `ADMINISTRADOR`, `OPERADOR`, `AUDITOR` y `SUPERVISOR`.

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones
1. **Migración Alembic `h1i202255de7`**:
   - Creación de ENUMs `rol_enum` (`'ADMINISTRADOR'`, `'OPERADOR'`, `'AUDITOR'`, `'SUPERVISOR'`) y `estado_usuario_enum` (`'ACTIVO'`, `'INACTIVO'`).
   - Tabla `usuarios` con campos `documento_identidad` (VARCHAR(8) UNIQUE NOT NULL), `password_hash`, `salt`, `nombres`, `apellidos`, `correo`, `telefono`, `rol` y `estado`.
   - Comentarios explicativos SQL (`COMMENT ON TABLE` y `COMMENT ON COLUMN`).
   - Semilla de 4 usuarios iniciales de prueba (Admin `12345678`, Operador `87654321`, Auditor `11223344`, Supervisor `44332211`).

#### ⚙️ Backend & Agente IA
2. **Seguridad y Passwords (`security.py`)**: Hashing PBKDF2-HMAC-SHA256 con salt aleatorio de 128 bits y gestión de sesiones de token.
3. **Repositorio asyncpg (`user_repository.py`)**: Persistencia asíncrona de usuarios. Pool global expuesto en `postgres_storage.py`.
4. **Router Auth (`/api/v1/auth`)**: Endpoints `/login` (validación DNI 8 cifras), `/logout` y `/me`.
5. **Router Users (`/api/v1/users`)**: Endpoints `/users` (GET, POST, PUT) restringidos al rol `ADMINISTRADOR`.
6. **Unit Tests (`test_auth_api.py`)**: 4 nuevas pruebas automáticas (21/21 pytest passing).

#### 🎨 Frontend & UX
7. **Cliente API Auth (`auth.api.ts`)**: Métodos `loginUser`, `logoutUser`, `getCurrentUser`, `fetchUsers`, `createNewUser`, `updateUserDetails`.
8. **Interfaz React (`App.tsx`)**: Modal de Login con validación 8 cifras DNI, accesos rápidos por rol, perfil de usuario en header, navegación por pestañas restringida por rol (RF-05) y panel completo de Administración de Usuarios.
9. **Estilos CSS (`App.css`)**: Estilos visuales para overlay de login, badges de rol y tabla de usuarios.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Nuevo** | `backend/alembic/versions/h1i202255de7_add_auth_and_user_management.py` | Migración Alembic para la tabla `usuarios` y roles. |
| **Nuevo** | `backend/app/core/security.py` | Módulo de hashing PBKDF2 y manejo de sesiones. |
| **Nuevo** | `backend/app/repositories/user_repository.py` | Repositorio asyncpg para persistencia de usuarios. |
| **Nuevo** | `backend/app/api/v1/auth.py` | API REST para inicio y cierre de sesión. |
| **Nuevo** | `backend/app/api/v1/users.py` | API REST para administración de usuarios y roles. |
| **Nuevo** | `backend/tests/test_auth_api.py` | Pruebas unitarias para autenticación y usuarios. |
| **Nuevo** | `frontend/src/api/auth.api.ts` | Cliente API de autenticación y usuarios. |
| **Nuevo** | `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO2.md` | Registro detallado del Módulo 1 (Auth & RBAC). |
| **Modificado** | `backend/app/main.py` | Registro de los routers `auth` y `users`. |
| **Modificado** | `backend/app/repositories/postgres_storage.py` | Exportación de `get_db_pool()`. |
| **Modificado** | `frontend/src/App.tsx` | Login Modal, RBAC nav tabs, Header badge y Vista Usuarios. |
| **Modificado** | `frontend/src/App.css` | Estilos CSS para auth modal, roles badges y users table. |
| **Modificado** | `Docs/HISTORIAL_CAMBIOS.md` | Actualización del Índice Maestro de Cambios. |
| **Modificado** | `Docs/PULL_REQUEST.md` | Actualización del Índice Maestro de Pull Requests. |

---

### 🏆 Checklist de la Regla de Oro
- [x] **PostgreSQL Fuente Única de Verdad**: Tabla `usuarios` con roles ENUM y contraseñas hasheadas en `mediflow_dev`.
- [x] **Control 100% Manual de Almacenamiento**: Opción LOCAL/OCI sin alteración automática.
- [x] **Pytest 100% Passing**: 21/21 pruebas unitarias pasadas en 1.03s.
- [x] **Frontend Clean Build**: `npm run build` compila exitosamente en 175ms sin errores TypeScript.
- [x] **Migraciones Alembic Sincronizadas**: Base de datos en `h1i202255de7`.

---

### 🧪 Verificación y Pruebas
1. `cd backend && .venv\Scripts\python.exe -m alembic upgrade head`
2. `cd backend && .venv\Scripts\python.exe -m pytest tests`
3. `cd frontend && npm run build`
