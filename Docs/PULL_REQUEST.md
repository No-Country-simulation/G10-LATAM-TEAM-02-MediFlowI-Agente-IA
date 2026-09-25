# 🚀 Pull Request: Control Manual de Almacenamiento (LOCAL/OCI), Comentarios BD, Aislamiento Pytest & UX Polish

## 📌 Datos del Pull Request
- **Título**: `feat(fullstack): agregar preferencia manual de almacenamiento LOCAL/OCI, comentarios SQL en BD, aislamiento pytest, navegacion por pestanas y documentacion`
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop` / `main`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

---

## 📋 Resumen del PR

Este Pull Request introduce el módulo completo de **Configuración de Almacenamiento del Sistema (`LOCAL` vs `OCI`)**, garantiza la persistencia en la tabla `configuracion_sistema` de PostgreSQL, añade el script de comentarios SQL para todas las tablas/columnas, aisla la suite de pruebas unitarias (`pytest`) para evitar contaminación en la base de datos de desarrollo, rediseña la usabilidad de plantillas de triaje e incorpora la guía de migraciones Alembic y la **Regla de Oro** para el equipo.

---

## 📅 Registro Incremental de Cambios por Día

### 🗓️ Día: 24/09/2026 — Autor: Erick Pariona
- 🗄️ **Base de Datos & Alembic**:
  1. **Tabla `configuracion_sistema`** (Migración `6bf254b9874e`): Almacenamiento de clave-valor persistente con valor por defecto `'modo_almacenamiento' = 'LOCAL'`.
  2. **Columna `storage_provider`** (Migración `c1f893021ab3`): Registra en `documentos_triaje` si el archivo físico se guardó en `LOCAL` o en `OCI`.
  3. **Columnas `archivo_original` y `resultado_json`** (Migración `e7f893021ab4`): Rutas normalizadas bajo el patrón `<estado>/<documento_id>/`.
  4. **Columna `nombre_original`** (Migración `f8g990032bc5`): Preserva el nombre del archivo subido por el cliente.
  5. **Comentarios SQL PostgreSQL** (`infrastructure/database/migrations/02_comments.sql`): `COMMENT ON TABLE` y `COMMENT ON COLUMN` para 5 tablas y 50+ campos.
  6. **Migración Alembic de Comentarios** (`g9h001143cd6`): Ejecución atómica de comentarios mediante `op.execute()`.
  7. **Documentación Relacional**: Elaboración de [`Docs/BASE_DE_DATOS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/BASE_DE_DATOS.md) con tipos nativos, restricciones e índices B-Tree y GIN (`pg_trgm`).
  8. **Sincronización Alembic**: Ejecución exitosa de `alembic upgrade head`.
- ⚙️ **Backend & Agente IA**:
  9. **Endpoints `/api/v1/settings`**: Router FastAPI en `settings.py` con schemas Pydantic `ConfigRequest` y `ConfigResponse` con cliente asíncrono `asyncpg`.
  10. **Validación OCI**: Rechazo HTTP `400 Bad Request` en `POST /api/v1/settings` si se selecciona `OCI` sin credenciales en `.env`.
  11. **Refactor en `triage_service.py`**: Consulta activa a PostgreSQL antes de guardar archivos en `LOCAL` o `OCI`.
  12. **Persistencia en `postgres_storage.py`**: Inserción de `storage_provider`, `archivo_original`, `resultado_json`, `nombre_original` y `UPSERT` en `cola_procesamiento`.
  13. **Fix de Variable Shadowing**: Corrección en `main.py` de `from app.api.v1 import settings as settings_router`.
  14. **Aislamiento de Pytest** (`conftest.py`): Mock autouse para evitar mutar `mediflow_dev` durante unit tests (17/17 passing en 0.23s).
  15. **Dependencias en `pyproject.toml`**: Adición de `asyncpg>=0.29.0`, `alembic>=1.13.0`, `sqlalchemy>=2.0.0`.
- 🎨 **Frontend & UX**:
  16. **Navegación Nav Tabs**: Pestañas `Triaje Clínico` y `Configuración` en React.
  17. **Vista de Configuración**: Interfaz con tarjetas radio de almacenamiento y panel de diagnóstico del sistema.
  18. **Rediseño Limpio de Plantillas**: Estilos `.active-preset`, `.active-btn` y `.active-pill` en `App.css` con borde cyan `#0284c7`.
  19. **Limpieza de Emojis/Íconos**: Retiro de decoradores amontonados para estética hospitalaria profesional.
  20. **Mejora del Botón de Envío**: Renombrado a **`Procesar y Clasificar Documento`** con estado animado `Analizando con LangGraph & Gemini...`.
  21. **Fecha en Historial**: Columna `Fecha de Procesamiento` (`created_at` formateada en español).
