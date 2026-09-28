# Pull Request — 2026-09-28 (PR1)

## feat(US-03): estabilización del entorno de desarrollo docker compose y comandos multiplataforma

## Issue Vinculado

- Closes #7

### 📌 Datos del Pull Request

- **Título del PR**: `feat(US-03): estabilización del entorno de desarrollo docker compose y comandos multiplataforma`
- **Identificador documental**: PR1 del día 2026-09-28
- **Fecha**: 2026-09-28
- **Autor**: Wilmer Gulcochia
- **Rama de Origen**: `dev-wilmer-gulcochia`
- **Rama de Destino**: `develop`
- **Estrategia de Merge**: Squash and merge
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [HISTORIAL_CAMBIOS_2026-09-28_CAMBIO1.md](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-28_CAMBIO1.md)

---

### 📋 Resumen del PR

Este Pull Request da cumplimiento estricto y total a los criterios de aceptación de la Historia de Usuario **US-03: Estabilización de Entorno Local Docker Compose**.

Se optimizó la configuración de Vite con la directiva canónica `usePolling: true` para hot-reload confiable en contenedores sobre cualquier sistema operativo (Linux, macOS y Windows/WSL2). Se alinearon las credenciales de conexión a PostgreSQL en `backend/.env.example` para coincidir con la base de datos de Docker (`mediflow:mediflow_dev_pass`), se formalizó `frontend/.env.example` documentando `VITE_API_URL`, se añadieron las dependencias del extra `sdd` en `backend/Dockerfile` bajo `INSTALL_DEV=true`, y se modernizó el `Makefile` con detección multiplataforma de navegador y comandos ergonómicos de gestión del stack de desarrollo (`dev-docker`, `dev-docker-d`, `db`, `db-down`).

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones

- Cero alteraciones en el esquema relacional y tablas de `mediflow_dev`.
- Sincronización de `DATABASE_URL` en `backend/.env.example` con el usuario `mediflow` y contraseña `mediflow_dev_pass`.
- Persistencia de PostgreSQL como Fuente Única de Verdad en Docker Compose.

#### ⚙️ Backend & Agente IA

- Actualización de `backend/Dockerfile` para instalar `.[dev,sdd]` en modo desarrollo (`INSTALL_DEV=true`).
- Auditoría de código limpio: Se preservó la configuración segura de CORS en `backend/app/main.py` para orígenes locales canónicos (`http://localhost:5173`, `http://127.0.0.1:5173`), descartando parches locales de expresiones regulares.

#### 🎨 Frontend & UX

- `frontend/vite.config.ts`: Inclusión de `watch: { usePolling: true }` dentro del bloque `server:` de Vite, asegurando que los eventos de guardado en el host se transmitan instantáneamente al contenedor.
- `frontend/.env.example`: Creación del archivo template documentando `VITE_API_URL=http://localhost:8000/api/v1`.

#### 🐳 Infraestructura & Documentación

- `infrastructure/docker/docker-compose.dev.yml`: Agregado `depends_on: [ backend ]` al servicio `frontend` para una secuencia de inicio predecible y ordenada.
- `Makefile`:
  - Detección automática del sistema operativo para `OPEN` (`xdg-open` en Linux, `open` en macOS, `start` en Windows).
  - Comandos ergonómicos: `make dev-docker`, `make dev-docker-d`, `make dev-docker-down`, `make db` y `make db-down`.
  - Actualización de la lista `.PHONY`.
