# 🚀 Pull Request — [FECHA: AAAA-MM-DD]

Este documento registra los Pull Requests generados el día **[FECHA: AAAA-MM-DD]** para el proyecto **MediFlow**. Si se realizan múltiples PRs en el mismo día, se enumeran de forma incremental (`PR #1`, `PR #2`, etc.).

---

## 🔀 PR #1 — [Título del PR]

### 📌 Datos del Pull Request
- **Fecha**: [AAAA-MM-DD]
- **Autor**: [Nombre del Autor]
- **Rama de Origen**: `[rama-origen]`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

---

### 📋 Resumen del PR
[Descripción concisa del propósito del PR, funcionalidades añadidas, correcciones de errores o refactorizaciones]

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones
- [Detalle de cambios en BD y Alembic]

#### ⚙️ Backend & Agente IA
- [Detalle de cambios en FastAPI, LangGraph, Pydantic, etc.]

#### 🎨 Frontend & UX
- [Detalle de cambios en React, Vite, CSS, TypeScript]

#### 🐳 Infraestructura & Documentación
- [Detalle de cambios en Docker, Makefile, docs]

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Nuevo / Modificado** | `[ruta/al/archivo]` | [Descripción breve del cambio] |

---

### 🏆 Checklist de la Regla de Oro
- [ ] **PostgreSQL es la Fuente Única de Verdad**: Persistencia garantizada en `mediflow_dev`.
- [ ] **Control 100% Manual de Almacenamiento**: Selección LOCAL/OCI controlada manualmente por el usuario.
- [ ] **Pruebas Backend Passing**: `pytest` 100% exitoso sin mutar `mediflow_dev`.
- [ ] **Compilación Frontend Limpia**: `npm run build` sin errores de TypeScript.
- [ ] **Migraciones Alembic Sincronizadas**: Base de datos en `alembic upgrade head`.

---

### 🧪 Verificación y Pruebas
1. `make db && make migrate`
2. `pytest backend/tests`
3. `cd frontend && npm run build`
