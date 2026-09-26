# 📜 Historial de Cambios — 2026-09-25 (CAMBIO10)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO10  
**Autor**: Erick Pariona  
**Sprint / Fase**: Sprint 2 — Modal de Usuarios, Estilizado de Combos y Menú de Documentación  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
En este cambio se implementó el Modal flotante para crear/editar usuarios, se mejoró el estilizado de todos los elementos `<select>` (combos) del sistema, se resolvió la persistencia en la tabla de gestión de usuarios en caso de falta de conexión al backend utilizando una lista por defecto local (`DEFAULT_USERS_LIST`), y se creó la vista/página de **Documentación** (`/documentacion`) incorporando en primer lugar el detalle exhaustivo del control de acceso basado en roles (RBAC) y la matriz de permisos.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🎨 1. Frontend & UX (React / Vite / TypeScript / CSS)
1. **Modal de Crear/Editar Usuario y Lista de Usuarios por Defecto** (`frontend/src/pages/TriageConsoleView.tsx`):
   - Se reemplazó el formulario integrado anterior por un Modal emergente (`isUserModalOpen`, `editingUser`) activado por el botón `+ Registrar Nuevo Usuario` y los botones de acción `Editar` por fila.
   - Se añadió `DEFAULT_USERS_LIST` como respaldo seguro ante desconexiones de la API FastAPI.
2. **Estilizado de Combos Select** (`frontend/src/App.css`):
   - Se incorporaron clases CSS personalizadas (`.form-select`, `.select-role-change`, `.modal-overlay`) garantizando un diseño limpio, profesional e integrado a la estética médica.
3. **Página de Documentación de Usuarios y Roles (RBAC)** (`frontend/src/pages/DocumentationView.tsx`):
   - Se creó la página completa con pestañas para Usuarios y Roles (RBAC), Triaje IA y Almacenamiento.
   - Se detallaron las capacidades y permisos explícitos de los roles `ADMINISTRADOR`, `OPERADOR`, `AUDITOR` y `SUPERVISOR`.
4. **Enrutamiento y Menú Lateral** (`frontend/src/routes/AppRoutes.jsx`, `frontend/src/components/layout/Sidebar.jsx`):
   - Se agregó la ruta `/documentacion` y el ítem **Documentación** en el menú vertical principal con ícono `FaBook`.

---

## 🧪 Verificación y Pruebas
- **Frontend (TypeScript)**: `npm run build` ejecutado exitosamente con 0 errores de TypeScript.
- **Backend (Pytest)**: Sin modificaciones en backend.
- **Migraciones (Alembic)**: `alembic upgrade head` sincronizado.
