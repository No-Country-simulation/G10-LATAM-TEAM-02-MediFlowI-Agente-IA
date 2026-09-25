# 📜 Historial de Cambios — 2026-09-25 (CAMBIO14)

**Fecha**: 25/09/2026 *(Fecha generada automáticamente por el Agente)*
**Identificador de Cambio**: CAMBIO14
**Autor**: Erick Pariona
**Sprint / Fase**: Cierre técnico integral — backlog crítico, UX, despliegue y seguridad
**Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal

---

## 📋 Resumen Ejecutivo

Se consolidó el cierre del backlog técnico y funcional de MediFlow: PostgreSQL quedó como fuente única de verdad, la carga y auditoría de documentos se conectaron a rutas reales, el almacenamiento LOCAL/OCI conserva control manual, el OCR admite imágenes y PDF, y el frontend fue migrado íntegramente a TypeScript con una experiencia clínica coherente y responsiva. También se endurecieron las sesiones, credenciales iniciales, validaciones, estados de error y configuración de despliegue con Docker.

---

## 🛠️ Detalle de Cambios por Capa Técnica

### 🗄️ 1. Base de Datos & Migraciones (PostgreSQL 17 / Alembic)

1. **Sesiones de usuario persistentes y revocables** (`backend/alembic/versions/m6n606300ij2_add_persistent_user_sessions.py`):
   - **SQL / DDL**: se incorporó la tabla de sesiones con token almacenado mediante hash, vencimiento, revocación, índices y comentarios explicativos.
   - **Propósito**: eliminar sesiones efímeras del proceso y mantener autenticación y trazabilidad en PostgreSQL.
2. **Rotación segura de credenciales semilla** (`backend/alembic/versions/n7o707411jk3_rotate_weak_seed_credentials.py`):
   - **SQL / DDL**: la contraseña inicial débil se reemplaza únicamente cuando el hash continúa siendo el valor semilla conocido; las sesiones activas asociadas se revocan.
   - **Propósito**: impedir que la migración sobrescriba contraseñas ya personalizadas y cerrar sesiones creadas con credenciales comprometidas.
3. **Persistencia clínica obligatoria** (`backend/app/repositories/`):
   - Se retiraron los respaldos de memoria y datos de demostración para usuarios, pacientes, documentos y configuración.
   - No se creó una migración adicional para DNI/HC: `paciente_id` e `historial_documento` ya existen y son utilizados por la integración.

### ⚙️ 2. Backend & Agente IA (FastAPI / LangGraph / Python)

1. **Flujo documental real y auditable** (`backend/app/api/v1/documents.py`, `backend/app/api/v1/triage.py`):
   - El listado, detalle, historial y auditoría consultan y actualizan PostgreSQL.
   - La auditoría actualiza documento, cola e historial de forma coherente y responde `409 Conflict` cuando el caso ya fue resuelto.
   - La carga valida tamaño, tipo MIME y firma binaria antes de procesar el archivo.
2. **Almacenamiento coherente LOCAL/OCI** (`backend/app/repositories/oci_storage.py`, `backend/app/repositories/postgres_storage.py`):
   - La preferencia se lee desde `configuracion_sistema` y solo puede modificarse manualmente desde Configuración.
   - Los fallos físicos de almacenamiento se registran y exponen; no existe degradación silenciosa de OCI a LOCAL.
3. **OCR, catálogo clínico y agente** (`backend/app/agent/`, `backend/app/services/triage_service.py`):
   - Se añadió OCR real con Tesseract en español para imágenes y respaldo OCR para PDF.
   - Se normalizó y amplió el catálogo clínico compartido por extracción, clasificación, confianza y enrutamiento.
   - El procesamiento incremental conserva fragmentos extensos y envía casos ambiguos a revisión humana.
4. **Autenticación, seguridad y disponibilidad** (`backend/app/api/v1/auth.py`, `backend/app/core/`, `backend/app/repositories/session_repository.py`):
   - Las sesiones se persisten en PostgreSQL, admiten revocación y respetan RBAC.
   - Se endurecieron la política de contraseñas y la asociación segura de pacientes.
   - El LLM opera en modo seguro: `ALLOW_MOCK_LLM=false` por defecto y devuelve `503` cuando el proveedor real no está disponible.
   - Los endpoints de salud verifican PostgreSQL y los errores de conexión se reportan como indisponibilidad del servicio.

### 🎨 3. Frontend & UX (React / Vite / TypeScript / CSS)

1. **Migración completa a TypeScript estricto** (`frontend/src/**/*.tsx`, `frontend/tsconfig.app.json`):
   - Se migraron los componentes `.jsx` y utilidades `.js` restantes a `.tsx`/`.ts`, con props y respuestas API tipadas.
   - `strict` permanece activo y `allowJs` fue deshabilitado.
2. **Cliente HTTP y flujos reales** (`frontend/src/api/httpClient.ts`, `frontend/src/api/triage.api.ts`, `frontend/src/api/documentsApi.ts`, `frontend/src/api/auditApi.ts`):
   - Se unificaron base URL, encabezado Bearer, serialización y tratamiento de errores.
   - La recepción usa `/triage/upload` y la auditoría usa el `PATCH` real, sin resultados simulados en `localStorage`.
3. **Sistema UX clínico estandarizado** (`frontend/src/components/common/`, `frontend/src/styles/`, `frontend/src/pages/`):
   - Se unificaron encabezados, tablas, formularios, modales, estados vacíos, carga y error.
   - Se mejoraron accesibilidad, foco, contraste, navegación responsiva y consistencia de acciones.
   - Las rutas se cargan de forma diferida para reducir el paquete inicial y los filtros usan el catálogo clínico normalizado.

### 🐳 4. Infraestructura, Scripts & Documentación

1. **Despliegue integral con contenedores** (`backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `infrastructure/docker/docker-compose.yml`):
   - Se configuraron PostgreSQL, backend y frontend, volúmenes, comprobaciones de salud y proxy Nginx.
   - La imagen del backend instala Tesseract y el paquete de idioma español.
2. **Contrato y guías actualizados** (`specs/openapi.yaml`, `specs/paths/`, `specs/components/`, `README.md`, `Makefile`, `Docs/BASE_DE_DATOS.md`):
   - OpenAPI documenta autenticación, usuarios, pacientes, configuración, carga, historial, catálogos y respuestas `409`/`503`.
   - Se actualizaron comandos de desarrollo, despliegue y credenciales semilla seguras.

---

## 🧪 Verificación y Pruebas

- **Backend (Pytest)**: `66 passed in 5.22s`.
- **Calidad Python**: `ruff check app tests` sin hallazgos y `mypy app` sin errores.
- **Frontend (ESLint)**: `npm run lint` completado sin errores.
- **Frontend (TypeScript)**: `npm run build` exitoso; 78 módulos transformados y paquete principal de 312.59 kB.
- **Migraciones (Alembic)**: `alembic upgrade head` aplicado y `alembic current` en `n7o707411jk3 (head)`.
- **Seguridad de acceso**: credencial semilla anterior rechazada y nueva credencial verificada contra PostgreSQL.
- **Docker**: configuración revisada estáticamente; la construcción/ejecución de contenedores no pudo probarse porque Docker CLI no está instalado en el entorno actual.