- `package.json` (raíz): Atajos `"dev"` y `"build"` para ejecutar frontend desde la raíz del repositorio.
- `Docs/PLANTILLA_PULL_REQUEST.md`: Modificación y estandarización de la plantilla oficial de Pull Requests para incorporar la sección obligatoria `## Issue Vinculado` con la directiva nativa `Closes #[Número de Issue o Tarea]`, facilitando el cierre automático del issue y la transición de tarjetas en el GitHub Project Board para todos los colaboradores del equipo.
- `Docs/workflow.md` e `infrastructure/scripts/create_github_issues.py`: Documentación de flujo de trabajo colaborativo y automatización de issues del sprint.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo                                                 | Descripción del Cambio                                                                                 |
| :------------- | :--------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------- |
| **Modificado** | `frontend/vite.config.ts`                                        | Configuración canónica de `watch: { usePolling: true }` para hot-reload.                               |
| **Modificado** | `infrastructure/docker/docker-compose.dev.yml`                   | Secuenciación con `depends_on: [ backend ]`.                                                           |
| **Modificado** | `backend/Dockerfile`                                             | Instalación de `.[dev,sdd]` cuando `INSTALL_DEV=true`.                                                 |
| **Modificado** | `backend/.env.example`                                           | Credenciales alineadas con PostgreSQL en Docker (`mediflow:mediflow_dev_pass`).                        |
| **Nuevo**      | `frontend/.env.example`                                          | Variables de entorno template para el frontend (`VITE_API_URL`).                                       |
| **Modificado** | `Makefile`                                                       | Comandos multiplataforma y gestión granular de Compose.                                                |
| **Modificado** | `package.json`                                                   | Scripts de acceso directo `dev` y `build` en la raíz.                                                  |
| **Nuevo**      | `Docs/workflow.md`                                               | Guía de flujo de trabajo Git y topología de ramas.                                                     |
| **Nuevo**      | `infrastructure/scripts/create_github_issues.py`                 | Script de automatización de issues y milestones en GitHub.                                             |
| **Modificado** | `Docs/PLANTILLA_PULL_REQUEST.md`                                 | Modificación de plantilla oficial: adición de sección `## Issue Vinculado` (`Closes #`) para el equipo.|
| **Modificado** | `Docs/PULL_REQUEST.md`                                           | Actualización del índice maestro de Pull Requests.                                                    |
| **Nuevo**      | `Docs/pull_requests/PULL_REQUEST_2026-09-28_PR1.md`             | Propuesta y documentación formal del Pull Request para US-03.                                          |
| **Modificado** | `Docs/HISTORIAL_CAMBIOS.md`                                      | Actualización del índice maestro de historiales de cambio.                                             |
| **Nuevo**      | `Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-28_CAMBIO1.md` | Registro de cambio diario detallado de la US-03.                                                       |

---

### 🏆 Checklist de la Regla de Oro (`AGENTS.md`)

- [x] **PostgreSQL es la Fuente Única de Verdad**: Persistencia garantizada en `mediflow_dev`, sin mutaciones de tablas ni migraciones huérfanas.
- [x] **Control 100% Manual de Almacenamiento**: Selección LOCAL/OCI preservada en `configuracion_sistema`.
- [x] **Pruebas Backend Passing**: `pytest` ejecutado con éxito (30/30 pruebas de contrato aprobadas en 2.10s con base aislada).
- [x] **Compilación Frontend Limpia**: `npm --prefix frontend run build` completado en 1.73s con 0 errores de TypeScript (78 módulos).
- [x] **Migraciones Alembic Sincronizadas**: Base de datos en `alembic upgrade head` (`n7o707411jk3`).
- [x] **Cero Parches Locales**: Código estándar, canónico y libre de configuraciones hardcodeadas para una máquina individual.

---

### 🧪 Verificación y Pruebas Empíricas

1. `npm --prefix frontend run build`: **0 errores de TypeScript**, build en 1.73s.
2. `python3 infrastructure/scripts/validate_spec.py`: **0 errores Spectral**, especificación OpenAPI 3.1 válida.
3. `pytest backend/tests/test_openapi_contract.py backend/tests/test_generated_models.py -v`: **30/30 tests PASSED** en 2.10s.
4. `make dev-docker`: Stack de 3 contenedores levantado limpiamente con PostgreSQL saludable, FastAPI en `:8000` y Vite en `:5173` con HMR activo.
