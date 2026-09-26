# 📜 Historial de Cambios — 2026-09-25 (CAMBIO5)

**Fecha**: 2026-09-25  
**Identificador de Cambio**: CAMBIO5  
**Autor**: Erick Pariona  
**Sprint / Fase**: Rediseño UX/UI — Configuración de Almacenamiento & Pestañas de Navegación  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Se corrigieron las interferencias de estilos producidas por la integración de Bootstrap en `frontend/src/App.css`. Se aplicó una reestructuración de reglas CSS con alta especificidad para alinear a la izquierda el texto de las tarjetas de almacenamiento (`LOCAL` vs `OCI`), mejorar la jerarquía visual de las credenciales y badges de estado, y destacar activamente los botones de pestañas superiores (`Triaje Clínico`, `Gestión de Usuarios`, `Configuración`).

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🎨 1. Frontend & UX (React / Vite / TypeScript / CSS)
1. **Rediseño de Vista de Configuración (`src/App.css`)**:
   - Ajustada la grilla `.storage-options-grid` para mostrar las opciones en tarjetas de 2 columnas responsivas.
   - Forzada la alineación a la izquierda (`text-align: left !important`) para títulos, descripciones (`.storage-desc`), cajas de ruta (`.storage-path-info`) y badges (`.storage-status-badge`).
   - Aplicados colores distintivos y efectos *hover* activos a la opción de almacenamiento seleccionada.
2. **Mejora de Pestañas de Navegación Superior (`.nav-tabs`, `.nav-tab-btn`)**:
   - Sobrescritas las reglas por defecto de Bootstrap en `.nav-tabs` y `.nav-tab-btn.active`.
   - Se destaca la pestaña activa con fondo primario `#0284c7`, texto blanco y sombra suave.

### 🐳 2. Infraestructura & Documentación
- **Documentación de Auditoría**: Creados `HISTORIAL_CAMBIOS_2026-09-25_CAMBIO5.md` y `PULL_REQUEST_2026-09-25_PR5.md`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: `21 passed in 0.97s` (100% passing).
- **Frontend (TypeScript / Vite)**: `npm run build` compilación limpia en **380ms** con 0 errores.
- **Migraciones (Alembic)**: `alembic upgrade head` sincronizado en `h1i202255de7`.
