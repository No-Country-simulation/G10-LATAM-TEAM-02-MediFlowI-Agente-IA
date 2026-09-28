# 📜 Historial de Cambios — 2026-09-28 (CAMBIO1)

**Fecha**: 28/09/2026 *(Fecha generada automáticamente por el Agente)*  
**Identificador de Cambio**: CAMBIO1  
**Autor**: Wilmer Gulcochia  
**Sprint / Fase**: Sprint 1 — Cierre de HU-03 (Estabilización de Entorno Local Docker Compose)  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo

Implementación y estabilización definitiva del entorno de desarrollo local con Docker Compose para la Historia de Usuario **US-03**. Se corrigió y optimizó la configuración de Vite en frontend con `usePolling` canónico para hot-reload transparente en entornos de desarrollo (Windows, WSL2, Linux y macOS), se alinearon las credenciales de conexión de PostgreSQL en `backend/.env.example`, se creó `frontend/.env.example` documentando `VITE_API_URL`, se incluyeron las herramientas `sdd` en `backend/Dockerfile` bajo `INSTALL_DEV=true`, y se enriqueció `Makefile` con comandos multiplataforma (`dev-docker`, `dev-docker-d`, `db`, `db-down`). Todo verificado empíricamente con 30/30 tests aprobados, compilación limpia de Vite y arranque exitoso de los tres contenedores.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **Alineación de credenciales de desarrollo** (`backend/.env.example`):
   - **Configuración**: Se actualizó `DATABASE_URL` para reflejar la cadena canónica `postgresql+asyncpg://mediflow:mediflow_dev_pass@localhost:5432/mediflow_dev`.
   - **Propósito**: Garantizar coincidencia exacta con las credenciales configuradas en `docker-compose.dev.yml` y `docker-compose.db.yml`, eliminando fallos de autenticación al clonar el repositorio.
   - **Persistencia**: Se mantiene la base de datos PostgreSQL `mediflow_dev` como Fuente Única de Verdad, sin alteraciones a esquemas ni migraciones existentes.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
2. **Soporte SDD en contenedor de desarrollo** (`backend/Dockerfile`):
   - **Cambio técnico**: Se actualizó la instrucción de instalación en modo desarrollo (`INSTALL_DEV=true`) a `python -m pip install ".[dev,sdd]"`.
   - **Propósito**: Proveer `datamodel-code-generator`, linters y herramientas de contrato dentro de la imagen de desarrollo del backend sin alterar la imagen final de producción.
   - **Auditoría de Integridad**: Se preservó la configuración limpia de CORS en `backend/app/main.py` con los orígenes locales canónicos (`localhost` y `127.0.0.1`), descartando parches locales de expresiones regulares.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
3. **Hot-Reload canónico para entornos contenerizados** (`frontend/vite.config.ts`):
   - **Cambio técnico**: Se añadió `watch: { usePolling: true }` dentro del bloque `server:` de Vite.
   - **Propósito**: Permitir que el servidor de desarrollo Vite dentro de Docker detecte instantáneamente modificaciones de código realizadas desde el host en sistemas de archivos mixtos (WSL2/Windows/Linux).
4. **Documentación de variables de entorno de cliente** (`frontend/.env.example`):
   - **Configuración**: Creación del archivo template documentando `VITE_API_URL=http://localhost:8000/api/v1`.

### 🐳 4. Infraestructura, Scripts & Documentación
5. **Orquestación robusta y ergonomía de comandos** (`infrastructure/docker/docker-compose.dev.yml`, `Makefile`, `package.json`):
   - **Docker Compose**: Añadida directiva `depends_on: [ backend ]` al servicio `frontend` para secuenciación adecuada de inicio.
   - **Makefile**:
     - Detección automática del sistema operativo para el comando `OPEN` (`xdg-open` en Linux, `open` en macOS, `start` en Windows).
     - Nuevos targets: `dev-docker-d` (arranque detached), `dev-docker-down` (detención limpia de dev), `db` y `db-down` (control desacoplado de PostgreSQL 17 + pgAdmin).
     - Target `docs` adaptado a ejecución multiplataforma.
     - Actualización integral de la lista `.PHONY`.
   - **package.json (raíz)**: Atajos delegados `"dev": "npm --prefix frontend run dev"` y `"build": "npm --prefix frontend run build"`.
   - **Documentación y gobierno**: Incorporación de `Docs/workflow.md` (modelo Git Flow por ramas personales), `infrastructure/scripts/create_github_issues.py` (automatización de issues) y estandarización de `Docs/PLANTILLA_PULL_REQUEST.md` (sección `## Issue Vinculado` con `Closes #` para linking automático en GitHub Projects).

---

## 🧪 Verificación y Pruebas

- **Backend (Pytest)**: `30 passed in 2.10s` (`backend/tests/test_openapi_contract.py` y `backend/tests/test_generated_models.py`).
- **Frontend (TypeScript / Vite)**: `built in 1.73s`, 78 módulos transformados con 0 errores de compilación (`npm --prefix frontend run build`).
- **Validación Contractual SDD**: `Spectral: 0 errores, 1 advertencias` (`python3 infrastructure/scripts/validate_spec.py`).
- **Docker Compose (Stack Completo)**:
  - `mediflow-postgres-dev`: Estado *Healthy* en puerto `5432`.
  - `mediflow-backend-dev`: Uvicorn en puerto `8000`, respondiendo `200 OK` en `/health`.
  - `mediflow-frontend-dev`: Vite en puerto `5173`, listo en `640 ms` con HMR activo.
