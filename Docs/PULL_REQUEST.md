# 🚀 Registro Incremental de Pull Requests por Día — MediFlow

Este documento contiene el registro **acumulativo e incrementable** de todos los Pull Requests del proyecto **MediFlow**. Los PRs se organizan cronológicamente por **Fecha (`AAAA-MM-DD`)** y se enumeran de forma incremental (**PR #1, PR #2, etc.**), permitiendo registrar múltiples Pull Requests en un mismo día.

---

## 📅 Historial de Pull Requests por Fecha

---

### 🗓️ Fecha: 24/09/2026

#### 🔀 PR #1 — Control Manual de Almacenamiento (LOCAL/OCI), Comentarios BD, Aislamiento Pytest & UX Polish

- **Autor**: Erick Pariona
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

##### 📋 Resumen del PR
Este Pull Request introduce el módulo completo de **Configuración de Almacenamiento del Sistema (`LOCAL` vs `OCI`)**, garantiza la persistencia en la tabla `configuracion_sistema` de PostgreSQL, añade el script de comentarios SQL para todas las tablas/columnas, aisla la suite de pruebas unitarias (`pytest`) para evitar contaminación en la base de datos de desarrollo, rediseña la usabilidad de plantillas de triaje e incorpora la guía de migraciones Alembic y la **Regla de Oro** para el equipo.

##### 🛠️ Cambios Detallados por Capa Técnica
- 🗄️ **Base de Datos & Alembic**:
  1. **Tabla `configuracion_sistema`** (Migración `6bf254b9874e`): Almacenamiento clave-valor con valor por defecto `'modo_almacenamiento' = 'LOCAL'`.
  2. **Columna `storage_provider`** (Migración `c1f893021ab3`): Identifica en `documentos_triaje` si el archivo está en `LOCAL` u `OCI`.
  3. **Columnas `archivo_original` y `resultado_json`** (Migración `e7f893021ab4`): Rutas normalizadas `<estado>/<documento_id>/`.
  4. **Columna `nombre_original`** (Migración `f8g990032bc5`): Preserva el nombre del archivo original.
  5. **Comentarios SQL PostgreSQL** (`infrastructure/database/migrations/02_comments.sql`): Comentarios explícitos en 5 tablas y 50+ campos.
  6. **Migración Alembic de Comentarios** (`g9h001143cd6`): Ejecución atómica de `COMMENT ON` mediante `op.execute()`.
  7. **Documentación Relacional**: [`Docs/BASE_DE_DATOS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/BASE_DE_DATOS.md).
  8. **Sincronización Alembic**: Transición exitosa a `head`.
- ⚙️ **Backend & Agente IA**:
  9. **Endpoints `/api/v1/settings`**: Router FastAPI (`settings.py`) con `ConfigRequest` / `ConfigResponse` y cliente asíncrono `asyncpg`.
  10. **Validación OCI**: Respuesta HTTP `400 Bad Request` si faltan credenciales en `.env`.
  11. **Refactor en `triage_service.py`**: Selección dinámica del proveedor de almacenamiento.
  12. **Persistencia en `postgres_storage.py`**: Escritura de metadatos de almacenamiento.
  13. **Fix Import Shadowing**: Corrección de nombres de módulos en `main.py`.
  14. **Aislamiento de Pytest** (`conftest.py`): Mock fixture autouse para evitar mutación de `mediflow_dev` en tests (17/17 passing).
  15. **Dependencias en `pyproject.toml`**: `asyncpg`, `alembic`, `sqlalchemy`.
- 🎨 **Frontend & UX**:
  16. **Navegación Nav Tabs**: Pestañas `Triaje Clínico` y `Configuración`.
  17. **Vista de Configuración**: Interfaz interactiva de selección de almacenamiento y diagnóstico.
  18. **Rediseño Limpio de Plantillas**: Clases CSS `.active-preset`, `.active-btn` y `.active-pill`.
  19. **Limpieza Visual**: Remoción de emojis amontonados en títulos y botones.
  20. **Botón Principal**: Renombrado a **`Procesar y Clasificar Documento`** con estado animado.
  21. **Fecha en Historial**: Formateo localizado de fechas de procesamiento.
- 🐳 **Infraestructura & Guías**:
  22. **`.gitignore`**: Exclusión de carpetas de almacenamiento local.
  23. **`Makefile`**: Comandos `make db` y `make migrate`.
  24. **Guías**: [`AGENTS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/AGENTS.md), [`Docs/GUIA_ALEMBIC.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/GUIA_ALEMBIC.md) y [`Docs/HISTORIAL_CAMBIOS_2026-09-24.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/HISTORIAL_CAMBIOS_2026-09-24.md).

##### 🛠️ Archivos Modificados / Creados en este PR
| Tipo de Cambio | Ruta del Archivo | Descripción |
| :--- | :--- | :--- |
| **Nuevo** | `AGENTS.md` | Guía de desarrollo y Regla de Oro. |
| **Nuevo** | `Docs/BASE_DE_DATOS.md` | Documentación relacional y modelo de datos. |
| **Nuevo** | `Docs/GUIA_ALEMBIC.md` | Guía de uso de Alembic (CLI y Docker). |
| **Nuevo** | `Docs/HISTORIAL_CAMBIOS_2026-09-24.md` | Detalle diario de cambios del 24/09/2026. |
| **Nuevo** | `Docs/HISTORIAL_CAMBIOS_2026-09-14.md` | Detalle diario del Sprint 1. |
| **Nuevo** | `backend/app/api/v1/settings.py` | API de configuración de almacenamiento. |
| **Nuevo** | `backend/tests/test_settings_api.py` | Pruebas unitarias para settings API. |
| **Nuevo** | `infrastructure/database/migrations/02_comments.sql` | Script SQL de comentarios de PostgreSQL. |
| **Modificado** | `backend/pyproject.toml` | Nuevas dependencias backend. |
| **Modificado** | `backend/app/services/triage_service.py` | Lógica de almacenamiento dinámico. |
| **Modificado** | `backend/app/repositories/postgres_storage.py` | Persistencia en PostgreSQL. |
| **Modificado** | `backend/tests/conftest.py` | Isolation fixture para pytest. |
| **Modificado** | `frontend/src/App.tsx` | Nav tabs y vista de configuración. |
| **Modificado** | `frontend/src/App.css` | Estilos visuales de active presets y tabs. |
| **Modificado** | `.gitignore` | Exclusión de storage local. |
| **Modificado** | `Makefile` | Metas `make db` y `make migrate`. |

##### 🏆 Checklist de la Regla de Oro
- [x] **PostgreSQL Fuente Única de Verdad**: Metadatos guardados siempre en `mediflow_dev`.
- [x] **Control 100% Manual**: Cambio LOCAL/OCI solo desde la UI de Configuración.
- [x] **Pytest 100% Passing**: 17/17 pruebas sin alterar la BD de desarrollo.
- [x] **Frontend Clean Build**: `npm run build` en 0ms / 0 TS errors.
- [x] **Alembic Sincronizado**: Base de datos en versión `g9h001143cd6`.

---

### 🗓️ Fecha: 14/09/2026

#### 🔀 PR #1 — Setup Inicial de Arquitectura, LangGraph Agent & API de Triaje

- **Autor**: Todos
- **Rama de Origen**: `feature/initial-setup`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

##### 📋 Resumen del PR
Inicialización del repositorio MediFlow. Se definieron los 5 nodos del agente autónomo en LangGraph (`ingestion` -> `extraction` -> `classification` -> `confidence` -> `routing`), el modelo de base de datos PostgreSQL en `V001__initial_schema.sql`, los endpoints iniciales de FastAPI (`/api/v1/triage`) y la interfaz React inicial.

##### 🛠️ Cambios Detallados
1. **Grafo LangGraph**: Implementación de la canalización de procesamiento clínico multimodal.
2. **PostgreSQL Schema**: Creación de tablas principales `documentos_triaje`, `clasificaciones`, `pacientes`, `cola_procesamiento` y `auditoria_medica`.
3. **FastAPI Services**: Configuración del servidor ASGI con validaciones Pydantic.
4. **React Frontend**: Setup del cliente SPA con soporte para carga de PDFs e imágenes.
5. **Docker Compose**: Entorno contenedorizado para desarrollo local.

---

## ⚡ Guía para Agregar un Nuevo PR al Documento

Cuando se requiera documentar un nuevo Pull Request:
1. Ubicar la sección correspondiente a la **Fecha actual (`AAAA-MM-DD`)** o crear una nueva cabecera `### 🗓️ Fecha: AAAA-MM-DD`.
2. Enumerar el PR correlativamente dentro de ese día: `#### 🔀 PR #1 ...`, `#### 🔀 PR #2 ...`, etc.
3. Rellenar los campos de Autor, Ramas, Resumen, Cambios por Capa, Tabla de Archivos y Checklist de la Regla de Oro.
