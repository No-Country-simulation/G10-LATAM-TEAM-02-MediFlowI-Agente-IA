# 📜 Historial de Cambios — 2026-09-25 (CAMBIO2)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO2  
**Autor**: Erick Pariona  
**Sprint / Fase**: Módulo 1 — Autenticación, Usuarios (DNI 8 Cifras) & Control de Acceso RBAC (RF-01 al RF-05)  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Implementación completa del **Módulo 1: Autenticación, Gestión de Usuarios y Control de Acceso por Roles (RBAC)** en MediFlow. Se habilitó el inicio de sesión con documento de identidad de 8 cifras (DNI por el momento), la invalidación de token en cierre de sesión, la gestión completa de trabajadores de la clínica (creación, edición, activación/desactivación y asignación de roles) y la restricción estricta de navegación e interfaz para los 4 roles del sistema: `ADMINISTRADOR`, `OPERADOR`, `AUDITOR` y `SUPERVISOR`.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **Migración `h1i202255de7` (`h1i202255de7_add_auth_and_user_management.py`)**:
   - **Tipos ENUM**: Creación de `rol_enum` (`'ADMINISTRADOR'`, `'OPERADOR'`, `'AUDITOR'`, `'SUPERVISOR'`) y `estado_usuario_enum` (`'ACTIVO'`, `'INACTIVO'`).
   - **Tabla `usuarios`**: Creación de la tabla con campos `id` (UUID), `documento_identidad` (VARCHAR(8) UNIQUE NOT NULL), `password_hash`, `salt`, `nombres`, `apellidos`, `correo`, `telefono`, `rol` y `estado`.
   - **Comentarios PostgreSQL**: `COMMENT ON TABLE` y `COMMENT ON COLUMN` para la tabla y todos sus atributos.
   - **Semilla de Usuarios Iniciales**: Carga de 4 usuarios por defecto (DNI `12345678` - Admin, `87654321` - Operador, `11223344` - Auditor, `44332211` - Supervisor).
   - **Sincronización**: `alembic upgrade head` ejecutado exitosamente.

### ⚙️ 2. Backend & Agente IA (FastAPI / Python)
2. **Módulo de Seguridad (`backend/app/core/security.py`)**:
   - Hashing seguro de contraseñas mediante PBKDF2-HMAC-SHA256 con salt aleatorio de 128 bits.
   - Creación, validación e invalidación de tokens de sesión de usuario (`mf_session_*`).
   - Dependencia `require_api_key` mantenida para compatibilidad de triaje.
3. **Repositorio de Usuarios (`backend/app/repositories/user_repository.py`)**:
   - Consultas asíncronas con `asyncpg` (`get_user_by_document`, `get_user_by_id`, `list_all_users`, `create_user`, `update_user`).
   - Función global `get_db_pool()` agregada en `postgres_storage.py` para compartir el pool de conexiones.
4. **API Router de Autenticación (`backend/app/api/v1/auth.py`)**:
   - `POST /api/v1/auth/login`: **RF-01** — Valida DNI de 8 cifras y contraseña.
   - `POST /api/v1/auth/logout`: **RF-02** — Destruye e invalida el token de sesión.
   - `GET /api/v1/auth/me`: Retorna los datos y rol del usuario autenticado.
5. **API Router de Usuarios y Roles (`backend/app/api/v1/users.py`)**:
   - `GET /api/v1/users`: **RF-03 & RF-04** — Lista trabajadores registrados (restringido a `ADMINISTRADOR`).
   - `POST /api/v1/users`: **RF-03** — Registra nuevos trabajadores validando 8 cifras de DNI.
   - `PUT /api/v1/users/{id}`: **RF-03 & RF-04** — Edita datos, cambia rol o altera estado (`ACTIVO`/`INACTIVO`).
6. **Pruebas Unitarias (`backend/tests/test_auth_api.py`)**:
   - 4 nuevas pruebas para login exitoso con DNI 8 cifras, rechazo de formato inválido, contraseña errónea y logout (21/21 pytest passing).

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
7. **Cliente API Auth (`frontend/src/api/auth.api.ts`)**:
   - Métodos `loginUser`, `logoutUser`, `getCurrentUser`, `fetchUsers`, `createNewUser`, `updateUserDetails`.
8. **Componente Principal (`frontend/src/App.tsx`)**:
   - **Login Screen / Modal (RF-01)**: Formulario de ingreso con input restringido a 8 cifras de DNI y contraseña. Botones de acceso rápido para los 4 roles.
   - **User Profile Badge & Logout (RF-02)**: Muestra nombres, DNI de 8 cifras, badge de rol con colores distintivos y botón de cerrar sesión en la cabecera.
   - **Restricción de Navegación por Rol (RF-05)**:
     - `Dashboard`: Visible para Admin, Operador, Auditor y Supervisor.
     - `Cargar Documentos`: Visible únicamente para Admin y Operador.
     - `Auditoría HITL`: Visible para Admin, Auditor y Supervisor (modo lectura).
     - `Gestión de Usuarios`: Visible únicamente para Admin.
     - `Configuración`: Visible únicamente para Admin.
   - **Vista de Gestión de Usuarios (`users`) (RF-03 & RF-04)**: Tabla interactiva para administrar trabajadores, alternar estados `ACTIVO`/`INACTIVO` y cambiar roles sobre la marcha.
9. **Estilos CSS (`frontend/src/App.css`)**:
   - Clases para `.login-overlay`, `.login-card`, `.quick-users-grid`, `.user-profile-badge`, `.role-administrador`, `.role-operador`, `.role-auditor`, `.role-supervisor`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: 21/21 pasados en 1.03s (`pytest tests`).
- **Frontend (TypeScript)**: Compilación limpia en 175ms (`npm run build`).
- **Migraciones (Alembic)**: Sincronizado a `h1i202255de7`.
