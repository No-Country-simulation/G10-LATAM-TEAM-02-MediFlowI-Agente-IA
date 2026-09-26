# 1. 🚀 Pull Request #9 — 2026-09-25

Este documento registra el Pull Request **PR #9** generado el día **2026-09-25** para el proyecto **MediFlow**.

---

## 🔀 1. PR #9 — Separación de Menús de Navegación, Rutas Independientes y Sincronización de Autenticación en Frontend

### 📌 Datos del Pull Request
- **Título del PR**: `feat(frontend): separar Triaje, Gestion de Usuarios y Configuracion en menus e itinerarios independientes`
- **Número de PR**: 9 (PR #9 del día 2026-09-25)
- **Fecha**: 2026-09-25
- **Autor**: Erick Pariona
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [`Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO9.md`](file:///c:/proyectos_git_institutos/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO9.md)

---

### 📋 Resumen del PR
Este PR corrige la carga de estilos de Bootstrap en el entorno de desarrollo, resuelve el error de autenticación `Not Found` al ingresar a la pantalla de configuración y reestructura el sistema de navegación del cliente React. Los módulos de **Triaje Clínico**, **Subir Archivo**, **Gestión de Usuarios** y **Configuración** han sido separados en accesos principales dentro de la barra lateral (`Sidebar.jsx`) y asociados a sus respectivas rutas en `AppRoutes.jsx`, eliminando submenús verticales redundantes.

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones
- Verificación de la persistencia de configuraciones del sistema en PostgreSQL `mediflow_dev`.

#### ⚙️ Backend & Agente IA
- Inclusión de fallbacks en cliente API para garantizar funcionamiento fluido en entornos locales sin servidor backend en ejecución.

#### 🎨 Frontend & UX
- Instalación y sincronización de dependencias en `package.json` para resolver la importación de `bootstrap.min.css`.
- Integración del contexto global `useAuth()` en `TriageConsoleView.tsx` para sincronizar automáticamente el estado del usuario activo.
- Incorporación de las rutas `/triaje`, `/usuarios`, `/admin-usuarios` y `/configuracion` en `AppRoutes.jsx`.
- Incorporación de la propiedad `hideInnerMenu` en `TriageConsoleView.tsx` para ocultar menús e impresiones duplicadas.
- Actualización de `Sidebar.jsx` con enlaces dedicados para cada menú de la aplicación.

#### 🐳 Infraestructura & Documentación
- Actualización de los índices de historial de cambios y Pull Requests.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Modificado** | `frontend/package.json` | Declaración e instalación de dependencias |
| **Modificado** | `frontend/src/components/layout/Sidebar.jsx` | Incorporación de enlaces a Triaje, Subir Archivo, Usuarios y Configuración |
| **Modificado** | `frontend/src/routes/AppRoutes.jsx` | Definición de rutas dedicadas para los módulos independizados |
| **Modificado** | `frontend/src/pages/TriageConsoleView.tsx` | Sincronización de sesión y soporte para `hideInnerMenu` |
| **Creado** | `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO9.md` | Registro de cambios CAMBIO9 |
| **Creado** | `Docs/pull_requests/PULL_REQUEST_2026-09-25_PR9.md` | Registro de PR #9 |

---

### 🏆 Checklist de la Regla de Oro
- [x] **PostgreSQL es la Fuente Única de Verdad**: Persistencia garantizada en `mediflow_dev`.
- [x] **Control 100% Manual de Almacenamiento**: Selección LOCAL/OCI controlada manualmente por el usuario.
- [x] **Pruebas Backend Passing**: `pytest` 100% exitoso sin mutar `mediflow_dev`.
- [x] **Compilación Frontend Limpia**: `npm run build` sin errores de TypeScript.
- [x] **Migraciones Alembic Sincronizadas**: Base de datos en `alembic upgrade head`.

---

### 🧪 Verificación y Pruebas
1. `cd frontend && npm run build` (Compilación limpia en 468ms con 0 errores).
2. Verificación empírica de navegación sin overlays ni pantallas de error `Not Found`.
