# 🏥 MediFlow — Agente Autónomo de Triaje Clínico

> **Hackathon ONE G10 · Oracle Next Education & Alura**

Agente autónomo que recibe documentos clínicos (PDF, imagen, texto), los clasifica con **LLMs multimodales (Google Gemini)**, extrae entidades estructuradas y los enruta automáticamente a la cola correcta, persistiendo todo en **OCI Object Storage** (Always Free).

---

## 🎯 El Problema
En los centros de salud, la clasificación inicial de pacientes (triaje) suele ser un cuello de botella manual, propenso a demoras y sesgos. Los documentos clínicos (estudios, derivaciones, notas) llegan en múltiples formatos (texto, imágenes, PDF), lo que dificulta una evaluación rápida para priorizar emergencias frente a casos de rutina.

## 💡 Nuestra Solución
Desarrollamos **MediFlow**, un agente autónomo impulsado por Inteligencia Artificial multimodal (Google Gemini) y flujos de decisión (LangGraph). El sistema automatiza este proceso para reducir tiempos de espera, priorizando la urgencia sin descartar la intervención médica humana (Human-in-the-Loop) en casos ambiguos.

### 🛠️ ¿Cómo estamos desarrollando esta solución?
Para garantizar un desarrollo ágil, escalable y profesional durante el hackathon, basamos nuestra construcción en tres pilares técnicos:

1. **Spec-Driven Development (SDD):** Nuestro desarrollo es "API-first". Definimos un contrato estricto en `openapi.yaml`. A partir de allí, generamos automáticamente los modelos de datos (Pydantic para Python) y el cliente frontend (TypeScript), garantizando integración sin fricciones.
2. **Flujo de Decisión Cognitiva (LangGraph):** El agente no es un simple llamado al LLM. Hemos diseñado un grafo de estados donde el documento pasa por varios nodos funcionales: *Ingestión → Extracción de Entidades → Clasificación Clínica → Evaluación de Confianza*. Dependiendo del *score*, el agente enruta dinámicamente la información.
3. **Persistencia "Serverless" y Contenedores:** Cumpliendo el reto, no dependemos de bases de datos locales tradicionales. Almacenamos el resultado de los triajes directamente en la nube usando **OCI Object Storage**, y orquestamos toda la aplicación localmente mediante Docker Compose para asegurar reproducibilidad entre los equipos.

### 📋 Plan de Acción Detallado (Ruta Crítica y Dependencias)
Para un equipo de 8 personas, es vital gestionar las dependencias para evitar cuellos de botella. El desarrollo se divide en *Squads* de 2 personas, siguiendo esta secuencia estricta:

#### 🟢 Sprint 1: Fundamentos y Contratos (Bloqueante para todos)
- [ ] **[Squad Backend & SDD]** Definir el contrato `openapi.yaml` (Endpoints, Schemas de Entidades Médicas, Respuestas).
  * 🛑 *Depende de:* Ninguna. Es el punto de partida.
- [ ] **[Squad Backend & SDD]** Ejecutar script generador para compilar modelos Pydantic (Backend) y tipos TypeScript (Frontend).
  * 🛑 *Depende de:* Aprobación del `openapi.yaml`.
- [ ] **[Squad UX/UI]** Crear Mockups en Figma (Uploader, Dashboard de Triaje, Panel de Auditoría).
  * 🛑 *Depende de:* Requerimientos del negocio.

#### 🟡 Sprint 2: Desarrollo en Paralelo (Desacoplado gracias al SDD)
**Backend & IA:**
- [ ] **[Squad IA]** Diseñar Prompts sistémicos y construir Nodos de LangGraph (Ingestión OCR, Extracción, Clasificación, Score de Confianza).
  * 🛑 *Depende de:* Modelos Pydantic autogenerados para estructurar el output del LLM.
- [ ] **[Squad Backend]** Levantar la base de FastAPI e implementar los endpoints (`/triage`, `/documents`) devolviendo datos *mockeados*.
  * 🛑 *Depende de:* Modelos Pydantic autogenerados.
