# MediFlow — Arquitectura SDD (Spec-Driven Development)
### Hackathon ONE G10 · Oracle Next Education & Alura

---

## ¿Qué es MediFlow?

**Agente Autónomo de Triaje Clínico** que recibe documentos médicos (PDF, imagen, texto), los clasifica con LLMs multimodales, extrae datos estructurados y los enruta automáticamente a la cola correcta (Urgencia / Rutina / Auditoría Humana), persistiendo todo en **OCI Object Storage**.

---

## Stack Definido (del documento)

| Capa | Tecnología |
|---|---|
| **Agente IA** | LangGraph (grafo de decisión con nodos condicionales) |
| **LLM** | Google Gemini (primario), OpenAI GPT-4o / Claude (opcionales) |
| **Backend** | Python + FastAPI |
| **Validación** | Pydantic |
| **Frontend** | React + Vite + TypeScript |
| **Almacenamiento** | OCI Object Storage (Always Free) |
| **Infraestructura** | Docker Compose + scripts Python |
| **SDD** | OpenAPI 3.1 como contrato |

---

## Estructura de Directorios

```
G10-LATAM-TEAM-02-MediFlowI-Agente-IA/
│
├── specs/                              # ← FUENTE DE VERDAD SDD
│   ├── openapi.yaml                    # Contrato API principal (OpenAPI 3.1)
│   ├── components/
│   │   ├── schemas.yaml                # DocumentoClinico, ResultadoTriaje, etc.
│   │   └── responses.yaml
│   └── paths/
│       ├── triage.yaml                 # POST /triage
│       ├── documents.yaml              # GET/POST /documents
│       └── health.yaml                 # GET /health
│
├── backend/                            # Python + FastAPI + LangGraph
│   ├── app/
│   │   ├── _generated/                 # ← AUTO-GENERADO desde spec (NO editar)
│   │   │   ├── models.py               # Pydantic models (desde schemas.yaml)
│   │   │   └── routers/                # Stubs de endpoints
│   │   │       ├── triage_stub.py
│   │   │       └── documents_stub.py
│   │   │
│   │   ├── api/                        # ← Implementación MANUAL
│   │   │   └── v1/
│   │   │       ├── triage.py           # POST /triage - endpoint principal
│   │   │       ├── documents.py        # CRUD de documentos
│   │   │       └── health.py
│   │   │
│   │   ├── agent/                      # ← Núcleo del Agente IA (LangGraph)
│   │   │   ├── graph.py                # Definición del grafo de decisión
│   │   │   ├── nodes/
│   │   │   │   ├── ingestion.py        # Nodo: Ingestión y parsing de PDF/imagen
│   │   │   │   ├── extraction.py       # Nodo: Extracción de entidades con LLM
│   │   │   │   ├── classification.py   # Nodo: Clasificación tipo doc + prioridad
│   │   │   │   ├── confidence.py       # Nodo: Score de confianza
│   │   │   │   └── routing.py          # Nodo: Decisión de enrutamiento
│   │   │   ├── edges/
│   │   │   │   └── conditional.py      # Conditional edges (Urgente/Rutina/Ambiguo)
│   │   │   └── state.py                # AgentState: estado compartido del grafo
│   │   │
│   │   ├── services/                   # Lógica de negocio (manual)
│   │   │   ├── triage_service.py       # Orquesta el agente LangGraph
│   │   │   ├── document_service.py     # Procesamiento de documentos
│   │   │   └── llm_service.py          # Abstracción LLM (Gemini/OpenAI/Claude)
│   │   │
│   │   ├── repositories/
│   │   │   └── oci_storage.py          # OCI Object Storage (buckets)
│   │   │
│   │   ├── core/
│   │   │   ├── config.py               # Settings via pydantic-settings
│   │   │   ├── dependencies.py         # DI: LLM client, OCI client
│   │   │   └── security.py             # API key validation (simple)
│   │   │
│   │   └── main.py                     # Entry point FastAPI
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_agent_nodes.py
│   │   │   └── test_services.py
│   │   ├── integration/
│   │   │   └── test_triage_endpoint.py
│   │   └── contract/                   # Schemathesis: tests automáticos desde spec
│   │       └── test_openapi_contract.py
│   │
│   ├── pyproject.toml                  # uv/poetry deps
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/                           # React + Vite + TypeScript
│   ├── src/
│   │   ├── _generated/                 # ← AUTO-GENERADO desde spec
│   │   │   └── api/                    # Cliente TypeScript (@hey-api/openapi-ts)
│   │   │       ├── types.ts
│   │   │       └── services.ts
│   │   │
│   │   ├── api/                        # Wrappers manuales sobre cliente generado
│   │   │   └── triage.api.ts
│   │   │
│   │   ├── components/
│   │   │   ├── DocumentUploader.tsx    # Upload de PDF/imagen
│   │   │   ├── TriageResult.tsx        # Visualización resultado triaje
│   │   │   ├── AuditPanel.tsx          # Human-in-the-Loop (diferencial)
│   │   │   └── PriorityBadge.tsx       # Badge Urgente/Rutina/Ambiguo
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx           # Panel principal
│   │   │   └── Audit.tsx               # Cola de auditoría humana
│   │   │
│   │   ├── hooks/
│   │   │   └── useTriage.ts
│   │   │
│   │   └── main.tsx
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── .env.example
│
├── infrastructure/                     # Orquestación y despliegue
│   ├── docker/
│   │   ├── docker-compose.yml          # Producción
│   │   └── docker-compose.dev.yml      # Dev con hot-reload
│   │
│   ├── scripts/
│   │   ├── generate.py                 # SDD: genera _generated/ desde openapi.yaml
│   │   ├── validate_spec.py            # Valida spec con Spectral
│   │   └── dev.py                      # Levanta servicios en modo dev
│   │
│   └── nginx/
│       └── nginx.conf                  # Reverse proxy: / → frontend, /api → backend
│
├── Docs/
│   └── Documento-Proyecto-Mediflow.pdf
│
├── Makefile                            # Comandos unificados
├── pyproject.toml                      # Python raíz (scripts infra)
└── README.md
```

