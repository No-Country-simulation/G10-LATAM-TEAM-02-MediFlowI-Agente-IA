# 14. 🚀 Pull Request #14 — 2026-09-25

Este documento registra el Pull Request número 14 del día **2026-09-25** para el proyecto **MediFlow**.

---

## 🔀 14. PR #14 — Cierre integral de plataforma clínica, persistencia, UX y seguridad

### 📌 Datos del Pull Request

- **Título del PR**: `feat(platform): cerrar backlog crítico, UX, persistencia y seguridad clínica`
- **Número de PR**: 14 (PR #14 del día 2026-09-25)
- **Fecha**: 2026-09-25
- **Autor**: Erick Pariona
- **Rama de Origen**: `dev-erick-pariona`
- **Rama de Destino**: `develop`
- **Proyecto**: MediFlow — Agente Autónomo de Triaje Clínico Multimodal
- **Historial de Cambios Asociado**: [`HISTORIAL_CAMBIOS_2026-09-25_CAMBIO14.md`](../historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO14.md)

---

### 📋 Resumen del PR

Este PR integra el cierre del backlog crítico identificado en MediFlow. Conecta los flujos de carga y auditoría con el backend real, establece PostgreSQL como fuente única de verdad, refuerza sesiones y credenciales, habilita OCR real, normaliza el catálogo clínico, completa la migración del frontend a TypeScript y estandariza la experiencia de usuario. Además, deja preparado el despliegue conjunto de base de datos, backend y frontend mediante Docker.

---

### 🛠️ Cambios Detallados por Capa Técnica

#### 🗄️ Base de Datos & Migraciones

- Nueva persistencia de sesiones revocables mediante hashes, vencimiento, índices y comentarios SQL.
- Rotación condicional de la credencial semilla débil sin sobrescribir claves personalizadas.
- Revocación de sesiones previas vinculadas con la credencial semilla.
- Eliminación de almacenes en memoria para datos clínicos y configuración; PostgreSQL queda como fuente única de verdad.
- Reutilización de `paciente_id` e `historial_documento`, sin migración redundante para DNI/HC.

#### ⚙️ Backend & Agente IA

- Endpoints reales para carga, consulta, historial y resolución de auditorías, con semántica `409` y `503`.
- Validación de tamaño, MIME y firma de archivos antes del procesamiento.
- Almacenamiento LOCAL/OCI controlado exclusivamente por la configuración manual persistida.
- OCR con Tesseract español para imágenes y respaldo para documentos PDF.
- Catálogo clínico normalizado y procesamiento incremental dentro de los cinco nodos de LangGraph.
- Sesiones persistentes, RBAC, política de contraseñas, asociación segura de pacientes y comprobación de salud de PostgreSQL.
- Ejecución LLM en modo seguro, sin simulación automática en producción.

#### 🎨 Frontend & UX

- Migración total de JavaScript/JSX a TypeScript/TSX con configuración estricta.
- Cliente HTTP tipado y centralizado con autenticación Bearer y errores normalizados.
- Carga documental y auditoría conectadas a endpoints reales.
- Componentes comunes para encabezados, tablas, formularios, confirmaciones, carga, error y estados vacíos.
- Mejoras de accesibilidad, diseño responsivo, foco, contraste y estados seleccionados.
- Catálogo clínico compartido en filtros y carga diferida de rutas.

#### 🐳 Infraestructura & Documentación

- Dockerfiles completos para backend y frontend, proxy Nginx y Compose con PostgreSQL, volúmenes y health checks.
- Instalación de Tesseract con idioma español en la imagen backend.
- Contrato OpenAPI ampliado para autenticación, usuarios, pacientes, configuración, documentos y triaje.
- README, Makefile y documentación de base de datos sincronizados con la operación actual.

---

### 🛠️ Archivos Modificados / Creados

| Tipo de Cambio | Ruta del Archivo | Descripción del Cambio |
| :--- | :--- | :--- |
| **Nuevo** | `backend/alembic/versions/m6n606300ij2_add_persistent_user_sessions.py` | Persistencia y revocación de sesiones. |
| **Nuevo** | `backend/alembic/versions/n7o707411jk3_rotate_weak_seed_credentials.py` | Rotación segura de credenciales semilla. |
| **Nuevo / Modificado** | `backend/app/agent/`, `backend/app/api/v1/`, `backend/app/repositories/`, `backend/app/services/` | Catálogo clínico, OCR, persistencia, seguridad y endpoints reales. |
| **Nuevo / Modificado** | `backend/tests/` | Cobertura de API, migraciones, catálogo, sesiones, salud y almacenamiento. |
| **Migrado / Modificado** | `frontend/src/` | Migración TS/TSX, cliente HTTP, componentes comunes y UX estandarizada. |
| **Nuevo / Modificado** | `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `infrastructure/docker/` | Despliegue integral de la plataforma. |
| **Modificado** | `specs/`, `README.md`, `Makefile`, `Docs/BASE_DE_DATOS.md` | Contrato API y documentación operativa. |

---

### 🏆 Checklist de la Regla de Oro

- [x] **PostgreSQL es la Fuente Única de Verdad**: persistencia garantizada en `mediflow_dev`.
- [x] **Control 100% Manual de Almacenamiento**: selección LOCAL/OCI controlada manualmente por el usuario.
- [x] **Pruebas Backend Passing**: `pytest` 100% exitoso sin mutar automáticamente el modo de almacenamiento.
- [x] **Compilación Frontend Limpia**: `npm run build` sin errores de TypeScript.
- [x] **Migraciones Alembic Sincronizadas**: base de datos en `n7o707411jk3 (head)`.

---

### 🧪 Verificación y Pruebas

1. `cd backend && .\.venv\Scripts\python.exe -m pytest -q` → **66 pruebas exitosas**.
2. `cd backend && .\.venv\Scripts\ruff.exe check app tests` → **sin hallazgos**.
3. `cd backend && .\.venv\Scripts\mypy.exe app` → **sin errores**.
4. `cd frontend && npm run lint` → **exitoso**.
5. `cd frontend && npm run build` → **exitoso, 78 módulos transformados**.
6. `cd backend && .\.venv\Scripts\alembic.exe upgrade head` y `alembic current` → **`n7o707411jk3 (head)`**.

> **Nota de entorno**: la configuración Docker fue revisada, pero no se ejecutó una construcción de imágenes porque Docker CLI no está instalado en el equipo de verificación.
