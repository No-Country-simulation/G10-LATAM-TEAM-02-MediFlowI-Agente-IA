# 📜 Historial de Cambios — 2026-09-25 (CAMBIO3)

**Fecha**: 2026-09-25  
**Identificador de Cambio**: CAMBIO3  
**Autor**: Erick Pariona  
**Sprint / Fase**: Módulo 1 — Autenticación y RBAC / Depuración de Advertencias Pydantic v2  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
En esta iteración se corrigieron las advertencias de deprecación (`PydanticDeprecatedSince20`) asociadas al uso directo de `example="..."` en modelos Pydantic v2 dentro del Backend (`/auth` y `/users`). Se actualizó el esquema OpenAPI al uso recomendado `json_schema_extra={"example": ...}`, logrando un resultado de pruebas en pytest 100% pasando sin advertencias ni regresiones.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
- **Estado de Sincronización**: Manteniendo la migración `h1i202255de7_add_auth_and_user_management.py` activa en `mediflow_dev`. No se requirieron cambios en esquemas SQL.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
1. **Esquema de Autenticación (`backend/app/api/v1/auth.py`)**:
   - **Cambio técnico**: Reemplazado `example="..."` por `json_schema_extra={"example": ...}` en el modelo Pydantic `LoginRequest`.
2. **Esquema de Usuarios (`backend/app/api/v1/users.py`)**:
   - **Cambio técnico**: Reemplazado `example="..."` por `json_schema_extra={"example": ...}` en el modelo Pydantic `UserCreateRequest`.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
- **Verificación**: Compilación con TypeScript y Vite ejecutada en 146ms limpiamente con 0 errores.

### 🐳 4. Infraestructura, Scripts & Documentación
- **Generación de Historial y PR**: Generados los documentos de auditoría `HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md` y `PULL_REQUEST_2026-09-25_PR3.md`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: `21 passed in 1.27s` (0 warnings).
- **Frontend (TypeScript)**: `npm run build` exitoso en 146ms.
- **Migraciones (Alembic)**: `alembic upgrade head` sincronizado en `h1i202255de7`.
