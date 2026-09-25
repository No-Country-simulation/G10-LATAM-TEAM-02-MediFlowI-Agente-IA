# 🤖 AGENTS.md — Reglas y Guía de Desarrollo para Agentes IA en MediFlow

Este archivo define las directrices arquitectónicas, la **Regla de Oro** y las normas de codificación que **todos los agentes de Inteligencia Artificial (Antigravity, Claude, Cursor, Copilot, etc.)** deben cumplir al modificar este repositorio.

---

## 🏆 REGLA DE ORO DE MEDIFLOW

> [!IMPORTANT]
> **1. PostgreSQL es la Fuente Única de Verdad**: 
> La base de datos PostgreSQL (`mediflow_dev`) **SIEMPRE** está activa y es obligatoria para almacenar metadatos, estructuración de diagnósticos, códigos CIE-10, trazabilidad, notificaciones y auditorías médicas (*Human-in-the-Loop*).
> 
> **2. Control 100% Manual del Modo de Almacenamiento (`LOCAL` vs `OCI`)**:
> La preferencia de almacenamiento de archivos físicos (PDFs/Imágenes) en `configuracion_sistema` solo se modifica **manualmente** por el usuario desde la pestaña `Configuración`. Ningún servicio, proceso en segundo plano ni prueba automatizada debe cambiar automáticamente este valor a `OCI`.
> 
> **3. Cero Regresiones y Verificación Estricta**:
> Ningún cambio se da por finalizado sin ejecutar y verificar empíricamente:
> - Backend: `pytest` (100% de pruebas pasando sin mutar la base de datos de desarrollo `mediflow_dev`).
> - Frontend: `npm run build` (compilación limpia en 0ms con 0 errores de TypeScript).
> - Base de Datos: Migraciones de Alembic sincronizadas (`alembic upgrade head`).
> 
> **4. Documentación Automática e Incremental por Fecha y Autor**:
> - **Historial de Cambios Diarios**: Al solicitar *"Generar documentación"* o *"Registrar cambios para Autor: [Nombre]"*, el agente debe tomar **automáticamente la fecha actual del sistema** (`AAAA-MM-DD`), cargar la plantilla `Docs/PLANTILLA_CAMBIOS.md`, generar el archivo diario `Docs/HISTORIAL_CAMBIOS_AAAA-MM-DD.md` y actualizar el índice `Docs/HISTORIAL_CAMBIOS.md`.
> - **Pull Requests Diarios e Incrementables**: Al solicitar *"Generar PR"* o *"Documentar Pull Request"*, el agente debe cargar la plantilla `Docs/PLANTILLA_PULL_REQUEST.md`, generar el archivo individual con la nomenclatura `Docs/PULL_REQUEST_AAAA-MM-DD_PR[N].md` (donde `PR[N]` es `PR1`, `PR2`, etc. permitiendo múltiples PRs por día) y actualizar el índice maestro `Docs/PULL_REQUEST.md`.

---

## 🛠️ Convenciones de Desarrollo por Capa

### 🗄️ Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
- Toda alteración de tablas debe realizarse a través de archivos de migración en `backend/alembic/versions/`.
- Todas las tablas y columnas **deben llevar comentarios explicativos** (`COMMENT ON TABLE` y `COMMENT ON COLUMN`).
- Usar identificadores únicos de documentos (`documento_id`) con restricción `UNIQUE` y manejar conflictos vía `ON CONFLICT (documento_id) DO UPDATE ...` (`UPSERT`).
- Agrupar archivos y resultados bajo la convención:
  - Archivos recibidos: `recibidos/<documento_id>/original.<ext>`
  - Resultados JSON: `<categoria_o_estado>/<documento_id>/resultado.json`

### ⚙️ Backend & Agente IA (FastAPI / LangGraph / Python)
- Mantener la orquestación del agente estructurada en los 5 nodos de LangGraph: `ingestion` ➔ `extraction` ➔ `classification` ➔ `confidence` ➔ `routing`.
- No alterar firmas de API ni modelos Pydantic sin actualizar la especificación OpenAPI (`specs/openapi.yaml`).
- Manejar la validación de credenciales OCI en `/api/v1/settings` rechazando solicitudes con HTTP 400 Bad Request si faltan variables en `.env`.

### 🎨 Frontend & UX (React / Vite / TypeScript)
- Mantener la interfaz limpia, profesional y accesible, apta para entornos clínicos y médicos.
- Evitar emojis o íconos amontonados en títulos, botones o selectores.
- Resaltar dinámicamente el estado activo de plantillas y configuraciones con clases CSS dedicadas (`.active-preset`, `.selected`).
- Garantizar que los tipos de TypeScript en `triage.api.ts` coincidan exactamente con la respuesta JSON del backend.

---

## 📋 Lista de Archivos Clave del Proyecto

- `AGENTS.md`: Guía y Regla de Oro para agentes IA (este archivo).
- `Docs/BASE_DE_DATOS.md`: Documentación completa del modelo relacional, campos, ENUMs e índices.
- `Docs/PLANTILLA_CAMBIOS.md`: Plantilla estándar genérica para historiales de cambio diarios.
- `Docs/HISTORIAL_CAMBIOS.md`: Índice maestro de registros de cambio por día.
- `Docs/PLANTILLA_PULL_REQUEST.md`: Plantilla estándar genérica para solicitudes de extracción (PRs).
- `Docs/PULL_REQUEST.md`: Índice maestro de Pull Requests por día.
- `backend/alembic/`: Directorio de versiones de migración de base de datos.
- `backend/app/agent/`: Grafo de estado y nodos del agente autónomo (LangGraph + Gemini).
- `backend/app/api/v1/`: Endpoints FastAPI (`/triage`, `/documents`, `/settings`, `/health`).
- `frontend/src/App.tsx`: Componente principal de la aplicación React.
- `infrastructure/docker/`: Archivos de Docker Compose para entornos de desarrollo y base de datos.
