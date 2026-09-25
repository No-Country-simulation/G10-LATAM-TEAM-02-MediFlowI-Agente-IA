# 🚀 Pull Request #13 — 2026-09-25

## 🔀 PR #13 — Integridad documental, OCR y trazabilidad clínica

### 📌 Datos del Pull Request

- **Título del PR**: `feat(triaje): reforzar integridad documental y trazabilidad clínica`
- **Número de PR**: 13 (PR #13 del día 2026-09-25)
- **Fecha**: 2026-09-25
- **Autor**: Erick Pariona
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO13.md](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO13.md)

---

### 📋 Resumen del PR

Refuerza la seguridad y trazabilidad del triaje clínico: autenticación Bearer/RBAC, identificación del usuario que carga documentos, historial funcional granular, fallback OCR, procesamiento incremental de documentos extensos, cola diferenciada para ambigüedad, políticas de contraseña y resolución segura de pacientes por DNI e historia clínica.

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones

- Se añadieron estados de ciclo de vida, tabla de historial, FKs de usuario y valor `Cola_Revision_Ambigua` en el ENUM de destinos.
- Se mantuvo `paciente_id` como FK existente para asociación automática sin inferencia por nombre.
- Migraciones sincronizadas hasta `l5m505299hi1`.

#### ⚙️ Backend & Agente IA

- Sesión Bearer y RBAC para endpoints clínicos.
- Persistencia de `usuario_registro_id` y consulta de historial por documento.
- PyMuPDF con fallback Tesseract para PDFs escaneados.
- Extracción y clasificación por bloques para evitar truncamientos de contexto.
- Eventos de OCR, IA, clasificación, enrutamiento y asociación/conflicto de paciente.
- Resolución exacta por DNI/HC: coincidencia única asocia; conflicto deriva a revisión ambigua.
- Política de contraseña robusta y sexo clínico opcional.

#### 🎨 Frontend & UX

- Tipos de triaje incorporan `Cola_Revision_Ambigua`.
- Formularios de pacientes permiten sexo no especificado y lo muestran de manera explícita.

#### 🐳 Infraestructura & Documentación

- Se añadió la dependencia `pytesseract`.
- Se documentaron diseño, plan e historial de cambios del bloque.
- Para OCR efectivo, el entorno debe instalar Tesseract y el paquete de idioma español.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| Migración | `backend/alembic/versions/l5m505299hi1_add_ambiguous_review_queue.py` | Cola dedicada para documentos ambiguos. |
| Backend | `backend/app/agent/nodes/ingestion.py` | Fallback OCR de PDFs escaneados. |
| Backend | `backend/app/agent/nodes/extraction.py` | Segmentación y extracción de DNI/HC. |
| Backend | `backend/app/agent/nodes/classification.py` | Clasificación incremental sin truncamiento. |
| Backend | `backend/app/services/triage_service.py` | Resolución segura de identidad del paciente. |
| Backend | `backend/app/repositories/postgres_storage.py` | Historial granular y persistencia de asociación. |
| Frontend | `frontend/src/api/triage.api.ts` | Contrato de la cola ambigua. |
| Frontend | `frontend/src/pages/PatientsManagementView.tsx` | Sexo no especificado en formularios y vistas. |

---

### 🏆 Checklist de la Regla de Oro

- [x] **PostgreSQL es la Fuente Única de Verdad**: metadatos, FKs e historial se persisten en PostgreSQL.
- [x] **Control 100% Manual de Almacenamiento**: no se modificó automáticamente LOCAL/OCI.
- [x] **Pruebas Backend Passing**: `pytest` exitoso sin mutar `mediflow_dev`.
- [x] **Compilación Frontend Limpia**: `npm run build` sin errores TypeScript.
- [x] **Migraciones Alembic Sincronizadas**: revisión `l5m505299hi1 (head)` aplicada.

---

### 🧪 Verificación y Pruebas

1. `alembic upgrade head` → `l5m505299hi1 (head)`.
2. `pytest -q` → `42 passed`.
3. `cd frontend && npm run build` → compilación exitosa; advertencia no bloqueante de tamaño de bundle.
