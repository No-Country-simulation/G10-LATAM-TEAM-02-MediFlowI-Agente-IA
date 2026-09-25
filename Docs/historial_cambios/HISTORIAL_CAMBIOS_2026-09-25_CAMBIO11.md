# 📜 Historial de Cambios — 2026-09-25 (CAMBIO11)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO11  
**Autor**: Erick Pariona  
**Sprint / Fase**: Sprint 2 — Módulo de Gestión de Usuarios, RBAC & Paleta de Colores Institucional  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Se implementó un rediseño integral de UX/UI en el módulo de gestión de usuarios (`UsersManagementView.tsx`), estandarizando el sistema de color institucional, introduciendo un selector interactivo de rol por tarjetas, dividiendo el cambio de contraseña en un modal dedicado accesible mediante icono de llave (`FaKey`) con tooltip en la tabla de acciones, y corrigiendo el perfil de permisos RBAC del usuario administrador en `AuthContext.jsx`.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🎨 1. Frontend & UX (React / Vite / TypeScript / CSS)
1. **Rediseño Institucional de Modales & Paleta Unificada** (`frontend/src/pages/UsersManagementView.tsx`, `frontend/src/App.css`):
   - Se estableció la paleta institucional médica basada en el degradado primario `linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)` para las cabeceras de todos los modales del sistema.
   - Estandarización de botones primarios (`btn-primary`), semáforos de estado (Verde: Activo, Ámbar: Advertencia/HITL, Rojo: Desactivado/Urgencia) y tarjetas neutras clínicas.

2. **Formulario de Registro & Selector Interactivo de Rol**:
   - Tarjetas seleccionables de rol (`OPERADOR`, `AUDITOR`, `SUPERVISOR`, `ADMINISTRADOR`) con icono contextual, marca de verificación `✓` y estado activo dinámico.
   - Eliminación de explicaciones extensas dentro de los selectores para mantener una interfaz limpia y sobria.
   - Incorporación de dos campos de contraseña (`Contraseña Inicial` y `Confirmar Contraseña`) en el modal de registro con validación estricta de coincidencia.

3. **Independización del Flujo de Cambio de Contraseña**:
   - Removidos los campos de contraseña del modal de edición de datos personales del trabajador.
   - Agregada una opción en la columna de Acciones de la tabla con el icono de llave (`<FaKey />`), tono de advertencia y tooltip interactivo *"Cambiar contraseña de usuario"*.
   - Creación del modal dedicado *"Cambiar Contraseña"* con 2 campos de entrada y botón de actualización unificado.

4. **Corrección de Autenticación & Permisos RBAC** (`frontend/src/context/AuthContext.jsx`, `frontend/src/pages/StorageSettingsView.tsx`):
   - Corrección del rol del usuario demo `admin` a `ADMINISTRADOR` en `AuthContext.jsx` (previamente asignado como `AUDITOR_LEAD`), solucionando el mensaje de *"Acceso Restringido (RBAC: RF-05)"*.
   - Ampliación de las comprobaciones de permisos `canManageUsers` y `canManageSettings` para reconocer `ADMINISTRADOR`, `ADMIN` y la cuenta principal `admin`.

---

## 🧪 Verificación y Pruebas
- **Frontend (TypeScript)**: `npm run build` ejecutado en 322ms con **0 errores de compilación**.
- **Backend (Pytest)**: Pruebas `pytest` 100% passing sin mutar `mediflow_dev`.
- **Base de Datos (Alembic)**: Sincronizada en `alembic upgrade head`.