---

## Flujo SDD — De spec a código

```
┌─────────────────────────┐
│  1. Editar              │
│  specs/openapi.yaml     │  ← Contrato del endpoint /triage, schemas, responses
└────────┬────────────────┘
         │
         ▼   make generate
┌─────────────────────────┐
│  infrastructure/        │  ← Script Python usa openapi-generator-cli
│  scripts/generate.py    │
└───┬─────────────────────┘
    │
    ├──► backend/app/_generated/models.py        (Pydantic desde schemas)
    ├──► backend/app/_generated/routers/         (Stubs de endpoints)
    └──► frontend/src/_generated/api/            (Cliente TypeScript tipado)
         │
         ▼
  3. Implementar manualmente:
  backend/app/api/v1/triage.py   ← usa los modelos generados
  frontend/src/api/triage.api.ts ← wrappea el cliente generado
```

---

## Flujo del Agente LangGraph

```
Documento (PDF/img/text)
         │
         ▼
   [Nodo: ingestion]          → Extrae texto (PyMuPDF / Tesseract OCR)
         │
         ▼
   [Nodo: extraction]         → LLM extrae entidades clínicas (Gemini)
         │                       Paciente, médico, diagnóstico, CIE-10
         ▼
   [Nodo: classification]     → Clasifica tipo doc + nivel prioridad
         │
         ▼
   [Nodo: confidence]         → Calcula score_confianza (0.0 - 1.0)
         │
         ▼
   [Conditional Edge]
         │
    ┌────┴────────┬─────────────────┐
    ▼             ▼                 ▼
score > 0.8   score 0.5-0.8    score < 0.5
    │             │                 │
[URGENTE/    [RUTINA]         [AMBIGUO →
 EMERGENCIA]                  Auditoría
    │             │            Humana]
    ▼             ▼                 ▼
Cola_Emergencia  Cola_Rutina   Cola_Auditoria
    └─────────────┴─────────────────┘
                  │
                  ▼
         OCI Object Storage
         /procesados/urgentes/
         /procesados/rutina/
         /auditoria_humana/
```

