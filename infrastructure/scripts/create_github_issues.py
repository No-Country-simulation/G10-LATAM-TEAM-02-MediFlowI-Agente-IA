#!/usr/bin/env python3
"""
MediFlow — Script de Automatización de GitHub Issues y Milestones.

Lee las 16 Historias de Usuario oficiales del Product Backlog (Docs/backlog.md)
y las publica o actualiza en el repositorio usando la CLI de GitHub (`gh`).

Estructura enriquecida inspirada en las mejores prácticas de ingeniería:
  - Descripción narrativa (User Story)
  - Tabla de Metadata (Épica, Sprint, Roles, Estimación, Dependencias, Commit sugerido)
  - Entregables específicos (rutas y módulos concretos)
  - Criterios de Aceptación verificables (- [ ])
  - Convenciones de PR y Commits (Conventional Commits, PR a develop, Squash & Merge)

Nota de gobernanza de ramas:
  Cada desarrollador trabaja en su rama personal (ej. dev-<nombre>) y abre PR hacia develop.

Uso:
  python infrastructure/scripts/create_github_issues.py [--dry-run] [--repo OWNER/REPO]
"""

import argparse
import subprocess
import sys
from typing import Dict, List, Any

# ── Configuración de Milestones (Sprints Oficiales) ───────────────────────────
MILESTONES = [
    {
        "title": "Sprint 1: Fundamentos y Contratos",
        "description": "Establecer contrato OpenAPI, generación tipada, mockups Figma y Docker Dev. Semana 1 (21/09 - 27/09).",
    },
    {
        "title": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "description": "Nodos LangGraph, FastAPI mocks, SDK OCI y Frontend React. Semanas 2 y 3 (28/09 - 11/10).",
    },
    {
        "title": "Sprint 3: Integración del Núcleo",
        "description": "Conectar FastAPI con LangGraph/Gemini real, persistencia en OCI y panel Human-in-the-Loop. Semana 4 (12/10 - 18/10).",
    },
    {
        "title": "Sprint 4: Orquestación, QA y Cierre",
        "description": "Nginx proxy, Contract Testing, Smoke Tests E2E, Video Demo en YouTube y cierre. Semana 5 (19/10 - 25/10).",
    },
]

# ── Configuración de Labels (Etiquetas por Épica y Rol) ───────────────────────
LABELS = [
    {"name": "sprint:1", "color": "0E8A16", "description": "Historias del Sprint 1"},
    {"name": "sprint:2", "color": "FBCA04", "description": "Historias del Sprint 2"},
    {"name": "sprint:3", "color": "D93F0B", "description": "Historias del Sprint 3"},
    {"name": "sprint:4", "color": "B60205", "description": "Historias del Sprint 4"},
    {"name": "epic:ingestion", "color": "1D76DB", "description": "ÉPICA 1: Ingestión Multimodal"},
    {"name": "epic:langgraph", "color": "5319E7", "description": "ÉPICA 2: Grafo de Decisión Cognitiva"},
    {"name": "epic:core-api", "color": "0052CC", "description": "ÉPICA 3: Core API REST y OCI"},
    {"name": "epic:ui-ux", "color": "C2E0C6", "description": "ÉPICA 4: Dashboard y Human-in-the-Loop"},
    {"name": "epic:qa", "color": "D4C5F9", "description": "ÉPICA 5: Aseguramiento de Calidad"},
    {"name": "epic:cloud-infra", "color": "006B75", "description": "ÉPICA 6: Infraestructura Cloud y Demo"},
    {"name": "role:backend", "color": "BFD4F2", "description": "Backend Developer"},
    {"name": "role:frontend", "color": "D4C5F9", "description": "Frontend Developer"},
    {"name": "role:ai-data", "color": "E99695", "description": "AI / LLM & Data Engineer"},
    {"name": "role:devops", "color": "F9D0C4", "description": "DevOps & Cloud Engineer"},
    {"name": "role:qa", "color": "FEF2C0", "description": "QA Engineer / Tester"},
    {"name": "role:ui-ux", "color": "C5DEF5", "description": "UI/UX Designer"},
    {"name": "priority:must-have", "color": "B60205", "description": "Prioridad Alta (Must Have)"},
    {"name": "priority:should-have", "color": "FBCA04", "description": "Prioridad Media (Should Have)"},
]

