# 📜 Historial de Cambios — 2026-09-14

**Fecha**: 14/09/2026  
**Autor**: Todos  
**Sprint / Fase**: Sprint 1 — Arquitectura Base & Setup Inicial  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Construcción e implementación del núcleo del sistema MediFlow. Se estableció la arquitectura desacoplada en tres capas (Base de Datos PostgreSQL 17, Backend FastAPI + LangGraph + Google Gemini, y Frontend React + Vite + TypeScript), junto con la definición de la especificación OpenAPI (SDD).

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **Creación del Esquema Inicial DDL** (`infrastructure/database/migrations/V001__initial_schema.sql`):
   - Creación de extensiones PostgreSQL: `uuid-ossp` (UUIDs), `pg_trgm` (trigramas de texto), `unaccent` (búsquedas sin tildes).
   - Creación de tipos enumerados: `tipo_archivo_enum`, `nivel_prioridad_enum`, `status_documento_enum`, `destino_enum`, `status_oci_enum`, `decision_auditoria_enum`.
   - Creación de las 4 tablas base de dominio:
     - `documentos_triaje`: Almacena el resultado completo del triaje clínico.
     - `auditorias_hitl`: Registra la intervención médica Human-in-the-Loop.
     - `notificaciones`: Registra alertas generadas para emergencias.
     - `cola_procesamiento`: Vista lógicamente materializada para colas de trabajo.
2. **Creación de Índices de Rendimiento**:
   - Creación de índices B-Tree en `documento_id`, `status`, `nivel_prioridad`, `destino_principal` y `created_at`.
   - Creación de índices Trigram (GIN) en `diagnostico_principal` y `paciente_nombre` para búsquedas en tiempo real.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
3. **Orquestador de Triaje Autónomo (LangGraph)** (`backend/app/agent/`):
   - Implementación del grafo de estado compuesto por 5 nodos secuenciales y condicionales:
     - `ingestion`: Procesamiento inicial de texto plano, PDF (PyMuPDF) e imágenes.
     - `extraction`: Extracción de paciente, edad, médico, estudio, diagnóstico, CIE-10 y hallazgos clave mediante Google Gemini.
     - `classification`: Clasificación de prioridad (`Urgente`, `Rutina`, `Ambiguo`) y especialidad médica.
     - `confidence`: Evaluación matemática del score de confianza (0.0 a 1.0).
     - `routing`: Decisión de enrutamiento a `Cola_Emergencia_Medica`, `Cola_Rutina` o `Cola_Auditoria_Humana`.
4. **Endpoints de la API REST** (`backend/app/api/v1/`):
   - `POST /api/v1/triage`: Ingesta de texto o archivo multipart file upload.
   - `GET /api/v1/documents`: Listado de documentos procesados.
   - `GET /api/v1/health`: Chequeo de estado del sistema.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
5. **Workspace Clínico React**:
   - Desarrollo de la aplicación cliente en React + Vite + TypeScript.
   - Implementación del formulario de ingesta (texto/PDF/imagen) y visualización del diagnóstico, CIE-10 y hallazgos.
   - Implementación de botones para auditoría médica HITL (*Aprobar*, *Reclasificar*, *Rechazar*).

### 🐳 4. Infraestructura, Scripts & Documentación
6. **Docker Compose & Entorno**:
   - Configuración de `docker-compose.yml` (producción) y `docker-compose.dev.yml` (desarrollo con hot-reload).
   - Configuración de `docker-compose.db.yml` para PostgreSQL 17 + pgAdmin 4.
7. **Especificación OpenAPI (SDD)**:
   - Definición formal en `specs/openapi.yaml` y `specs/components/schemas.yaml`.

---

## 🧪 Verificación y Pruebas
- **Backend (Pytest)**: Suite de pruebas unitarias configurada en `backend/tests/`.
- **Frontend (TypeScript)**: Compilación sin errores en Vite.
- **Base de Datos**: PostgreSQL 17 activo.
