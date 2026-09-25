# 📜 Historial de Cambios — 2026-09-25 (CAMBIO12)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO12  
**Autor**: Erick Pariona  
**Sprint / Fase**: Sprint 2 — Módulo 2 (Pacientes: RF-06 a RF-09) y Módulo 3 (Recepción: RF-10)  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal  

---

## 📋 Resumen Ejecutivo
Implementación integral del **Módulo 2: Pacientes** (RF-06 Registro de Pacientes, RF-07 Búsqueda por DNI/HC/Nombres, RF-08 Asociación Paciente-Documento y RF-09 Trazabilidad de Datos Extraídos por IA) y acoplamiento directo con **Módulo 3: Recepción de Documentos** (RF-10 Ingesta directa para el paciente). Incluye la creación de la migración de base de datos con comentarios relacionales en PostgreSQL, backend en FastAPI, cliente API TypeScript y la interfaz de usuario con buscador interactivo Search Select (`SearchableDocSelect`) y estilizado corporativo.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)
1. **Migración `add_pacientes_table`** (`backend/alembic/versions/i2j302266ef8_add_pacientes_table.py`):
   - **SQL / DDL**: 
     - `CREATE TABLE IF NOT EXISTS pacientes (...)` con columnas `id`, `tipo_documento`, `numero_documento` (UNIQUE), `historia_clinica` (UNIQUE), `nombres`, `apellidos`, `fecha_nacimiento`, `sexo`, `telefono` y `correo`.
     - `ALTER TABLE documentos_triaje ADD COLUMN IF NOT EXISTS paciente_id UUID REFERENCES pacientes(id) ON DELETE SET NULL;`
     - Añadidos `COMMENT ON TABLE` y `COMMENT ON COLUMN` para todas las columnas de `pacientes` y `documentos_triaje.paciente_id` cumpliendo las reglas del repositorio.
   - **Propósito**: Persistir de manera estructurada los pacientes del sistema en PostgreSQL como Fuente Única de Verdad y permitir el enlace FK con los expedientes clínicos procesados por la IA.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)
2. **Repositorio de Pacientes** (`backend/app/repositories/patient_repository.py`):
   - Implementada la persistencia asíncrona mediante `asyncpg` con funciones `list_patients`, `get_patient_by_id`, `get_patient_by_doc`, `get_patient_by_hc`, `create_patient`, `update_patient`, `get_patient_documents`, `get_unlinked_documents` (filtrando `WHERE d.paciente_id IS NULL`) y `associate_document_to_patient`.
   - Incluida capa de fallback resiliente en memoria para entornos locales de desarrollo.
3. **Endpoints de Pacientes** (`backend/app/api/v1/patients.py`):
   - Definidas las rutas REST `/api/v1/patients`:
     - `GET /patients`: Búsqueda y listado (RF-07).
     - `POST /patients`: Registro de pacientes (RF-06).
     - `PUT /patients/{id}`: Edición de paciente.
     - `GET /patients/{id}/documents`: Historial documental y metadatos IA conservados (RF-08 y RF-09).
     - `GET /patients/unlinked-documents`: Documentos disponibles para asociar.
     - `POST /patients/{id}/documents/{documento_id}/associate`: Vinculación manual de expediente.
   - Autenticación flexible mediante la dependencia `get_current_user_or_api_key` (aporta soporte tanto para tokens de sesión Bearer como X-API-Key).
4. **Registro en App Principal** (`backend/app/main.py`):
   - Incluido el nuevo router `patients.router` bajo el prefijo `/api/v1`.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)
5. **Cliente API TypeScript** (`frontend/src/api/patients.api.ts`):
   - Definidas interfaces TypeScript `Paciente`, `PacienteCreatePayload`, `PacienteUpdatePayload`, `DocumentoPaciente`, `HistorialDocumentosPacienteResponse`, `DocumentoDisponible`.
   - Normalización de URL base en `getApiBaseUrl()` para evitar duplicaciones como `/api/v1/api/v1/`.
6. **Vista de Gestión de Pacientes y UX Polish** (`frontend/src/pages/PatientsManagementView.tsx`):
   - Diseñado el dashboard con Tarjetas KPI (Total Pacientes, Con Historia Clínica, Vínculos Documentales y Detección IA).
   - Implementado el componente interactivo **`SearchableDocSelect`**: buscador tipo desplegable con filtrado en tiempo real, sombra flotante `z-index: 1080` y detector de clics externos para ocultar el menú de sugerencias de forma fluida.
   - Ajustado el modal de expedientes con la paleta de colores corporativa `.modal-header-mediflow` y eliminación completa de guiones em (`—`).
7. **Estilos CSS Globales** (`frontend/src/App.css`):
   - Añadidas clases `.modal-header-mediflow` (`linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0284c7 100%)`) y `.modal-backdrop-custom` con efecto de desenfoque (`backdrop-filter: blur(4px)`).
8. **Rutas y Menú** (`frontend/src/routes/AppRoutes.jsx`, `frontend/src/components/layout/Sidebar.jsx`):
   - Registrada la ruta `/pacientes` e ícono `<FaUserInjured />` en el menú principal.

---

## 🧪 Verificación y Pruebas
- **Backend (Python)**: `python -m py_compile` ejecutado exitosamente en `main.py`, `patients.py`, `patient_repository.py` y la migración Alembic (0 errores de sintaxis o importación).
- **Frontend (TypeScript)**: `npm run build` ejecutado en 389ms sin ningún error de TypeScript (`0 errors`).
- **Migraciones (Alembic)**: Migración `i2j302266ef8_add_pacientes_table.py` sincronizada en la base de datos `mediflow_dev`.
