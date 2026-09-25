# 📜 Historial de Cambios — 2026-09-24

**Fecha**: 24/09/2026  
**Autor**: Erick Pariona  
**Sprint / Fase**: Sprint 2 — Control Manual de Almacenamiento, Comentarios BD, Aislar Pruebas & UX Polish  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
En esta jornada se implementó el módulo completo de configuración de almacenamiento (`LOCAL` vs `OCI`), la tabla `configuracion_sistema`, migraciones de Alembic, script de comentarios SQL para PostgreSQL, aislamiento de la suite `pytest`, rediseño UX de plantillas de triaje, retiro de emojis amontonados en la interfaz y elaboración de la documentación técnica y guías de desarrollo (`AGENTS.md`, `Docs/BASE_DE_DATOS.md`, `Docs/GUIA_ALEMBIC.md`).

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)

1. **Creación de la Tabla `configuracion_sistema`** (`backend/alembic/versions/6bf254b9874e_add_configuracion_sistema.py`):
   - **SQL DDL**:
     ```sql
     CREATE TABLE IF NOT EXISTS configuracion_sistema (
         clave VARCHAR(100) PRIMARY KEY,
         valor VARCHAR(500) NOT NULL,
         descripcion TEXT,
         updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
     );
     ```
   - **Inserción Semilla**: `INSERT INTO configuracion_sistema (clave, valor, descripcion) VALUES ('modo_almacenamiento', 'LOCAL', 'Modo de almacenamiento activo: LOCAL u OCI') ON CONFLICT (clave) DO NOTHING;`
   - **Propósito**: Almacenar la preferencia de almacenamiento persistente en la BD PostgreSQL sin depender de variables de entorno globales temporales.

2. **Columna `storage_provider` en `documentos_triaje`** (`backend/alembic/versions/c1f893021ab3_add_storage_provider_column.py`):
   - **Alembic Command**: `op.add_column('documentos_triaje', sa.Column('storage_provider', sa.String(length=50), nullable=True, server_default='LOCAL'))`
   - **Propósito**: Registrar de forma individual en cada fila si el respaldo del archivo físico original y resultado JSON se guardó en `LOCAL` o en `OCI`.

3. **Columnas `archivo_original` y `resultado_json`** (`backend/alembic/versions/e7f893021ab4_add_archivo_original_and_resultado_json.py`):
   - **Alembic Commands**: `op.add_column('documentos_triaje', sa.Column('archivo_original', sa.String(length=500), nullable=True))` y `resultado_json`.
   - **Patrón de Rutas**: Guarda rutas estructuradas por `documento_id` (ej. `recibidos/DOC-776123/original.png` y `urgentes/DOC-776123/resultado.json`).

4. **Columna `nombre_original`** (`backend/alembic/versions/f8g990032bc5_add_nombre_original_column.py`):
   - **Alembic Command**: `op.add_column('documentos_triaje', sa.Column('nombre_original', sa.String(length=500), nullable=True))`
   - **Propósito**: Preservar el nombre real del archivo subido por el cliente (ej. `laboratorio_juan_perez.pdf`) evitando problemas de URL escaping o exposición de PII en el sistema de archivos.

5. **Script de Comentarios SQL PostgreSQL** (`infrastructure/database/migrations/02_comments.sql`):
   - Inclusión de sentencias `COMMENT ON TABLE` y `COMMENT ON COLUMN` para las 5 tablas principales (`documentos_triaje`, `auditorias_hitl`, `configuracion_sistema`, `notificaciones`, `cola_procesamiento`) y sus 50+ columnas.

6. **Migración Alembic de Comentarios** (`backend/alembic/versions/g9h001143cd6_add_database_comments.py`):
   - Empaquetado atómico de llamadas `op.execute("COMMENT ON TABLE ...")` y `op.execute("COMMENT ON COLUMN ...")` para asegurar compatibilidad completa en Alembic.

7. **Documentación Técnica del Modelo Relacional** (`Docs/BASE_DE_DATOS.md`):
   - Elaboración del diccionario de datos con tipos nativos (`UUID`, `VARCHAR`, `TEXT`, `JSONB`, `TIMESTAMPTZ`, `FLOAT`, `ENUM`), restricciones (`PRIMARY KEY`, `UNIQUE`, `CHECK`, `FOREIGN KEY`) e índices B-Tree y GIN (`pg_trgm`).

8. **Sincronización de Schema Alembic**:
   - Ejecución de `alembic upgrade head` dejando la base de datos `mediflow_dev` en la revisión `g9h001143cd6`.

---

### ⚙️ 2. Backend & Servicios (FastAPI / LangGraph / Python)

9. **Endpoints de Configuración del Sistema `/api/v1/settings`** (`backend/app/api/v1/settings.py`):
   - **Router**: Prefijo `/settings`, tag `settings`.
   - **Schemas Pydantic**: `ConfigRequest(storage_mode: str)` con patrón `^(LOCAL|OCI)$` y `ConfigResponse` (contiene `storage_mode`, `oci_configured`, `llm_provider`, `llm_configured`, `database_url_configured`).
   - **GET /api/v1/settings**: Invoca `_obtener_modo_almacenamiento_db()` que ejecuta `SELECT valor FROM configuracion_sistema WHERE clave = 'modo_almacenamiento'` vía `asyncpg`.
   - **POST /api/v1/settings**: Invoca `_guardar_modo_almacenamiento_db()` ejecutando SQL `INSERT INTO configuracion_sistema ... ON CONFLICT (clave) DO UPDATE SET valor = EXCLUDED.valor`.