- [ ] **[Squad Cloud]** Configurar credenciales y crear funciones SDK para subir/descargar JSON y PDFs desde OCI Object Storage.
  * 🛑 *Depende de:* Ninguna.

**Frontend:**
- [ ] **[Squad Frontend]** Maquetar la interfaz base en React + Vite (Estructura, ruteo, componentes vacíos).
  * 🛑 *Depende de:* Mockups de Figma.
- [ ] **[Squad Frontend]** Integrar el cliente TypeScript autogenerado para armar las llamadas a la API (usando los mocks del backend).
  * 🛑 *Depende de:* Tipos TypeScript autogenerados en el Sprint 1.

#### 🟠 Sprint 3: Integración del Núcleo (Ruta Crítica)
- [ ] **[Squad Backend + IA]** Conectar los endpoints de FastAPI con el motor real de LangGraph y Gemini (reemplazar *mocks*).
  * 🛑 *Depende de:* Nodos de LangGraph listos y Endpoints FastAPI creados.
- [ ] **[Squad Backend + Cloud]** Conectar el resultado final del Agente (JSON) para que se persista en OCI Object Storage antes de retornar el HTTP 200.
  * 🛑 *Depende de:* SDK de OCI y Agente IA funcionando.
- [ ] **[Squad Frontend]** Conectar los componentes UI con la API real y gestionar estados de carga, errores y renderizado del resultado del triaje.
  * 🛑 *Depende de:* API de FastAPI emitiendo respuestas reales o mockeadas consistentes.
- [ ] **[Squad Frontend]** Desarrollar lógica del "Panel de Auditoría" (Aprobar/Corregir Json de triaje ambiguo).
  * 🛑 *Depende de:* Renderizado del triaje y esquemas de datos claros.

#### 🔴 Sprint 4: Orquestación, Pruebas y Entrega
- [ ] **[Squad QA & Cloud]** Orquestar Backend, Frontend y Nginx en un `docker-compose.yml` unificado.
  * 🛑 *Depende de:* Ambos proyectos (Front/Back) con sus respectivos `Dockerfile` funcionales.
- [ ] **[Equipo Completo]** Smoke Tests (Pruebas E2E): Subir un PDF médico real en el Uploader (Front) → Procesar en LangGraph (Back) → Guardar en OCI → Ver resultado (Front).
  * 🛑 *Depende de:* Todas las fases anteriores.
- [ ] **[Squad QA]** Grabar Demo en video y redactar presentación técnica final.
  * 🛑 *Depende de:* Smoke tests exitosos.

## ⭐ Propuesta de Valor
* **Eficiencia:** Reducción drástica del tiempo de triaje inicial.
* **Precisión Multimodal:** Capacidad de entender texto manuscrito en imágenes, PDFs estructurados y texto plano usando Gemini.
* **Seguridad (Human-in-the-Loop):** Los casos ambiguos o de baja confianza (<50%) no se descartan, sino que se envían a una cola de auditoría para revisión médica humana.
* **Escalabilidad:** Arquitectura basada en microservicios (FastAPI + React) persistiendo en la nube (OCI Object Storage).

## 🎥 Demo
> [!NOTE]
> [🔗 **Ver Video Demo del Proyecto aquí**](#) *(Reemplaza este texto con el enlace a tu video en Loom/YouTube)*
> 
> [🔗 **Ver Proyecto Desplegado**](#) *(Reemplaza este texto con la URL de tu app desplegada, si aplica)*

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

### 3. Acceder
- **Frontend**: http://localhost:5173
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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
| **Agente IA** | LangGraph + Google Gemini |
| **Backend** | Python 3.11 + FastAPI + Pydantic |
| **Frontend** | React 18 + Vite + TypeScript |
| **Almacenamiento** | OCI Object Storage (Always Free) |
| **Infraestructura** | OCI (Oracle Cloud Infrastructure) Docker Compose + Nginx |
| **SDD** | OpenAPI 3.1 → datamodel-codegen + @hey-api/openapi-ts |
---

## 📄 Licencia

MIT — Ver [LICENSE](LICENSE)