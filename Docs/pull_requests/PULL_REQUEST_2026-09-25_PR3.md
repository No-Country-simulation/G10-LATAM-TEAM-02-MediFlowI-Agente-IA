# 🚀 Pull Request #3 — [FECHA: 2026-09-25]

Este documento registra el Pull Request #3 generado el día **2026-09-25** para el proyecto **MediFlow**.

---

## 🔀 1. PR #3 — Refactor de esquemas Pydantic v2 y eliminación de advertencias en Backend

### 📌 Datos del Pull Request
- **Título del PR**: `fix(backend): actualizar esquemas Pydantic v2 con json_schema_extra y eliminar advertencias de deprecacion`
- **Número de PR**: 3 (PR #3 del día 2026-09-25)
- **Fecha**: 2026-09-25
- **Autor**: Erick Pariona
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [`Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md)

---

## 📋 Resumen del PR
Este PR realiza una refactorización menor pero crítica en la capa del Backend FastAPI para adaptar las definiciones de modelos `Field(...)` en Pydantic V2. Se reemplazó el argumento en desuso `example` por `json_schema_extra={"example": ...}`, logrando que el suite de pruebas en `pytest` ejecute de forma 100% limpia sin advertencias ni regresiones en las respuestas JSON.

---

## 🛠️ Cambios Detallados por Capa Técnica

### 🗄️ Base de Datos & Migraciones
- Sin cambios en la base de datos (PostgreSQL 17 sincronizado en la versión `h1i202255de7`).

### ⚙️ Backend & Agente IA
- Se actualizaron las clases Pydantic `LoginRequest` en `app/api/v1/auth.py` y `UserCreateRequest` en `app/api/v1/users.py` utilizando `json_schema_extra`.

### 🎨 Frontend & UX
- Se mantuvo el build de Vite y TypeScript 100% funcional.

### 🐳 Infraestructura & Documentación
- Registro incremental en `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md` y `Docs/pull_requests/PULL_REQUEST_2026-09-25_PR3.md`.

---

## 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Modificado** | `backend/app/api/v1/auth.py` | Migración de `example` a `json_schema_extra` en `LoginRequest` |
| **Modificado** | `backend/app/api/v1/users.py` | Migración de `example` a `json_schema_extra` en `UserCreateRequest` |
| **Nuevo** | `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md` | Registro de cambios incremental CAMBIO3 del 2026-09-25 |
| **Nuevo** | `Docs/pull_requests/PULL_REQUEST_2026-09-25_PR3.md` | Registro de PR #3 del 2026-09-25 |

---

## 🏆 Checklist de la Regla de Oro
- [x] **PostgreSQL es la Fuente Única de Verdad**: Persistencia de usuarios en `mediflow_dev`.
- [x] **Control 100% Manual de Almacenamiento**: No mutación de preferencias OCI/LOCAL.
- [x] **Pruebas Backend Passing**: `21 passed in 1.27s` (0 warnings).
- [x] **Compilación Frontend Limpia**: `npm run build` en 146ms.
- [x] **Migraciones Alembic Sincronizadas**: Alembic en `h1i202255de7`.

---

## 🧪 Verificación y Pruebas
1. `.venv\Scripts\python.exe -m pytest` (21 passed)
2. `npm run build` (0 errores)
