# 🏥 MediFlow — Product Backlog Unificado (HUs & Tareas Atómicas)

## 1. Información del Proyecto

| Campo | Valor |
|---|---|
| **Proyecto** | MediFlow – Agente Autónomo para Triaje, Extracción y Enrutamiento Clínico |
| **Programa** | Hackathon ONE Grupo 10 (Oracle Next Education & Alura) |
| **Documento Base** | [`proyecto.md`](file:///home/wigsdev/GitHub/mediflow/proyecto.md) |
| **Metodología** | Spec-First / Schema-Driven Development (SDD) · Conventional Commits · GitHub Flow |
| **Tamaño del Equipo** | 8 Integrantes |
| **Stack Principal** | OpenAPI 3.0 · FastAPI · Google Gemini Multimodal · OCI Object Storage Always Free · React 18 (Vite + TS) · n8n |
| **Estrategia Git** | Feature Branches · Squash and Merge · Cierre Automático vía PR (`Closes #XX`) |

---

## 2. Sistema de Gestión del Equipo (8 Integrantes)

### 2.1 Asignación y Dinámica de Trabajo
* **Estructura Jerárquica:** Cada **Historia de Usuario (HU)** define el requisito funcional y clínico de negocio; debajo de cada HU se encuentran sus **Tareas Técnicas Atómicas (`T-01` a `T-18`)** (estimadas entre 1 a 3 horas).
* **Guía Técnica de Apoyo:** Para cada tarea, los desarrolladores pueden consultar [`docs/guia-desarrollo.md`](guia-desarrollo.md) donde encontrarán fragmentos de código (*snippets*), ejemplos de payloads y guías paso a paso.
* **Paralelización Real (SDD):** Al contar con el contrato en [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml), los integrantes asignados a Frontend, IA, Backend y OCI pueden programar en paralelo sin esperarse.
* **Roles Especializados:**
  1. **Team Leader / Arquitectura (1):** Gobernanza, PR reviews, validación de schemas y despliegue (`T-01`, `T-16`).
  2. **AI & Prompt Engineers (2):** Prompts de Gemini multimodal, modelos Pydantic y extracción CIE-10 (`T-05`, `T-06`).
  3. **Workflow & Backend Engineers (2):** Lógica condicional, endpoints FastAPI, webhooks y alertas (`T-07`, `T-09`, `T-10`, `T-11`).
  4. **Cloud & OCI Engineer (1):** Conector OCI SDK con Instance Principal, buckets Always Free y VM Ampere A1 (`T-08`, `T-17`).
  5. **Frontend / UI Engineer (1):** Dashboard clínico, visualizador Split-Screen y panel HITL (`T-12`, `T-13`, `T-14`).
  6. **QA, Datasets & Demo (1):** Datasets clínicos oficiales, suite de pruebas y guión de video (`T-02`, `T-03`, `T-04`, `T-15`, `T-18`).

### 2.2 Estados del Tablero (GitHub Projects v2)
* 🔲 **Backlog:** Tarea disponible sin asignar.
* 👤 **Assigned (`status: assigned`):** Tomada por un integrante con fecha límite.
* 🔨 **In Progress (`status: in-progress`):** En desarrollo en rama `feature/T-XX-...`.
* 🔍 **In Review (`status: in-review`):** Pull Request abierto en GitHub (movimiento automático).
* ✅ **Done:** PR aprobado y mergeado a `main` (cierre automático vía `Closes #XX`).

### 2.3 Prioridades
* `priority: critical` 🔴 Bloqueante para otros integrantes.
* `priority: high` 🟠 Core – Requisito obligatorio evaluable del pliego.
* `priority: medium` 🟡 Importante – Componentes de integración y soporte.
* `priority: low` 🟢 Diferenciales y mejoras opcionales.

---

## 3. Catálogo Unificado de HUs y Tareas Técnicas

```
HU-01: Ingesta Multicanal y Contratos de Entrada
  ├── T-01: Scaffolding Base del Proyecto y Variables de Entorno [✅ Done]
  ├── T-02: Dataset Caso 1: Flujo Estándar de Receta Médica
  ├── T-03: Dataset Caso 2: Urgencia Médica de Tromboembolismo Pulmonar (TEP)
  └── T-04: Dataset Caso 3: Caso Ambiguo con Derivación a HITL

HU-02: Extracción Clínica Estructurada y Codificación CIE-10
  ├── T-05: Modelos Pydantic para Validación Clínica en Python
  └── T-06: Prompt de Sistema y Agente Extractor Multimodal con Google Gemini

HU-03: Detección y Notificación de Urgencias Médicas
  ├── T-07: Motor de Lógica de Decisión Condicional y Reglas de Enrutamiento
  └── T-11: Integración de Notificaciones de Alerta en n8n (Slack / Webhook)

HU-04: Enrutamiento Departamental Automatizado
  ├── T-09: Configuración de Docker Compose para n8n Local
  └── T-10: Workflow de n8n: Webhook, Nodos de IA y Bifurcación Condicional

HU-05: Derivación y Auditoría Human-in-the-Loop (HITL)
  ├── T-14: UI: Panel Human-in-the-Loop (Auditoría Médica y Aprobación 1-clic)
  └── T-15: Suite de Pruebas Automatizadas de Extracción y Enrutamiento

HU-06: Persistencia y Segregación en OCI Object Storage (Always Free)
  ├── T-08: Conector de Persistencia en OCI Object Storage con Instance Principal
  └── T-17: Guía y Script para Despliegue en OCI Compute VM Ampere A1

HU-07: Dashboard de Visualización y Triaje en Vivo
  ├── T-12: UI: Selector de Casos Demo y Subida de Archivos
  ├── T-13: UI: Visor Split-Screen y Panel de Resultados de Triaje
  ├── T-16: Documentación Final: README.md del Proyecto y Diagrama de Arquitectura
  └── T-18: Preparación del Guión y Grabación del Video de Demostración
```

---

### HU-01: Ingesta Multicanal de Documentos Clínicos
> **Como:** Personal administrativo de admisión hospitalaria o sistema externo emisor.  
> **Quiero:** Enviar documentos clínicos en texto crudo, PDF escaneado o imagen de alta resolución a través de la API/Webhook.  
> **Para:** Centralizar el procesamiento documental sin transcripciones manuales previas.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un payload con `documento_id`, `tipo_archivo` y contenido válido, *cuando* se envía a `POST /api/v1/triaje`, *entonces* se acepta y valida contra [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml).  
> * *Dado* un payload sin `documento_id`, *cuando* se valida, *entonces* retorna error `400 Bad Request`.

#### T-01 — Scaffolding Base del Proyecto y Variables de Entorno
* **Prioridad:** `priority: critical` | **Tipo:** `type: structure` | **Rol:** Team Leader / DevOps | **Complejidad:** Baja (1h) | **Estado:** ✅ Done
* **Entregables:** `.gitignore`, `.env.example`, `docker-compose.yml`, `requirements.txt`.
* **Criterios:**
  - [x] Variables de entorno documentadas para Gemini y OCI.
  - [x] `.gitignore` previene subida de secretos y `.env`.

#### T-02 — Dataset Caso 1: Flujo Estándar de Receta Médica
* **Prioridad:** `priority: high` | **Tipo:** `type: dataset` | **Rol:** QA & Datasets | **Complejidad:** Baja (1-2h) | **Dependencia:** T-01
* **Entregables:** `datasets/caso_1_estandar_receta.json` conforme a la spec.
* **Criterios:**
  - [ ] Simula receta de tratamiento crónico (hipertensión/diabetes).
  - [ ] Prioridad resultante esperada: `Rutina`.
  - [ ] Destino esperado: `Farmacia_Hospitalaria` con `requiere_auditoria_humana = false`.

#### T-03 — Dataset Caso 2: Urgencia Médica de Tromboembolismo Pulmonar (TEP)
* **Prioridad:** `priority: critical` | **Tipo:** `type: dataset` | **Rol:** QA & Datasets | **Complejidad:** Baja (1-2h) | **Dependencia:** T-01
* **Entregables:** `datasets/caso_2_urgencia_tep.json` basado en el texto del pliego oficial (`Carlos Mendes, 52 años`).
* **Criterios:**
  - [ ] Diagnóstico: Tromboembolismo Pulmonar Agudo (CIE-10: `I26.9`).
  - [ ] Prioridad: `Urgente`. Destino: `Cola_Emergencia_Medica`.
  - [ ] Contiene objeto `notificacion_generada` con mensaje de alerta crítica.

#### T-04 — Dataset Caso 3: Caso Ambiguo con Derivación a Human-in-the-Loop (HITL)
* **Prioridad:** `priority: high` | **Tipo:** `type: dataset` | **Rol:** QA & Datasets | **Complejidad:** Baja (1-2h) | **Dependencia:** T-01
* **Entregables:** `datasets/caso_3_ambiguo_hitl.json`.
* **Criterios:**
  - [ ] Documento con baja resolución o datos incompletos (`score_confianza < 0.85`).
  - [ ] Destino: `Cola_Auditoria_Humana` con `requiere_auditoria_humana = true`.
  - [ ] Campo `motivo_ambiguedad` documentado.

---

### HU-02: Extracción Clínica Estructurada y Codificación CIE-10
> **Como:** Auditor médico hospitalario.  
> **Quiero:** Que el agente multimodal Gemini extraiga estructuradamente datos del paciente, médico tratante, diagnóstico, medicamentos y proponga el código CIE-10.  
> **Para:** Estandarizar la información médica en formato digital e interoperable sin errores manuales.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un informe médico legible, *cuando* el agente analiza el texto/imagen, *entonces* retorna el esquema de entidades clínicas tipado y validado.

#### T-05 — Modelos Pydantic para Validación Clínica en Python
* **Prioridad:** `priority: high` | **Tipo:** `type: schema` | **Rol:** AI Engineer / Backend | **Complejidad:** Media (2h) | **Dependencia:** T-01
* **Entregables:** `backend-api/app/models/schemas.py`.
* **Criterios:**
  - [ ] Modelos Pydantic v2 para `DocumentoClinicoInput`, `DatosClinicosExtraidos`, `RespuestaTriaje`.
  - [ ] Tipado estricto con validaciones y enums clínicos.

#### T-06 — Prompt de Sistema y Agente Extractor Multimodal con Google Gemini
* **Prioridad:** `priority: critical` | **Tipo:** `type: ia-agent` | **Rol:** AI Engineer | **Complejidad:** Media (2-3h) | **Dependencia:** T-05
* **Entregables:** `backend-api/app/agent/gemini_client.py` y `prompts.py`.
* **Criterios:**
  - [ ] Prompt con rol de auditor clínico y tabla de correspondencia CIE-10.
  - [ ] Soporte para llamadas con texto y archivos base64 usando el SDK `google-generativeai`.

---

### HU-03: Detección y Notificación de Urgencias Médicas
> **Como:** Médico de guardia de emergencias.  
> **Quiero:** Que el sistema identifique de inmediato hallazgos clínicos críticos (ej. TEP, infarto, hemorragia).  
> **Para:** Intervenir precozmente al paciente y activar alertas en los canales de guardia médica.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento con hallazgo de riesgo vital, *cuando* el evaluador condicional lo procesa, *entonces* marca prioridad `Urgente`, deriva a `Cola_Emergencia_Medica` y despacha alerta inmediata.

#### T-07 — Motor de Lógica de Decisión Condicional y Reglas de Enrutamiento
* **Prioridad:** `priority: critical` | **Tipo:** `type: workflow` | **Rol:** Backend Engineer | **Complejidad:** Media (2h) | **Dependencia:** T-05
* **Entregables:** `backend-api/app/agent/graph.py`.
* **Criterios:**
  - [ ] Evalúa score de confianza (< 0.85 desvía a HITL).
  - [ ] Evalúa palabras clave críticas (desvía a Emergencias con alerta).
  - [ ] Enruta recetas a Farmacia y estudios a Historia Clínica.

#### T-11 — Integración de Notificaciones de Alerta en n8n (Slack / Webhook)
* **Prioridad:** `priority: medium` | **Tipo:** `type: workflow` | **Rol:** Workflow Engineer | **Complejidad:** Baja (1-2h) | **Dependencia:** T-07
* **Entregables:** Nodo de Slack/Webhook en el workflow de n8n.
* **Criterios:**
  - [ ] Envía mensaje formateado a canal de guardia solo ante casos de prioridad `Urgente`.

---

### HU-04: Enrutamiento Departamental Automatizado
> **Como:** Gestor hospitalario.  
> **Quiero:** Que los documentos de rutina sin anomalías sean derivados automáticamente a su sistema de destino correspondiente.  
> **Para:** Agilizar la entrega de recetas en farmacia y el archivo en historias clínicas sin demoras.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento de rutina con score $\ge 0.85$, *cuando* se ejecuta el enrutamiento, *entonces* se asigna a Farmacia o HCE sin requerir intervención humana.

#### T-09 — Configuración de Docker Compose para n8n Local
* **Prioridad:** `priority: medium` | **Tipo:** `type: workflow` | **Rol:** DevOps / Workflow | **Complejidad:** Baja (1h) | **Dependencia:** T-01
* **Entregables:** `docker-compose.yml` con servicio `n8n` en puerto 5678.
* **Criterios:**
  - [ ] `docker compose up -d` levanta n8n con volumen de datos persistente.

#### T-10 — Workflow de n8n: Webhook, Nodos de IA y Bifurcación Condicional
* **Prioridad:** `priority: critical` | **Tipo:** `type: workflow` | **Rol:** Workflow Engineer | **Complejidad:** Alta (3h) | **Dependencia:** T-06, T-07, T-09
* **Entregables:** `workflows/mediflow_triaje_workflow.json`.
* **Criterios:**
  - [ ] Webhook de entrada que se conecta con la API o ejecuta el flujo.
  - [ ] Archivo JSON exportado importable limpiamente en cualquier n8n.

---

### HU-05: Derivación y Auditoría Human-in-the-Loop (HITL)
> **Como:** Auditor clínico de control de calidad.  
> **Quiero:** Que cualquier documento con baja legibilidad o confianza < 0.85 sea aislado en una cola de revisión para validación manual.  
> **Para:** Prevenir errores médicos antes de que la información impacte al paciente.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento borroso con confianza < 0.85, *cuando* se procesa, *entonces* su estado es `pendiente_auditoria`, destino `Cola_Auditoria_Humana` y se almacena en `/auditoria_humana/`.

#### T-14 — UI: Panel Human-in-the-Loop (Auditoría Médica y Aprobación 1-clic)
* **Prioridad:** `priority: high` | **Tipo:** `type: frontend` | **Rol:** Frontend Engineer | **Complejidad:** Media (2h) | **Dependencia:** T-07, T-13
* **Entregables:** Módulo de auditoría médica en `frontend/`.
* **Criterios:**
  - [ ] Se activa ante documentos con `requiere_auditoria_humana = true`.
  - [ ] Formulario editable para corregir paciente, diagnóstico o CIE-10.
  - [ ] Botón de aprobación que actualiza el estado a `procesado` en OCI.

#### T-15 — Suite de Pruebas Automatizadas de Extracción y Enrutamiento
* **Prioridad:** `priority: high` | **Tipo:** `type: dataset` | **Rol:** QA & Datasets | **Complejidad:** Media (2h) | **Dependencia:** T-02, T-03, T-04, T-07
* **Entregables:** `backend-api/tests/test_contract.py`.
* **Criterios:**
  - [ ] Pasan las 3 pruebas unitarias de los 3 escenarios obligatorios (3/3).

---

### HU-06: Persistencia y Segregación en OCI Object Storage (Always Free)
> **Como:** Administrador de infraestructura y cumplimiento regulatorio.  
> **Quiero:** Que los documentos y sus metadatos procesados se almacenen en carpetas segregadas de OCI Object Storage Always Free.  
> **Para:** Mantener una pista de auditoría organizada y respaldada en la nube de Oracle.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento procesado, *cuando* se persiste, *entonces* se almacena en el bucket bajo `/recibidos`, `/procesados/urgentes`, `/procesados/farmacia` o `/auditoria_humana`.

#### T-08 — Conector de Persistencia en OCI Object Storage con Instance Principal
* **Prioridad:** `priority: high` | **Tipo:** `type: cloud-oci` | **Rol:** Cloud & OCI Engineer | **Complejidad:** Media (2-3h) | **Dependencia:** T-01
* **Entregables:** `backend-api/app/services/oci.py`.
* **Criterios:**
  - [ ] Soporte para autenticación **IAM Instance Principal** (sin claves en disco).
  - [ ] Segregación automática por carpetas según decisión del triaje.
  - [ ] Modo simulación local (*Mock*) para pruebas sin credenciales.

#### T-17 — Guía y Script para Despliegue en OCI Compute VM Ampere A1
* **Prioridad:** `priority: low` | **Tipo:** `type: cloud-oci` | **Rol:** Cloud & OCI Engineer | **Complejidad:** Media (2h) | **Dependencia:** T-08, T-10
* **Entregables:** `docs/oci_deployment_guide.md` y script de provisionamiento.
* **Criterios:**
  - [ ] Pasos para crear la VM Ampere A1 (4 OCPU / 24 GB RAM Always Free).
  - [ ] Configuración de VCN, Subnet pública y apertura de puertos 8000, 8501, 5678.

---

### HU-07: Dashboard de Visualización y Triaje en Vivo
> **Como:** Personal de salud / Auditor clínico.  
> **Quiero:** Una interfaz web interactiva con vista Split-Screen para cargar documentos, ver diagnósticos en tiempo real y métricas hospitalarias.  
> **Para:** Operar el triaje con máxima ergonomía y reducción de carga cognitiva.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento procesado, *cuando* se consulta en pantalla, *entonces* se muestra el documento original al lado de los datos extraídos con badges semánticos de prioridad.

#### T-12 — UI: Selector de Casos Demo y Subida de Archivos
* **Prioridad:** `priority: high` | **Tipo:** `type: frontend` | **Rol:** Frontend Engineer | **Complejidad:** Media (2h) | **Dependencia:** T-01, T-02, T-03, T-04
* **Entregables:** Pantalla de carga y selector de los 3 casos demo en `frontend/src/` (React + Vite).
* **Criterios:**
  - [ ] Permite alternar entre Caso 1, Caso 2 y Caso 3 con un solo clic.
  - [ ] Permite cargar archivos PDF o imágenes vía drag & drop.

#### T-13 — UI: Visor Split-Screen y Panel de Resultados de Triaje
* **Prioridad:** `priority: high` | **Tipo:** `type: frontend` | **Rol:** Frontend Engineer | **Complejidad:** Media (2h) | **Dependencia:** T-07, T-12
* **Entregables:** Layout Split-Screen según diseño en `docs/design_system.md`.
* **Criterios:**
  - [ ] Documento original a la izquierda (45%) y extracción clínica a la derecha (55%).
  - [ ] Badges cromáticos de prioridad (Rojo Urgente, Ámbar Prioritario, Verde Rutina).
  - [ ] Alerta crítica pulsante ante casos de urgencia TEP.

#### T-16 — Documentación Final: README.md del Proyecto y Diagrama de Arquitectura
* **Prioridad:** `priority: critical` | **Tipo:** `type: docs` | **Rol:** Team Leader / QA | **Complejidad:** Media (2h) | **Dependencia:** T-08, T-10, T-14
* **Entregables:** `README.md` principal del repositorio.
* **Criterios:**
  - [ ] Arquitectura visual, diagrama del grafo del agente e instrucciones de ejecución.
  - [ ] Documenta los 3 casos de demostración obligatorios de la hackathon.

#### T-18 — Preparación del Guión y Grabación del Video de Demostración
* **Prioridad:** `priority: high` | **Tipo:** `type: docs` | **Rol:** Team Leader & Equipo | **Complejidad:** Media (2-3h) | **Dependencia:** T-13, T-14, T-16
* **Entregables:** `docs/pitch_demo_script.md`.
* **Criterios:**
  - [ ] Guión estructurado cubriendo los 3 casos clínicos en menos de 5 minutos.
  - [ ] Demostración visual de los archivos guardados en OCI Object Storage.
