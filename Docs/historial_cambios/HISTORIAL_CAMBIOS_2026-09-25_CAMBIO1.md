# 📜 Historial de Cambios — 2026-09-25 (CAMBIO1)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO1  
**Autor**: Erick Pariona  
**Sprint / Fase**: Sprint 2 — Setup Entorno Local, Dependencias AsyncIO & Frontend Setup  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Configuración y puesta a punto del entorno local de desarrollo para backend y frontend sin Docker. Se agregaron las dependencias requeridas para soporte asíncrono en PostgreSQL con SQLAlchemy (`greenlet`), se configuraron los archivos de variables de entorno `.env` en `backend/` y `frontend/`, y se validó el paso de migraciones de Alembic e instalación de módulos de Node.js.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **Configuración de Conexión Local y Migraciones**:
   - **Configuración**: Actualización de la URL de conexión en `backend/.env` a `postgresql+asyncpg://postgres:sistemas@localhost:5432/mediflow_dev`.
   - **Ejecución**: Ejecución exitosa de `alembic upgrade head` hasta la revisión `g9h001143cd6 (head)`.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
2. **Dependencias de AsyncIO y Grafo LangGraph** (`backend/pyproject.toml`):
   - **Cambio técnico**: Incorporación explícita de `"greenlet>=3.0.0"` y `"sqlalchemy[asyncio]>=2.0.0"` a las dependencias de `pyproject.toml` para resolver compatibilidad en Python 3.14 con SQLAlchemy asyncio.
   - **Instalación de paquetes**: Instalación completa de `langgraph`, `langchain`, `google-genai` y dependencias asociadas en el entorno virtual `.venv`.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
3. **Setup de Variables de Entorno e Instalación** (`frontend/.env`, `frontend/package-lock.json`):
   - **Configuración**: Creación de `frontend/.env` definiendo `VITE_API_URL=http://localhost:8000`.
   - **Instalación de paquetes**: Ejecución de `npm install` (70 paquetes auditados) y verificación de compilación limpia con `npm run build` (0 errores de TypeScript en 740ms).

### 🐳 4. Infraestructura, Scripts & Documentación
4. **Archivos de Entorno e Índices**:
   - **Configuración**: Creación de `backend/.env` y `frontend/.env` (ambos excluidos por `.gitignore`).
   - **Documentación**: Actualización del índice maestro `Docs/HISTORIAL_CAMBIOS.md` y `Docs/PULL_REQUEST.md`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: Dependencias e importaciones validadas (`import app.main` exitoso).
- **Frontend (TypeScript)**: `npm run build` ejecutado en 740ms sin errores.
- **Migraciones (Alembic)**: `alembic upgrade head` sincronizado en `g9h001143cd6 (head)`.
