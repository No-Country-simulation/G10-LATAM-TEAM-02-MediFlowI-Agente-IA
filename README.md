# 🏥 MediFlow — Agente Autónomo de Triaje Clínico

> **Hackathon ONE G10 · Oracle Next Education & Alura**

Agente autónomo que recibe documentos clínicos (PDF, imagen, texto), los clasifica con **LLMs multimodales (Google Gemini)**, extrae entidades estructuradas y los enruta automáticamente a la cola correcta, persistiendo todo en **OCI Object Storage** (Always Free).

---

## 🏗️ Arquitectura

```
G10-LATAM-TEAM-02-MediFlowI-Agente-IA/
├── specs/              ← FUENTE DE VERDAD (OpenAPI 3.1)
├── backend/            ← Python + FastAPI + LangGraph
├── frontend/           ← React + Vite + TypeScript
└── infrastructure/     ← Docker Compose + scripts SDD + Nginx
```

### Flujo del Agente (LangGraph)

```
Documento → [ingestion] → [extraction] → [classification] → [confidence]
          → Cola_Emergencia_Medica  (score > 0.8 + Urgente)
          → Cola_Rutina             (score > 0.8 + Rutina)
          → Cola_Auditoria_Humana   (score < 0.5 o Ambiguo)
          → OCI Object Storage
```

### Flujo SDD (Spec-Driven Development)

```
specs/openapi.yaml  →  make generate  →  _generated/  →  implementación manual
```

---

## 🚀 Inicio Rápido

### Pre-requisitos
- Python 3.11+
- Node.js 20+
- Docker + Docker Compose (opcional)

### 1. Clonar y configurar
```bash
git clone https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA
cd G10-LATAM-TEAM-02-MediFlowI-Agente-IA

# Copiar y configurar variables de entorno
cp backend/.env.example backend/.env
# Editar backend/.env con tu GOOGLE_API_KEY y credenciales OCI
```

### 2. Levantar en desarrollo
```bash
make dev          # Backend :8000 + Frontend :5173 (sin Docker)
# o
make dev-docker   # Todo en Docker con hot-reload
```

### Despliegue completo con Docker

El stack incluye PostgreSQL 17, FastAPI con todas sus dependencias, OCR Tesseract
en español, migraciones automáticas de Alembic y el frontend compilado servido por
Nginx. No es necesario instalar Python, Node.js ni Tesseract en el equipo anfitrión.

```bash
# Opcional: configurar claves LLM/OCI y seguridad
cp backend/.env.example backend/.env

# Construir y levantar frontend, backend y PostgreSQL
docker compose -f infrastructure/docker/docker-compose.yml up --build -d

# Ver estado y logs
docker compose -f infrastructure/docker/docker-compose.yml ps
docker compose -f infrastructure/docker/docker-compose.yml logs -f
```

También puede usarse `make docker-up`. Los datos de PostgreSQL y los documentos
almacenados en modo `LOCAL` se conservan en volúmenes Docker. Para detener sin
borrar información use `make docker-down`.

Accesos del despliegue Docker:

- Aplicación y API mediante proxy: `http://localhost`
- Swagger UI: `http://localhost/docs`
- Backend directo para diagnóstico: `http://localhost:8000`
- Desarrollo con recarga: `http://localhost:5173`

### 3. Acceder
- **Frontend**: http://localhost:5173
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Credencial administrativa inicial de desarrollo:

- **DNI**: `12345678`
- **Contraseña**: `MediFlow#Admin2026`

Esta cuenta es únicamente para desarrollo. Cambie su contraseña antes de
exponer MediFlow en una red compartida.

---

## 🔧 Comandos

| Comando | Descripción |
|---|---|
| `make validate` | Valida `specs/openapi.yaml` con Spectral |
| `make generate` | Genera `_generated/` desde el spec (SDD) |
| `make dev` | Desarrollo local (sin Docker) |
| `make dev-docker` | Docker Compose con hot-reload |
| `make test` | Todos los tests |
| `make test-contract` | Contract tests desde OpenAPI spec |
| `make docs` | Abre Swagger UI |
| `make build` | Build producción |

---

## 🧪 Casos de Prueba

```json
// Caso 1: Rutina
{ "documento_id": "DOC-001", "tipo_archivo": "TEXTO",
  "documento_texto": "Analítica normal. Sin hallazgos.", "canal_origen": "Consulta_Externa" }
// → Cola_Rutina

// Caso 2: Urgencia (TEP Agudo)
{ "documento_id": "DOC-002", "tipo_archivo": "TEXTO",
  "documento_texto": "TEP agudo detectado. Correlación clínica urgente.", "canal_origen": "Guardia_Emergencias" }
// → Cola_Emergencia_Medica + ALERTA

// Caso 3: Ambiguo
{ "documento_id": "DOC-003", "tipo_archivo": "TEXTO",
  "documento_texto": "... texto ilegible ... px ... mgr ???", "canal_origen": "Admision" }
// → Cola_Auditoria_Humana (Human-in-the-Loop)
```

---

## 📚 Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Agente IA | LangGraph + Google Gemini |
| Backend | Python 3.11 + FastAPI + Pydantic |
| Frontend | React 18 + Vite + TypeScript |
| Almacenamiento | OCI Object Storage (Always Free) |
| Infraestructura | Docker Compose + Nginx |
| SDD | OpenAPI 3.1 → datamodel-codegen + @hey-api/openapi-ts |

---

## 📄 Licencia

MIT — Ver [LICENSE](LICENSE)
