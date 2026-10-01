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
> **3. Cero Regresiones y Verificación Estricta (100% Pruebas en Verde ANTES de Implementar/Finalizar)**:
> Ningún cambio se da por finalizado sin ejecutar y verificar empíricamente:
> - Backend: `pytest` (100% de pruebas unitarias y E2E pasando en verde sin mutar la base de datos de desarrollo `mediflow_dev`).
> - Frontend: `vitest run` y `npm run build` (compilación limpia con 0 errores de TypeScript y todas las pruebas en verde).
> - Base de Datos: Migraciones de Alembic sincronizadas (`alembic upgrade head --sql`).
>
> **4. Principio de Consulta Obligatoria ("Si no sabe, pregunte siempre")**:
> Queda estrictamente prohibido adivinar o asumir requerimientos, reglas clínicas, parámetros o esquemas de datos no especificados. Ante cualquier duda, ambigüedad o incertidumbre, el agente DEBE PREGUNTAR SIEMPRE al usuario antes de proceder.
> 
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

## ⚡ Comandos Spec Kit Disponibles en este Chat

Cualquier comando escrito por el usuario en el chat con los siguientes formatos debe ser reconocido y ejecutado de inmediato cargando la skill correspondiente de `.agents/skills/`:

| Comando en Chat | Acción / Skill Invocada |
|---|---|
| `/speckit-specify [descripción]` o `/specify` | Genera o actualiza la especificación en `specs/` |
| `/speckit-plan` o `/plan-spec` | Elabora el plan de arquitectura e implementación técnica |
| `/speckit-tasks` o `/tasks` | Desglosa las tareas de desarrollo con enfoque TDD |
| `/speckit-implement` o `/implement` | Ejecuta la implementación paso a paso asegurando pruebas en verde |
| `/speckit-clarify` o `/clarify` | Realiza el cuestionario de clarificación ante dudas |
| `/speckit-analyze` | Evalúa la consistencia de las especificaciones y el código |
| `/speckit-constitution` | Consulta o ajusta la constitución oficial de MediFlow |

---

## 📋 Lista de Archivos Clave del Proyecto

- `AGENTS.md`: Guía, Regla de Oro y comandos para agentes IA (este archivo).
- `.specify/memory/constitution.md`: Constitución oficial de desarrollo, calidad TDD y gobernanza del proyecto.
- `Docs/Documento-Proyecto-Mediflow.pdf`: Documento oficial del proyecto MediFlow.
- `Docs/PROPUESTA_NUEVA_BASE_DE_DATOS.md`: Especificación formal y aprobada del modelo unificado de base de datos hospitalaria.
- `backend/alembic/`: Directorio de versiones de migración de base de datos PostgreSQL.
- `backend/app/agent/`: Grafo de estado y nodos del agente autónomo (LangGraph + Gemini).
- `backend/app/api/v1/`: Endpoints FastAPI (`/triage`, `/documents`, `/patients`, `/users`, `/settings`, `/health`).
- `frontend/src/App.tsx`: Componente principal de la aplicación React.
- `infrastructure/docker/`: Archivos de Docker Compose para entornos de desarrollo y base de datos.
- `specs/`: Directorio oficial de especificaciones guiadas por Spec Kit.