10. **Validación Estricta de Credenciales OCI**:
    - Evaluación lógica `if payload.storage_mode == "OCI" and not settings.oci_configured:` en `POST /api/v1/settings`.
    - Retorna `HTTPException(status_code=400, detail={"error": "OCI_NO_CONFIGURADO", "mensaje": "..."})` si faltan `OCI_USER_OCID`, `OCI_TENANCY_OCID` o `OCI_NAMESPACE` en `.env`.

11. **Refactorización del Almacenamiento en `triage_service.py`**:
    - Método `procesar_documento()`: Consulta la preferencia `modo_almacenamiento` desde PostgreSQL antes de la ingesta.
    - Modo `LOCAL`: Guarda en `backend/storage/recibidos/<doc_id>/original.<ext>` y `backend/storage/<estado>/<doc_id>/resultado.json`.
    - Modo `OCI`: Sube a Oracle Cloud Object Storage en el bucket `mediflow-documentos-clinicos`.

12. **Persistencia en `postgres_storage.py`**:
    - Actualización de la consulta `INSERT INTO documentos_triaje` para escribir los campos `storage_provider`, `archivo_original`, `resultado_json` y `nombre_original`.
    - Mantiene el `UPSERT` en `cola_procesamiento` (`ON CONFLICT (documento_id) DO UPDATE SET destino = EXCLUDED.destino, status = EXCLUDED.status`).

13. **Fix de Sombreado de Nombres en `main.py`** (`backend/app/main.py`):
    - Corrección de la importación a `from app.api.v1 import settings as settings_router` evitando la colisión con la variable local `settings = get_settings()`.

14. **Aislamiento Total de la Suite Pytest** (`backend/tests/conftest.py`):
    - Creación de fixture autouse `mock_db_writes` que parchea `PostgresStorageRepository.guardar_resultado` y `_guardar_modo_almacenamiento_db`.
    - Evita que los unit tests inserten filas de prueba (`DOC-TEST-RUTINA`) o muten la tabla `configuracion_sistema` en `mediflow_dev`.
    - Verificación: 17 de 17 unit tests pasando en 0.23s.

15. **Inclusión de Dependencias de BD** (`backend/pyproject.toml`):
    - Adición de `"asyncpg>=0.29.0"`, `"alembic>=1.13.0"`, `"sqlalchemy>=2.0.0"` al bloque `dependencies`.

---

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)

16. **Navegación por Pestañas Superior (`nav-tabs`)** (`frontend/src/App.tsx` & `App.css`):
    - Adición del estado `activeTab: 'triage' | 'settings'` en `App.tsx`.
    - Renderizado de la barra de navegación `<nav className="nav-tabs">` con botones `Triaje Clínico` y `Configuración`.

17. **Pantalla de Configuración del Sistema**:
    - Creación de la vista `{activeTab === 'settings' && (...)}`.
    - Implementación de tarjetas radio `Almacenamiento Local (Disco del Servidor)` y `OCI Object Storage (Oracle Cloud)`.
    - Integración con API `obtenerConfiguracion()` y `actualizarConfiguracion()` en `frontend/src/api/triage.api.ts`.

18. **Rediseño Limpio y Resaltado de Plantillas (`PRESET_CASES`)**:
    - Actualización del mapeo de plantillas en `App.tsx` usando el estado `selectedPresetId`.
    - Eliminación del texto amontonado en la cabecera del card.
    - Adición de clases CSS en `App.css`:
      - `.preset-card.active-preset`: `border: 2px solid #0284c7`, `background-color: #f0f9ff`, `box-shadow: 0 4px 16px rgba(2, 132, 199, 0.15)`.
      - `.btn-use-preset.active-btn`: `background: #0284c7`, `color: #ffffff`.
      - `.active-pill`: Píldora discreta `Activo`.

19. **Limpieza Integral de Emojis y Decoradores UI**:
    - Retiro de emojis decorativos del encabezado (`🏥`), pestañas de navegación, selectores de canal (`Guardia_Emergencias`, `Consulta_Externa`), toggles de tipo de entrada (`Texto Clínico`, `Archivo PDF / Imagen`) y botones principales.

20. **Mejora del Botón de Ingesta**:
    - Cambio del texto del botón principal a **`Procesar y Clasificar Documento`**.
    - Estado animado de carga: `Analizando con LangGraph & Gemini...`.

21. **Columna Fecha de Procesamiento en Historial**:
    - Adición de la columna `Fecha de Procesamiento` en la tabla de historial reciente.
    - Formateo mediante `new Date(doc.created_at).toLocaleString('es-ES', { dateStyle: 'short', timeStyle: 'medium' })`.

---

### 🐳 4. Infraestructura, Scripts & Documentación

22. **Actualización de `.gitignore`**:
    - Adición de `backend/storage/` y `storage/` para ignorar archivos subidos locales y resultados JSON temporales.

23. **Nuevos Comandos en `Makefile`**:
    - Adición de las metas `make db` (`docker compose -f infrastructure/docker/docker-compose.db.yml up -d`) y `make migrate` (`cd backend && alembic upgrade head`).

24. **Creación de Guías Técnicas para el Equipo**:
    - [`AGENTS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/AGENTS.md): Reglas generales y Regla de Oro para agentes de IA.
    - [`Docs/GUIA_ALEMBIC.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/GUIA_ALEMBIC.md): Guía de comandos Alembic para el equipo de desarrollo.
    - [`Docs/BASE_DE_DATOS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/BASE_DE_DATOS.md): Documentación del modelo entidad-relación y diccionario de datos.
    - [`Docs/PLANTILLA_CAMBIOS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/PLANTILLA_CAMBIOS.md): Plantilla estándar genérica para cambios diarios.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: 17/17 pruebas unitarias pasando en 0.23s.
- **Frontend (TypeScript)**: `npm run build` exitoso en 155ms con 0 errores.
- **Migraciones (Alembic)**: `alembic upgrade head` sincronizado a revisión `g9h001143cd6`.
