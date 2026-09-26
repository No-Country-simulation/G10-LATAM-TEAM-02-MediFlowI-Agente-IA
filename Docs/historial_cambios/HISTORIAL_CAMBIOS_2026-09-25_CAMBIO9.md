# 📜 Historial de Cambios — 2026-09-25 (CAMBIO9)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO9  
**Autor**: Erick Pariona  
**Sprint / Fase**: Sprint 2 — Frontend UI/UX, Navegación Independiente & Sincronización de Autenticación  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
En esta jornada de trabajo se resolvieron problemas de importación de estilos Bootstrap, se solucionó el fallo de autenticación `Not Found` al ingresar al módulo de configuración, y se reestructuró por completo la navegación del frontend. Los módulos de **Triaje Clínico**, **Subir Archivo**, **Gestión de Usuarios** y **Configuración** fueron independizados en la barra lateral principal (`Sidebar.jsx`), removiendo menús internos duplicados para garantizar una interfaz limpia, responsiva y accesible.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **Sincronización de Preferencias de Almacenamiento**:
   - **Propósito**: Garantizar que las configuraciones de almacenamiento (`LOCAL` vs `OCI`) se mantengan sincronizadas y persistentes en la tabla `configuracion_sistema` de PostgreSQL `mediflow_dev` sin alterar valores de forma automática.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
2. **Resguardo de Endpoints de Configuración y Autenticación**:
   - **Cambio técnico**: Se mejoró el manejo de respuestas en el frontend ante llamadas a los endpoints `/api/v1/settings` y `/api/v1/auth/me`, ofreciendo valores de resguardo (fallbacks) cuando el servidor de backend o la base de datos se encuentren en entornos de prueba locales offline.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
3. **Resolución de Importación Bootstrap** (`frontend/package.json` y `package-lock.json`):
   - **Cambio de UI**: Instalación y verificación de dependencias de `bootstrap` para resolver la carga de `bootstrap/dist/css/bootstrap.min.css` en [main.tsx](file:///c:/proyectos_git_institutos/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/frontend/src/main.tsx#L3).
4. **Sincronización de Autenticación Global** (`frontend/src/pages/TriageConsoleView.tsx`):
   - **Cambio de Estado**: Integración del hook `useAuth()` proveniente de `AuthContext.jsx` para evitar que la vista de la consola muestre una segunda ventana modal de login o la alerta `Not Found` al abrir la pestaña de configuración.
5. **Independización de Menús y Rutas** (`frontend/src/components/layout/Sidebar.jsx` y `frontend/src/routes/AppRoutes.jsx`):
   - **Navegación**: Separación de las opciones en el menú lateral principal (**Dashboard**, **Triaje Clínico**, **Subir Archivo**, **Gestión de Usuarios**, **Configuración**, **Auditoría**, **Historial**).
   - **Prop `hideInnerMenu`**: Implementación de la propiedad `hideInnerMenu` en `TriageConsoleView` para ocultar la sub-tarjeta duplicada *"MENÚ DE CONSOLA"* y los encabezados redundantes al estar embebido dentro del `MainLayout`.

### 🐳 4. Infraestructura, Scripts & Documentación
6. **Actualización de Índices Maestros y Documentación de PRs** (`Docs/`):
   - **Configuración**: Registro incremental de cambios en los archivos maestros `HISTORIAL_CAMBIOS.md` y `PULL_REQUEST.md`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: `100% de pruebas pasando sin mutar la base de datos de desarrollo mediflow_dev.`
- **Frontend (TypeScript)**: `npm run build ejecuto limpiamente en 468ms con 0 errores de TypeScript.`
- **Migraciones (Alembic)**: `Base de datos sincronizada en alembic upgrade head.`
