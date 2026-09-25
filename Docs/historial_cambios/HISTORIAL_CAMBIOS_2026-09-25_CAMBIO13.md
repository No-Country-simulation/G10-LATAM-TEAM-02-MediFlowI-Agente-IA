# 📜 Historial de Cambios — 2026-09-25 (CAMBIO13)

**Fecha**: 25/09/2026  
**Identificador de Cambio**: CAMBIO13  
**Autor**: Erick Pariona  
**Sprint / Fase**: Integridad, trazabilidad y seguridad del triaje clínico  
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

---

## 📋 Resumen Ejecutivo

Se reforzó el flujo clínico de extremo a extremo: sesión Bearer y RBAC, trazabilidad del usuario que carga cada documento, historial funcional, OCR de respaldo, procesamiento por bloques sin pérdida de contenido, contraseñas robustas, sexo opcional y una cola dedicada para documentos ambiguos. También se inició la asociación segura de pacientes por DNI e historia clínica.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)

1. **Trazabilidad documental y cola de revisión ambigua** (`backend/alembic/versions/j3k303277fg9_add_document_statuses.py`, `k4l404288gh0_add_document_traceability.py`, `l5m505299hi1_add_ambiguous_review_queue.py`):
   - **SQL / DDL**: se añadieron estados de recepción, la FK `documentos_triaje.usuario_registro_id`, la tabla `historial_documento`, la relación de asignación de cola por UUID y el valor `Cola_Revision_Ambigua` al ENUM `destino_enum`.
   - **Propósito**: preservar actor, secuencia funcional y destino operativo de cada documento.

2. **Asociación segura de paciente** (`backend/app/repositories/patient_repository.py`, `backend/app/repositories/postgres_storage.py`):
   - **Cambio técnico**: se aprovecha la FK existente `documentos_triaje.paciente_id`; no se requirió una migración adicional.
   - **Propósito**: asociar sólo coincidencias exactas por DNI/HC y evitar inferencias por nombre.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)

1. **Autenticación y trazabilidad de carga** (`backend/app/core/security.py`, `backend/app/api/v1/triage.py`, `backend/app/services/triage_service.py`):
   - **Cambio técnico**: se propaga el usuario de la sesión Bearer hacia la persistencia del documento.

2. **OCR, extracción y clasificación incremental** (`backend/app/agent/nodes/ingestion.py`, `extraction.py`, `classification.py`):
   - **Cambio técnico**: PyMuPDF usa Tesseract como fallback para PDF escaneado; extracción y clasificación procesan bloques completos en vez de cortes `texto[:4000]` y `texto[:3000]`.
   - **Propósito**: no perder información clínica situada al final de documentos extensos.

3. **Identificadores y resolución de paciente** (`backend/app/agent/state.py`, `backend/app/agent/nodes/extraction.py`, `backend/app/services/triage_service.py`):
   - **Cambio técnico**: se extraen `documento_identidad` e `historia_clinica`; un conflicto deriva a `Cola_Revision_Ambigua` y una coincidencia única persiste `paciente_id`.

4. **Historial funcional granular** (`backend/app/repositories/postgres_storage.py`, `backend/app/api/v1/documents.py`):
   - **Cambio técnico**: se registran recepción, inicio, OCR, extracción IA, clasificación, enrutamiento, asociación/conflicto de paciente y finalización; el endpoint de historial permite consultarlos.

5. **Políticas clínicas y seguridad** (`backend/app/api/v1/users.py`, `backend/app/api/v1/patients.py`):
   - **Cambio técnico**: contraseñas de mínimo 12 caracteres con mayúscula, minúscula, número y símbolo; sexo de paciente opcional sin default clínico.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)

1. **Contratos de triaje y paciente** (`frontend/src/api/triage.api.ts`, `frontend/src/api/patients.api.ts`, `frontend/src/pages/PatientsManagementView.tsx`):
   - **Cambio de UI / Estado**: se tipó `Cola_Revision_Ambigua`; sexo admite `null` y se representa como “No especificado”, sin asumir `M`.

### 🐳 4. Infraestructura, Scripts & Documentación

1. **Dependencia OCR y documentación técnica** (`backend/pyproject.toml`, `Docs/superpowers/specs/`, `Docs/superpowers/plans/`):
   - **Configuración**: se incorporó `pytesseract` y se documentaron los diseños y planes de integridad documental. El entorno de ejecución debe disponer del binario Tesseract y el idioma español para OCR efectivo.

---

## 🧪 Verificación y Pruebas

- **Backend (Pytest)**: `42 passed`.
- **Frontend (TypeScript)**: `npm run build` exitoso; persiste únicamente advertencia de bundle mayor a 500 kB.
- **Migraciones (Alembic)**: `alembic upgrade head` aplicado; revisión `l5m505299hi1 (head)`.