# ── Catálogo Enriquecido de las 16 Historias de Usuario (Docs/backlog.md) ──────
ISSUES: List[Dict[str, Any]] = [
    # ── SPRINT 1 ──
    {
        "id": "US-01",
        "title": "[US-01] Definición del Contrato OpenAPI 3.1 y Generación de Tipos (SDD)",
        "milestone": "Sprint 1: Fundamentos y Contratos",
        "labels": ["sprint:1", "epic:core-api", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como Tech Lead y Desarrolladores (Backend/Frontend), quiero definir el contrato central en `specs/openapi.yaml` con endpoints (`/triage`, `/documents`, `/health`), schemas de datos médicos y respuestas HTTP tipadas, y generar el código base con `make generate`, para que Frontend y Backend cuenten con una única fuente de verdad técnica y tipos fuertemente tipados (Pydantic y TypeScript) desde el día 1.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 3 — Core API REST, Arquitectura SDD y Persistencia Serverless |
| **Sprint** | Sprint 1 (Semana 1: 21/09 - 27/09) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta - Bloqueante) |
| **Roles Responsables** | Tech Lead (SDD) & Backend Developer |
| **Dependencias** | Ninguna (Punto de partida del proyecto) |
| **Commit Ejemplo** | `feat(US-01): definir contrato openapi 3.1 y generacion tipada pydantic/ts` |

## Entregables
- Especificación oficial `specs/openapi.yaml` (OpenAPI 3.1.0) con schemas clínicos completos.
- Modelos Pydantic compilados en `backend/app/_generated/`.
- Tipos e interfaces TypeScript compilados en `frontend/src/_generated/`.
- Reglas de validación Spectral en `.spectral.yaml` y comando `make validate` funcional.

## Criterios de Aceptación
- [ ] `specs/openapi.yaml` es válido según Spectral (`make validate` pasa con 0 errores).
- [ ] El comando `make generate` compila los modelos Pydantic en `backend/app/_generated/` y tipos TS en `frontend/src/_generated/`.
- [ ] Esquemas clínicos modelados: `DocumentoClinico`, `ResultadoTriaje`, `EntidadesMedicas`, `PrioridadTriaje`.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-01): definición de contrato openapi 3.1 y generación de tipos sdd`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-02",
        "title": "[US-02] Sistema de Diseño Clínico y Mockups UX/UI en Figma",
        "milestone": "Sprint 1: Fundamentos y Contratos",
        "labels": ["sprint:1", "epic:ui-ux", "role:ui-ux", "role:frontend", "priority:must-have"],
        "body": """## Descripción
Como Diseñador UI/UX y Equipo Frontend, quiero diseñar en Figma los flujos e interfaces de alta fidelidad: Uploader de documentos, Dashboard de colas de triaje y Panel de Auditoría médica, para guiar la maquetación visual del frontend sin ambigüedades y asegurando ergonomía clínica para personal bajo estrés.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 4 — Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX |
| **Sprint** | Sprint 1 (Semana 1: 21/09 - 27/09) |
| **Estimación** | 3 Story Points |
| **Prioridad** | MUST HAVE (Alta - Bloqueante) |
| **Roles Responsables** | UI/UX Designer & Frontend Developer |
| **Dependencias** | Requerimientos clínicos de la visión del producto |
| **Commit Ejemplo** | `docs(US-02): enlace a prototipo interactivo figma y guia de diseño clinico` |

## Entregables
- Archivo o link público interactivo de Figma con prototipos de alta fidelidad.
- Guía de estilos y paleta clínica de severidad documentada (`Docs/design-system.md` o README).
- Especificaciones de layout para 3 vistas: Dashboard, Detalle/Auditoría y Módulo de Carga.

## Criterios de Aceptación
- [ ] Prototipo navegable en Figma de las 3 vistas principales (Dashboard, Detalle/Auditoría, Carga de Archivos).
- [ ] Paleta de severidad médica estandarizada: Emergencia (#EF4444), Urgente (#F59E0B), Rutina (#10B981), Auditoría (#3B82F6).
- [ ] Aprobación visual del Product Owner.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `design(US-02): prototipos figma y sistema de diseño clínico`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-03",
        "title": "[US-03] Estabilización de Entorno Local Docker Compose",
        "milestone": "Sprint 1: Fundamentos y Contratos",
        "labels": ["sprint:1", "epic:cloud-infra", "role:devops", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como Desarrollador del equipo, quiero contar con un entorno Docker Compose funcional (`make dev-docker`) con hot-reload tanto para Backend como Frontend, para levantar el proyecto en un comando sin discrepancias de librerías ni fallos de empaquetado en local.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 6 — Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales |
| **Sprint** | Sprint 1 (Semana 1: 21/09 - 27/09) |
| **Estimación** | 3 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | DevOps / Cloud Engineer & Backend Developer |
| **Dependencias** | Configuración base del repositorio en `dev-wilmer-gulcochia` |
| **Commit Ejemplo** | `fix(docker): corregir contexto de build hatchling y docker-compose dev` |

## Entregables
- `backend/Dockerfile` optimizado y compilable mediante Hatchling.
- `docker-compose.dev.yml` con montaje de volúmenes y hot-reload para backend y frontend.
- `backend/.env.example` y `frontend/.env.example` con variables de entorno exhaustivas.
- Target `dev-docker` validado en `Makefile`.

## Criterios de Aceptación
- [ ] `backend/Dockerfile` compila limpiamente sin errores de Hatchling (`README.md` y `app/` copiados en orden).
- [ ] `docker-compose.dev.yml` levanta Backend (:8000) y Frontend (:5173) con hot-reload activo.
- [ ] `backend/.env.example` documenta todas las variables requeridas (Gemini, OCI, App).

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `build(US-03): estabilización del entorno de desarrollo docker compose`
- **Merge Strategy:** Squash and merge
""",
    },

    # ── SPRINT 2 ──
    {
        "id": "US-04",
        "title": "[US-04] Ingestión y Parsing de Documentos Clínicos (PyMuPDF)",
        "milestone": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "labels": ["sprint:2", "epic:ingestion", "role:backend", "role:ai-data", "priority:must-have"],
        "body": """## Descripción
Como Médico / Administrativo de admisión, quiero subir archivos médicos (PDF, JPG, PNG) al endpoint `POST /api/v1/documents` y extraer su texto íntegro, para alimentar al agente de triaje sin requerir transcripción manual de recetas u órdenes.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 1 — Ingestión Multimodal y Extracción Clínica Inteligente |
| **Sprint** | Sprint 2 (Semanas 2 y 3: 28/09 - 11/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | Backend Developer & AI/LLM Engineer |
| **Dependencias** | US-01 (Modelos Pydantic autogenerados) |
| **Commit Ejemplo** | `feat(US-04): parsing de documentos clinicos pdf e imagenes con pymupdf` |

## Entregables
- Servicio de extracción en `backend/app/services/document_parser.py` con PyMuPDF (`fitz`).
- Controlador de endpoint `POST /api/v1/documents` en `backend/app/api/v1/endpoints/documents.py`.
- Suite de pruebas unitarias en `backend/tests/test_document_parser.py` con archivos sintéticos.

## Criterios de Aceptación
- [ ] Soporte para `multipart/form-data` hasta 10 MB con validación estricta de tipos MIME.
- [ ] Extracción limpia de texto de PDFs multipágina mediante `PyMuPDF`.
- [ ] Manejo defensivo de errores devolviendo HTTP 400 descriptivo ante archivos corruptos o ilegibles.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-04): ingestión y extracción de texto de documentos con pymupdf`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-05",
        "title": "[US-05] Nodos de Extracción Clínica y Clasificación en LangGraph",
        "milestone": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "labels": ["sprint:2", "epic:ingestion", "epic:langgraph", "role:ai-data", "priority:must-have"],
        "body": """## Descripción
Como Agente de Triaje IA, quiero enviar el texto médico a Google Gemini 1.5 con prompts estructurados y clasificar el nivel de prioridad (Emergencia, Urgente, Rutina), para extraer entidades clínicas estructuradas (síntomas, diagnóstico, signos vitales) y clasificar la severidad preliminar.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 1 & ÉPICA 2 — Extracción Multimodal y Grafo de Decisión Cognitiva |
| **Sprint** | Sprint 2 (Semanas 2 y 3: 28/09 - 11/10) |
| **Estimación** | 8 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | AI / LLM & Data Engineer |
| **Dependencias** | US-01 (Modelos Pydantic) |
| **Commit Ejemplo** | `feat(US-05): implementar nodos de extraccion y clasificacion en langgraph` |

## Entregables
- Nodo de extracción `backend/app/agent/nodes/extraction.py`.
- Nodo de clasificación `backend/app/agent/nodes/classification.py`.
- Definición del estado del grafo `backend/app/agent/state.py`.
- Configuración de modelo LLM (`ChatGoogleGenerativeAI` con fallback) en `backend/app/agent/llm.py`.

## Criterios de Aceptación
- [ ] Nodos `extraction` y `classification` construidos dentro de `backend/app/agent/nodes/`.
- [ ] Invocación a Gemini (`ChatGoogleGenerativeAI`) con fallback configurado a OpenAI.
- [ ] Salida validada estrictamente contra el schema Pydantic `ExtractedMedicalData`.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-05): nodos de extracción y clasificación clínica en langgraph`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-06",
        "title": "[US-06] Algoritmo de Score de Confianza y Lógica de Enrutamiento",
        "milestone": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "labels": ["sprint:2", "epic:langgraph", "role:ai-data", "role:devops", "priority:must-have"],
        "body": """## Descripción
Como Auditor Médico de Calidad, quiero que el agente calcule un `confidence_score` (0.0 a 1.0) para cada triaje, para enrutar automáticamente a **Auditoría Humana** si `score < 0.8` o a la cola clínica respectiva si `score >= 0.8`.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 2 — Grafo de Decisión Cognitiva y Triaje Autónomo (LangGraph) |
| **Sprint** | Sprint 2 (Semanas 2 y 3: 28/09 - 11/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | AI / LLM & Data Engineer & DevOps (Apoyo) |
| **Dependencias** | US-05 (Nodos de extracción y clasificación) |
| **Commit Ejemplo** | `feat(US-06): calculo de confidence score y aristas de enrutamiento human-in-the-loop` |

## Entregables
- Nodo de cálculo de confianza `backend/app/agent/nodes/confidence.py`.
- Aristas condicionales de enrutamiento en `backend/app/agent/graph.py`.
- Pruebas del grafo con fixtures de casos ambiguos vs casos concluyentes en `backend/tests/test_graph_routing.py`.

## Criterios de Aceptación
- [ ] Nodo `confidence` pondera completitud de datos, certeza del LLM y consistencia de signos vitales.
- [ ] Aristas condicionales de LangGraph derivan a `COLA_AUDITORIA_HUMANA`, `COLA_EMERGENCIA` o `COLA_RUTINA`.
- [ ] Se registra la justificación clínica del score dentro del resultado.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-06): algoritmo de confidence score y enrutamiento a colas en langgraph`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-07",
        "title": "[US-07] Implementación de Endpoints FastAPI con Respuestas Mockeadas",
        "milestone": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "labels": ["sprint:2", "epic:core-api", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como Desarrollador Frontend, quiero que los endpoints `/api/v1/triage`, `/api/v1/triage/{id}` y `/api/v1/health` respondan en FastAPI con datos mock basados en el schema, para conectar el frontend y probar interacciones de red sin esperar a que el motor de IA esté 100% terminado.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 3 — Core API REST, Arquitectura SDD y Persistencia Serverless |
| **Sprint** | Sprint 2 (Semanas 2 y 3: 28/09 - 11/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | Backend Developer |
| **Dependencias** | US-01 (Modelos autogenerados OpenAPI) |
| **Commit Ejemplo** | `feat(US-07): stubs y endpoints mock de triaje en fastapi segun contrato` |

## Entregables
- Router de triaje en `backend/app/api/v1/endpoints/triage.py`.
- Router de estado en `backend/app/api/v1/endpoints/health.py`.
- Generador de datos sintéticos conformes al contrato en `backend/app/mocks/triage_mocks.py`.

## Criterios de Aceptación
- [ ] Endpoints implementados en `backend/app/api/v1/` devolviendo payloads conformes a `ResultadoTriaje`.
- [ ] Endpoint `GET /api/v1/health` operativo respondiendo status de salud.
- [ ] Respuestas compatibles con el cliente tipado de frontend.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-07): endpoints mockeados de triaje y health en fastapi`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-08",
        "title": "[US-08] SDK de Almacenamiento Serverless en OCI Object Storage",
        "milestone": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "labels": ["sprint:2", "epic:core-api", "epic:cloud-infra", "role:devops", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como Arquitecto de Software y Desarrollador Backend, quiero un módulo cliente (`oci_storage.py`) para subir y descargar archivos médicos y resultados JSON desde buckets de Oracle Cloud Infrastructure, para cumplir el reto de persistencia serverless sin depender obligatoriamente de base de datos local.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 3 & ÉPICA 6 — Persistencia Serverless e Infraestructura Cloud |
| **Sprint** | Sprint 2 (Semanas 2 y 3: 28/09 - 11/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | DevOps / Cloud Engineer & Backend Developer |
| **Dependencias** | Aprovisionamiento de Bucket y credenciales OCI en `.env` |
| **Commit Ejemplo** | `feat(US-08): cliente oci object storage con soporte para mock local` |

## Entregables
- Cliente OCI en `backend/app/storage/oci_client.py` con métodos de subida y consulta.
- Adaptador de almacenamiento local simulado (`backend/app/storage/local_mock_storage.py`) para desarrollo sin internet.
- Documentación de variables OCI en `backend/README.md`.

## Criterios de Aceptación
- [ ] Métodos funcionales: `upload_file`, `upload_json`, `get_file_url` (URLs pre-autenticadas PAR).
- [ ] Modo Mock local automático cuando no se configuren credenciales OCI en desarrollo.
- [ ] Manejo de excepciones y reintentos ante caídas transitorias de red.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-08): sdk de almacenamiento serverless en oci object storage`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-09",
        "title": "[US-09] Maquetación del Dashboard y Componentes UI con Cliente Tipado",
        "milestone": "Sprint 2: Desarrollo en Paralelo con Mocks",
        "labels": ["sprint:2", "epic:ui-ux", "role:frontend", "priority:must-have"],
        "body": """## Descripción
Como Personal médico de guardia, quiero una interfaz interactiva en React + Vite que muestre tarjetas de KPIs, tabla de casos por severidad y módulo Drag & Drop, para gestionar el triaje con estados de carga, filtros y consumo tipado del backend mockeado.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 4 — Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX |
| **Sprint** | Sprint 2 (Semanas 2 y 3: 28/09 - 11/10) |
| **Estimación** | 8 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | Frontend Developer |
| **Dependencias** | US-01 (Tipos TypeScript autogenerados) y US-02 (Mockups Figma) |
| **Commit Ejemplo** | `feat(US-09): dashboard principal de triaje react con cliente tipado y kpis` |

## Entregables
- Componentes modulares en `frontend/src/components/` (Dropzone, MetricCards, TriageTable).
- Cliente de API integrado en `frontend/src/api/client.ts` consumiendo `specs/openapi.yaml`.
- Vista principal `frontend/src/pages/DashboardPage.tsx`.

## Criterios de Aceptación
- [ ] Dashboard maquetado con filtros por prioridad (Emergencia, Urgente, Rutina, Auditoría).
- [ ] Zona Drag & Drop con previsualizador inmediato de archivos (.pdf, .jpg, .png).
- [ ] Consumo del cliente API tipado manejando estados de carga (loaders), vacío (empty states) y errores.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-09): maquetación del dashboard clínico react con cliente tipado`
- **Merge Strategy:** Squash and merge
""",
    },

    # ── SPRINT 3 ──
    {
        "id": "US-10",
        "title": "[US-10] Conexión FastAPI con el Motor Real de LangGraph y Gemini",
        "milestone": "Sprint 3: Integración del Núcleo",
        "labels": ["sprint:3", "epic:langgraph", "epic:core-api", "role:backend", "role:ai-data", "priority:must-have"],
        "body": """## Descripción
Como Sistema MediFlow Integrado, quiero que el endpoint `POST /api/v1/triage` procese el archivo entrante a través del grafo real de LangGraph, para emitir un diagnóstico automatizado, score de confianza y prioridad clínica real basada en LLM multimodal.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 2 & ÉPICA 3 — Grafo de Decisión Cognitiva y Core API REST |
| **Sprint** | Sprint 3 (Semana 4: 12/10 - 18/10) |
| **Estimación** | 8 Story Points |
| **Prioridad** | MUST HAVE (Alta - Ruta Crítica) |
| **Roles Responsables** | Backend Developer & AI / LLM Engineer |
| **Dependencias** | US-05, US-06 (Grafo LangGraph) y US-07 (Endpoints FastAPI) |
| **Commit Ejemplo** | `feat(US-10): integracion de langgraph y gemini multimodal en post /triage` |

## Entregables
- Orquestador del servicio de triaje en `backend/app/services/triage_service.py`.
- Integración del grafo compilado (`compiled_graph.ainvoke`) en `POST /api/v1/triage`.
- Manejo asíncrono de timeouts y fallbacks de conectividad con Gemini.

## Criterios de Aceptación
- [ ] Reemplazo total de datos mock por la ejecución del grafo `compiled_graph.ainvoke()`.
- [ ] Respuesta HTTP 200 con payload real cumpliendo estrictamente `specs/openapi.yaml`.
- [ ] Tiempo de inferencia optimizado y control defensivo de timeouts de API externa.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-10): conexión de fastapi con motor langgraph y gemini real`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-11",
        "title": "[US-11] Persistencia Activa Serverless en OCI Object Storage y DB Soporte",
        "milestone": "Sprint 3: Integración del Núcleo",
        "labels": ["sprint:3", "epic:core-api", "epic:cloud-infra", "role:backend", "role:devops", "priority:must-have"],
        "body": """## Descripción
Como Oficial de Cumplimiento y Seguridad, quiero que cada triaje procesado almacene automáticamente el archivo original y el JSON de resultado en OCI Object Storage, e indexe el caso en PostgreSQL, para garantizar respaldo duradero en la nube de Oracle y permitir consultas indexadas inmediatas desde el dashboard.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 3 & ÉPICA 6 — Persistencia Serverless e Infraestructura Cloud |
| **Sprint** | Sprint 3 (Semana 4: 12/10 - 18/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | Backend Developer & DevOps / Cloud Engineer |
| **Dependencias** | US-08 (SDK OCI) y US-10 (Pipeline de agente activo) |
| **Commit Ejemplo** | `feat(US-11): persistencia automatica en oci object storage y postgresql` |

## Entregables
- Módulo de persistencia dual en `backend/app/services/storage_service.py`.
- Estructura de carpetas en bucket OCI organizadas por severidad (`/emergencias/`, `/urgentes/`, `/rutina/`, `/auditoria/`).
- Migraciones y modelos SQLAlchemy/SQLModel para indexación en `backend/app/models/triage.py`.

## Criterios de Aceptación
- [ ] El resultado JSON y el documento se suben a OCI organizados por carpeta de severidad.
- [ ] Registro de metadatos clínicos en tablas PostgreSQL (`triage_cases`, `patients`) según `schema.sql`.
- [ ] Generación de enlaces de acceso seguro (PAR URLs) para visualización desde la UI.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-11): persistencia activa en oci object storage y base de datos relacional`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-12",
        "title": "[US-12] Panel Human-in-the-Loop y Auditoría Médica en Vivo",
        "milestone": "Sprint 3: Integración del Núcleo",
        "labels": ["sprint:3", "epic:ui-ux", "role:frontend", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como Médico Auditor / Supervisor de Triaje, quiero una vista especializada en el frontend para revisar casos ambiguos (`confidence_score < 0.8`), ver el documento original lado a lado con el resultado del agente, y corregir o aprobar la prioridad clínica, para mantener la seguridad del paciente como regla inquebrantable mediante validación humana.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 4 — Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX |
| **Sprint** | Sprint 3 (Semana 4: 12/10 - 18/10) |
| **Estimación** | 8 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | Frontend Developer & Backend Developer |
| **Dependencias** | US-09 (Dashboard UI) y US-10, US-11 (API integrada) |
| **Commit Ejemplo** | `feat(US-12): panel interactivo human-in-the-loop y endpoint de auditoria put` |

## Entregables
- Vista de auditoría en `frontend/src/pages/AuditPage.tsx` con visor de documento split-screen.
- Endpoint de confirmación `PUT /api/v1/triage/{id}/audit` en `backend/app/api/v1/endpoints/triage.py`.
- Formulario de corrección clínica de diagnósticos, signos vitales y prioridad.

## Criterios de Aceptación
- [ ] Vista comparativa: Documento original (PDF/imagen) vs datos clínicos extraídos por la IA y motivo de la baja confianza.
- [ ] Formulario interactivo para ajustar diagnóstico o nivel de prioridad.
- [ ] Botón de "Confirmar Auditoría" que envía `PUT /api/v1/triage/{id}/audit`, actualiza el estado en backend y remueve el caso de la cola de pendientes.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-12): panel human-in-the-loop y flujo de auditoría médica`
- **Merge Strategy:** Squash and merge
""",
    },

    # ── SPRINT 4 ──
    {
        "id": "US-13",
        "title": "[US-13] Orquestación con Reverse Proxy Nginx y Docker Compose de Producción",
        "milestone": "Sprint 4: Orquestación, QA y Cierre",
        "labels": ["sprint:4", "epic:cloud-infra", "role:devops", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como DevOps Engineer y Equipo de Desarrollo, quiero empaquetar Frontend, Backend y Nginx en un Docker Compose unificado para producción, para servir la plataforma en un puerto único (:80) con ruteo transparente (`/` para React y `/api` para FastAPI) sin problemas de CORS ni puertos expuestos dispersos.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 6 — Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales |
| **Sprint** | Sprint 4 (Semana 5: 19/10 - 25/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | DevOps / Cloud Engineer & Backend Developer |
| **Dependencias** | Sistema integrado de Frontend y Backend (Sprint 3) |
| **Commit Ejemplo** | `feat(US-13): reverse proxy nginx en puerto 80 y compose de produccion` |

## Entregables
- Archivo de configuración `infrastructure/nginx/nginx.conf` con directivas proxy_pass y headers seguros.
- `docker-compose.prod.yml` orquestando Frontend empaquetado, Backend y Nginx.
- Target `prod-docker` o `up-prod` en `Makefile`.

## Criterios de Aceptación
- [ ] Configuración de Nginx en `infrastructure/nginx/nginx.conf` ruteando peticiones correctamente.
- [ ] `docker compose up` levanta todos los servicios de forma limpia y orquestada en el puerto `:80`.
- [ ] Eliminación de errores CORS en comunicaciones cliente-servidor bajo el mismo origen.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `feat(US-13): orquestación de producción con reverse proxy nginx`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-14",
        "title": "[US-14] Contract Testing Automatizado (Schemathesis) y Suites Pytest",
        "milestone": "Sprint 4: Orquestación, QA y Cierre",
        "labels": ["sprint:4", "epic:qa", "role:qa", "role:backend", "priority:must-have"],
        "body": """## Descripción
Como QA Engineer y Tech Lead, quiero ejecutar pruebas automáticas de contrato contra `specs/openapi.yaml` y pruebas unitarias/integración de todos los módulos, para certificar que el sistema cumple 100% con la especificación y asegurar que no existan regresiones de código.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 5 — Aseguramiento de Calidad, Contract Testing y Validación Clínica |
| **Sprint** | Sprint 4 (Semana 5: 19/10 - 25/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta) |
| **Roles Responsables** | QA Engineer & Tech Lead (SDD) |
| **Dependencias** | Endpoints de backend completos (US-10, US-11) |
| **Commit Ejemplo** | `test(US-14): suite de contract testing schemathesis y pruebas pytest` |

## Entregables
- Suite de pruebas de contrato en `backend/tests/test_contract.py` con Schemathesis.
- Suites de cobertura unitaria para servicios y nodos en `backend/tests/`.
- Target `make test-contract` y `make test-backend` validados con reporte de cobertura.

## Criterios de Aceptación
- [ ] `make test-contract` ejecuta Schemathesis con 0 discrepancias contractuales.
- [ ] `make test-backend` corre suites con `pytest` y `pytest-asyncio` con cobertura superior al 75%.
- [ ] Pruebas de borde para payloads malformados y límites de tamaño.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `test(US-14): automatización de contract testing con schemathesis y pytest`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-15",
        "title": "[US-15] Pipeline de CI/CD en GitHub Actions",
        "milestone": "Sprint 4: Orquestación, QA y Cierre",
        "labels": ["sprint:4", "epic:cloud-infra", "role:devops", "role:qa", "priority:should-have"],
        "body": """## Descripción
Como Tech Lead y Product Owner, quiero un pipeline que valide automáticamente cada Pull Request antes de fusionarlo a `develop`, para garantizar que ningún commit rompa el linter, los tests ni el contrato de la API.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 6 — Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales |
| **Sprint** | Sprint 4 (Semana 5: 19/10 - 25/10) |
| **Estimación** | 3 Story Points |
| **Prioridad** | SHOULD HAVE (Media) |
| **Roles Responsables** | DevOps / Cloud Engineer & QA Engineer |
| **Dependencias** | US-13 (Docker funcional) y US-14 (Suites de prueba) |
| **Commit Ejemplo** | `ci(US-15): pipeline github actions para linter validacion spectral y tests` |

## Entregables
- Workflow en `.github/workflows/ci.yml`.
- Pasos automatizados: `lint` (Ruff/ESLint), `validate-spec` (Spectral) y `test` (Pytest).
- Insignia de estado de CI en `README.md`.

## Criterios de Aceptación
- [ ] Workflow de GitHub Actions que corre: `ruff`, `make validate` y `pytest`.
- [ ] Bloqueo automático de PRs que no superen los checks obligatorios.
- [ ] Tiempos de ejecución de CI optimizados con cache de dependencias.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `ci(US-15): implementación de pipeline de integración continua con github actions`
- **Merge Strategy:** Squash and merge
""",
    },
    {
        "id": "US-16",
        "title": "[US-16] Smoke Tests E2E, Video Demo en YouTube y Preparación Demo Day",
        "milestone": "Sprint 4: Orquestación, QA y Cierre",
        "labels": ["sprint:4", "epic:qa", "epic:cloud-infra", "role:qa", "role:devops", "priority:must-have"],
        "body": """## Descripción
Como Jurado de Oracle & No Country / Evaluadores del Hackathon, quiero un video demostrativo público en YouTube y una presentación técnica en vivo de 5 minutos mostrando el sistema en funcionamiento, para evaluar la propuesta de valor médica, la viabilidad técnica, la integración cloud en OCI y el impacto clínico para la clasificación final.

## Metadata
| Campo | Valor |
|---|---|
| **Épica** | ÉPICA 5 & ÉPICA 6 — Aseguramiento de Calidad y Entregables Oficiales del Hackathon |
| **Sprint** | Sprint 4 (Semana 5: 19/10 - 25/10) |
| **Estimación** | 5 Story Points |
| **Prioridad** | MUST HAVE (Alta - Entrega Obligatoria) |
| **Roles Responsables** | QA Engineer, Product Owner & DevOps |
| **Dependencias** | US-10 a US-14 (Todo el sistema integrado) |
| **Commit Ejemplo** | `docs(US-16): guia de sustentacion para demo day y enlace de video demo youtube` |

## Entregables
- Guion técnico del Demo Day y diapositivas en `Docs/pitch-demo-day.md`.
- Video Demostrativo subido a YouTube con visibilidad pública/oculta (5 minutos).
- Actualización de `README.md` con enlaces oficiales de entrega antes del 25/10/2026.
- Evidencias de Smoke Test E2E documentadas.

## Criterios de Aceptación (Requisitos Oficiales del Manual)
- [ ] **Smoke Test E2E validado:** Subida de PDF real → Procesamiento LangGraph/Gemini → Guardado en OCI → Renderizado en Dashboard.
- [ ] **Video Demo Obligatorio:** Duración sugerida de **5 minutos** (máximo 10 min), publicado en **YouTube** y enlace cargado en la plataforma No Country antes del 25/10/2026.
- [ ] **Inscripción al Demo Day:** Formulario completado por el representante antes de la fecha límite.
- [ ] **Presentación en Vivo (Demo Day 1 y 2):** Pitch estricto de **5 minutos** realizado por **una sola persona** representante, demostrando el software funcionando en vivo (MVP).
- [ ] **Carga de materiales:** Repositorio GitHub con README y enlaces cargados antes del **25/10/2026**.

## Convenciones
- **Rama de trabajo:** Rama de desarrollo personal del colaborador (`dev-<nombre>`).
- **PR Destino:** `develop`
- **PR Title:** `docs(US-16): entregables oficiales, guía para demo day y video demostrativo`
- **Merge Strategy:** Squash and merge
""",
    },
]


def run_command(cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
    """Ejecuta un comando en el sistema y retorna el resultado."""
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def check_gh_installed() -> bool:
    """Verifica si GitHub CLI está instalado."""
    try:
        res = run_command(["gh", "--version"], check=False)
        return res.returncode == 0
    except FileNotFoundError:
        return False


def check_gh_auth() -> bool:
    """Verifica si el usuario está autenticado en GitHub CLI."""
    res = run_command(["gh", "auth", "status"], check=False)
    return res.returncode == 0


def ensure_labels(repo: str = None, dry_run: bool = False):
    """Crea las etiquetas requeridas en el repositorio si no existen."""
    print("\n🏷️  Verificando / creando Labels...")
    for label in LABELS:
        cmd = [
            "gh", "label", "create", label["name"],
            "--color", label["color"],
            "--description", label["description"],
            "--force",
        ]
        if repo:
            cmd.extend(["--repo", repo])

        if dry_run:
            print(f"  [DRY-RUN] {' '.join(cmd)}")
        else:
            try:
                run_command(cmd, check=False)
                print(f"  ✓ Label lista: {label['name']}")
            except Exception as e:
                print(f"  ⚠️ Error creando label {label['name']}: {e}")


def ensure_milestones(repo: str = None, dry_run: bool = False):
    """Crea los milestones (Sprints) en el repositorio."""
    print("\n🚩 Verificando / creando Milestones (Sprints)...")
    for ms in MILESTONES:
        cmd = [
            "gh", "api",
            f"/repos/{repo}/milestones" if repo else "/repos/:owner/:repo/milestones",
            "-f", f"title={ms['title']}",
            "-f", f"description={ms['description']}",
        ]
        if dry_run:
            print(f"  [DRY-RUN] {' '.join(cmd)}")
        else:
            try:
                res = run_command(cmd, check=False)
                if res.returncode == 0:
                    print(f"  ✓ Milestone creado: {ms['title']}")
                else:
                    print(f"  ℹ️ Milestone verificado: {ms['title']}")
            except Exception as e:
                print(f"  ⚠️ Error en milestone {ms['title']}: {e}")


def create_issues(repo: str = None, dry_run: bool = False):
    """Crea las 16 Historias de Usuario como GitHub Issues."""
    print(f"\n🚀 Procesando las {len(ISSUES)} Historias de Usuario (Issues)...")
    created = 0
    for issue in ISSUES:
        cmd = [
            "gh", "issue", "create",
            "--title", issue["title"],
            "--body", issue["body"],
            "--milestone", issue["milestone"],
        ]
        for label in issue["labels"]:
            cmd.extend(["--label", label])

        if repo:
            cmd.extend(["--repo", repo])

        if dry_run:
            print(f"\n[DRY-RUN] {issue['id']}: {issue['title']}")
            print(f"  Milestone: {issue['milestone']}")
            print(f"  Labels: {', '.join(issue['labels'])}")
            created += 1
        else:
            try:
                res = run_command(cmd)
                issue_url = res.stdout.strip()
                print(f"  ✓ {issue['id']} creada: {issue_url}")
                created += 1
            except subprocess.CalledProcessError as e:
                print(f"  ❌ Error creando {issue['id']}: {e.stderr.strip()}")

    print(f"\n✨ Proceso completado: {created}/{len(ISSUES)} issues procesadas.")


def main():
    parser = argparse.ArgumentParser(description="Automatización de creación de GitHub Issues para MediFlow.")
    parser.add_argument("--dry-run", action="store_true", help="Simula la ejecución sin realizar llamadas reales a la API.")
    parser.add_argument(
        "--repo",
        type=str,
        default="No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA",
        help="Repositorio destino OWNER/REPO.",
    )
    args = parser.parse_args()

    print("════════════════════════════════════════════════════════════════")
    print("   🏥 MediFlow — Automatización de GitHub Issues & Milestones   ")
    print("════════════════════════════════════════════════════════════════")

    if not check_gh_installed():
        print("❌ Error: GitHub CLI ('gh') no está instalado en tu sistema.")
        print("   Instálalo con: sudo apt install gh  (o brew install gh)")
        sys.exit(1)

    if not args.dry_run and not check_gh_auth():
        print("⚠️ Advertencia: No has iniciado sesión en GitHub CLI.")
        print("   Por favor ejecuta: gh auth login")
        sys.exit(1)

    print(f"🎯 Repositorio destino: {args.repo}")
    if args.dry_run:
        print("🔍 Modo: SIMULACIÓN (DRY-RUN) — No se realizarán cambios reales.")

    ensure_labels(repo=args.repo, dry_run=args.dry_run)
    ensure_milestones(repo=args.repo, dry_run=args.dry_run)
    create_issues(repo=args.repo, dry_run=args.dry_run)

    print("\n📋 Tablero Kanban: Puedes vincular estos issues a tu GitHub Project Board.")


if __name__ == "__main__":
    main()
