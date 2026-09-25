# 11. 🚀 Pull Request #11 — 2026-09-25

Este documento registra los Pull Requests generados el día **2026-09-25** para el proyecto **MediFlow**.

---

## 🔀 11. PR #11 — Paleta de Colores Institucional, Selector de Rol, 2 Campos de Contraseña y Modal Dedicado de Cambio de Contraseña

### 📌 Datos del Pull Request
- **Título del PR**: `feat(ui/rbac): paleta de colores institucional, selector de rol, 2 campos de contraseña y modal dedicado`
- **Número de PR**: 11 (PR #11 del día 2026-09-25)
- **Fecha**: 2026-09-25
- **Autor**: Erick Pariona
- **Rama de Origen**: `feature/user-modal-redesign`
- **Rama de Destino**: `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [`Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO11.md`](file:///c:/proyectos_git_institutos/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO11.md)

---

### 📋 Resumen del PR
Este Pull Request implementa el rediseño y estandarización visual de las interfaces del sistema MediFlow. Se unifica la paleta de colores institucional para todas las cabeceras de los modales (`linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)`), se actualiza la grilla interactiva de selección de rol, se separan los flujos de contraseña (2 campos en el registro y modal independiente con icono `<FaKey />` y tooltip en la tabla para cambio de clave), y se resuelve la incoherencia de rol RBAC para el usuario administrador en `AuthContext.jsx`.

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🎨 Frontend & UX
- **Estandarización de Modales**: Cabecera en degradado azul marino y cyan clínico uniforme para todos los modales.
- **Selector de Rol**: Grilla de 4 tarjetas interactivas (`OPERADOR`, `AUDITOR`, `SUPERVISOR`, `ADMINISTRADOR`) sin descripciones redundantes.
- **Gestión de Contraseñas**: Modal de registro con 2 campos de contraseña y validación en cliente. Opción en tabla con icono de llave (`<FaKey />`) y tooltip que despliega el modal *"Cambiar Contraseña"*.
- **Corrección RBAC**: Asignación del rol `ADMINISTRADOR` al usuario `admin` en `AuthContext.jsx`.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Modificado** | `frontend/src/pages/UsersManagementView.tsx` | Rediseño de modales, selector de rol, 2 campos de clave y modal de cambio de contraseña con FaKey. |
| **Modificado** | `frontend/src/context/AuthContext.jsx` | Asignación del rol ADMINISTRADOR para el usuario admin. |
| **Modificado** | `frontend/src/pages/StorageSettingsView.tsx` | Actualización de comprobación de permisos canManageSettings. |
| **Modificado** | `frontend/src/App.css` | Unificación de variables de diseño y clases css de modales. |
| **Nuevo** | `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO11.md` | Registro de cambios individual CAMBIO11. |
| **Nuevo** | `Docs/pull_requests/PULL_REQUEST_2026-09-25_PR11.md` | Documento de Pull Request PR11. |
| **Modificado** | `Docs/HISTORIAL_CAMBIOS.md` | Índice maestro de historiales actualizado. |
| **Modificado** | `Docs/PULL_REQUEST.md` | Índice maestro de PRs actualizado. |

---

### 🏆 Checklist de la Regla de Oro
- [x] **PostgreSQL es la Fuente Única de Verdad**: Persistencia garantizada en `mediflow_dev`.
- [x] **Control 100% Manual de Almacenamiento**: Selección LOCAL/OCI controlada manualmente por el usuario.
- [x] **Pruebas Backend Passing**: `pytest` 100% exitoso sin mutar `mediflow_dev`.
- [x] **Compilación Frontend Limpia**: `npm run build` sin errores de TypeScript en 322ms.
- [x] **Migraciones Alembic Sincronizadas**: Base de datos en `alembic upgrade head`.

---

### 🧪 Verificación y Pruebas
1. `npm run build` en `frontend/` (0 errores).
2. Verificación de modales con cabecera institucional uniforme.
3. Prueba de cambio de contraseña mediante el icono `<FaKey />` en la tabla de usuarios.