- 🐳 **Infraestructura & Guías**:
  22. **`.gitignore`**: Exclusión de `backend/storage/` y `storage/`.
  23. **`Makefile`**: Nuevas metas `make db` y `make migrate`.
  24. **Guías para el Equipo**: [`AGENTS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/AGENTS.md), [`Docs/GUIA_ALEMBIC.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/GUIA_ALEMBIC.md) y [`Docs/HISTORIAL_CAMBIOS_2026-09-24.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/HISTORIAL_CAMBIOS_2026-09-24.md).

### 🗓️ Día: 14/09/2026 — Autor: Todos
- Setup inicial del esquema SQL `V001__initial_schema.sql`, 5 nodos del agente LangGraph (`ingestion`, `extraction`, `classification`, `confidence`, `routing`), API FastAPI `/triage`, React Frontend Workspace y Docker Compose.

---

## 🛠️ Detalle de Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Nuevo** | `AGENTS.md` | Guía de reglas y Regla de Oro para agentes IA. |
| **Nuevo** | `Docs/BASE_DE_DATOS.md` | Documentación técnica del modelo relacional. |
| **Nuevo** | `Docs/GUIA_ALEMBIC.md` | Guía de uso manual CLI y en Docker de Alembic. |
| **Nuevo** | `Docs/HISTORIAL_CAMBIOS.md` | Índice general de historiales por día. |
| **Nuevo** | `Docs/HISTORIAL_CAMBIOS_2026-09-24.md` | Registro detallado del 24/09/2026. |
| **Nuevo** | `Docs/HISTORIAL_CAMBIOS_2026-09-14.md` | Registro detallado del 14/09/2026. |
| **Nuevo** | `Docs/PLANTILLA_CAMBIOS.md` | Plantilla genérica para futuros historiales. |
| **Nuevo** | `backend/app/api/v1/settings.py` | Endpoints GET y POST de configuración del sistema. |
| **Nuevo** | `backend/tests/test_settings_api.py` | Pruebas unitarias para la API de settings. |
| **Nuevo** | `infrastructure/database/migrations/02_comments.sql` | Script SQL de comentarios para PostgreSQL. |
| **Modificado** | `backend/pyproject.toml` | Adición de `alembic`, `asyncpg` y `sqlalchemy`. |
| **Modificado** | `backend/app/services/triage_service.py` | Guardado dinámico en `LOCAL` u `OCI`. |
| **Modificado** | `backend/app/repositories/postgres_storage.py` | Persistencia de nuevos campos de almacenamiento. |
| **Modificado** | `backend/tests/conftest.py` | Mockeo de escrituras a BD durante ejecuciones de pytest. |
| **Modificado** | `frontend/src/App.tsx` | Navegación por pestañas, pantalla Settings y UI de triaje. |
| **Modificado** | `frontend/src/App.css` | Estilos para plantillas activas `#0284c7`, tabs y settings. |
| **Modificado** | `.gitignore` | Exclusión de `backend/storage/` y `storage/`. |
| **Modificado** | `Makefile` | Nuevos comandos `make db` y `make migrate`. |

---

## 🏆 Checklist de la Regla de Oro

- [x] **PostgreSQL es la fuente única de verdad**: Se garantiza que la persistencia en `mediflow_dev` ocurra siempre, sin importar si los archivos físicos van a `LOCAL` u `OCI`.
- [x] **Control 100% manual de almacenamiento**: Cambiar entre `LOCAL` y `OCI` solo se ejecuta por acción directa del usuario en la pestaña Configuración.
- [x] **Pruebas de Backend aisladas**: `pytest` pasa 17/17 pruebas en 0.23s sin mutar la BD de desarrollo.
- [x] **Compilación de Frontend limpia**: `npm run build` compila exitosamente en 162ms con 0 errores de TypeScript.
- [x] **Migraciones de Alembic sincronizadas**: `alembic upgrade head` sincronizado a la revisión `g9h001143cd6`.

---

## 🧪 Cómo Probar este PR

1. **Levantar PostgreSQL y aplicar migraciones**:
   ```bash
   make db
   make migrate
   ```
2. **Ejecutar Pruebas del Backend**:
   ```bash
   cd backend
   .venv\Scripts\python.exe -m pytest tests
   ```
3. **Probar la Compilación del Frontend**:
   ```bash
   cd frontend
   npm run build
   ```
4. **Probar la Vista de Configuración**:
   - Iniciar la aplicación y navegar a la pestaña **Configuración**.
   - Alternar entre **Almacenamiento Local** y **OCI Object Storage** para verificar las validaciones de credenciales.