---

## Comunicación entre servicios

```
┌──────────────┐   :5173   ┌─────────────┐  nginx  ┌──────────────┐
│  frontend    │ ────────► │    nginx    │ ──────► │   backend    │
│  React/Vite  │           │   :80       │         │  FastAPI:8000│
└──────────────┘           └─────────────┘         └──────┬───────┘
                                                          │
                                               ┌──────────┴──────────┐
                                               │                     │
                                               ▼                     ▼
                                         LangGraph Agent      OCI Object Storage
                                         (in-process)         (cloud, Always Free)
```

> **Sin base de datos local**: Los documentos se almacenan directamente en OCI Object Storage, siguiendo el requisito obligatorio del proyecto.

---

## Makefile — Comandos

```makefile
make validate      # Valida specs/openapi.yaml con Spectral
make generate      # Genera _generated/ en backend y frontend
make dev           # docker compose up --build (dev con hot-reload)
make test          # pytest + contract tests (schemathesis)
make docs          # Abre http://localhost:8000/docs (Swagger UI)
make build         # Build producción
```

---

## Herramientas SDD

| Herramienta | Propósito |
|---|---|
| `openapi-generator-cli` | Genera stubs Python y modelos Pydantic desde spec |
| `@hey-api/openapi-ts` | Genera cliente TypeScript tipado para React |
| `spectral` | Linting / validación del spec OpenAPI |
| `schemathesis` | Contract testing automático desde openapi.yaml |
| `pydantic-settings` | Config tipada desde env vars |

---

## Casos de prueba mínimos (del documento)

| # | Escenario | Resultado esperado |
|---|---|---|
| 1 | Documento de rutina (analítica normal) | `nivel_prioridad: "Rutina"`, ruta `/procesados/rutina/` |
| 2 | Informe de TEP agudo (urgencia médica) | `nivel_prioridad: "Urgente"`, alerta generada |
| 3 | Documento ambiguo / ilegible | `requiere_auditoria_humana: true`, ruta `/auditoria_humana/` |

---

## Archivos a crear (ejecución)

### Fase 1 — Spec
- [ ] `specs/openapi.yaml` — Contrato con `/triage`, `/documents`, `/health`
- [ ] `specs/components/schemas.yaml` — `DocumentoClinico`, `ResultadoTriaje`, `DatosExtraidos`

### Fase 2 — Backend
- [ ] `backend/pyproject.toml` — deps: fastapi, langgraph, langchain-google-genai, pydantic, oci, pymupdf
- [ ] `backend/app/main.py`
- [ ] `backend/app/core/config.py`
- [ ] `backend/app/agent/graph.py` + nodos
- [ ] `backend/app/services/triage_service.py`
- [ ] `backend/app/repositories/oci_storage.py`
- [ ] `backend/Dockerfile`
- [ ] `backend/.env.example`

### Fase 3 — Frontend
- [ ] Scaffold con `create-vite` (React + TypeScript)
- [ ] Componentes: `DocumentUploader`, `TriageResult`, `AuditPanel`
- [ ] `frontend/Dockerfile`

### Fase 4 — Infrastructure
- [ ] `infrastructure/docker/docker-compose.dev.yml`
- [ ] `infrastructure/scripts/generate.py`
- [ ] `infrastructure/scripts/validate_spec.py`
- [ ] `infrastructure/nginx/nginx.conf`
- [ ] `Makefile`
- [ ] `README.md` (actualizado)

---

## Verification Plan

- `make validate` → Spectral valida spec sin errores
- `make generate` → `_generated/` se popula en backend y frontend
- `make dev` → Backend `:8000/docs` + Frontend `:5173` accesibles
- Test case 1, 2 y 3 pasan con `make test`
- OCI Object Storage recibe los documentos procesados
