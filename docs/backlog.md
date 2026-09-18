# 🏥 MediFlow — Product Backlog

## Información del proyecto

| Campo | Valor |
|-------|-------|
| **Proyecto** | MediFlow — Agente Autónomo para Triaje, Extracción y Enrutamiento Clínico |
| **Programa** | Hackathon ONE Grupo 10 (Oracle Next Education & Alura) |
| **Repositorio** | `No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA` |
| **Team Leader** | Wilmer (@wigsdev) |
| **Equipo** | 8 Integrantes |
| **Metodología** | Spec-First / Schema-Driven Development (SDD) |
| **Stack** | OpenAPI 3.0 · FastAPI · Pydantic v2 · Google Gemini 1.5 · OCI Object Storage Always Free · React 18 (Vite + TS) · n8n |
| **Convenciones** | Conventional Commits · GitHub Flow · Squash Merge |

---

## Sistema de gestión

### Asignación de tareas

- El Team Leader asigna tareas vía GitHub Issues (`assignee` + `due date`).
- La fecha límite se define al momento de asignar según la complejidad estimada (entre 2 y 4 horas).
- Si no se cumple el deadline, el Team Leader puede reasignar o asistir la tarea.
- Las tareas son unidades de trabajo consolidadas y coherentes, con dependencias claramente documentadas.
- Gracias a la metodología **Spec-First**, los módulos de Frontend, Backend, IA, OCI y QA pueden desarrollarse en paralelo respetando los contratos en [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml).

### Estados

| Estado | Label en GitHub | Significado |
|--------|----------------|-------------|
| 🔲 Backlog | — | Sin asignar, disponible en el tablero |
| 👤 Assigned | `status: assigned` | Asignada a un integrante con fecha límite |
| 🔨 In Progress | `status: in-progress` | Desarrollador trabajando en rama `feature/T-XX-...` |
| 🔍 In Review | `status: in-review` | Pull Request abierto en GitHub esperando code review |
| ✅ Done | — (issue cerrado) | PR aprobado y mergeado a `develop` / `main` |

### Prioridades

| Label | Color | Significado |
|-------|-------|-------------|
| `priority: critical` | 🔴 #B60205 | Bloqueante — sin esto otros integrantes no avanzan |
| `priority: high` | 🟠 #D93F0B | Core — funcionalidad esencial evaluable del pliego |
| `priority: medium` | 🟡 #FBCA04 | Importante — componentes de integración y soporte |
| `priority: low` | 🟢 #0E8A16 | Diferenciales y mejoras complementarias |

### Categorías / Tipos

| Label | Significado |
|-------|-------------|
| `type: structure` | Estructura base, configuración y tooling |
| `type: schema` | Contratos de datos OpenAPI 3.0 y modelos Pydantic v2 |
| `type: dataset` | Casos de prueba clínicos oficiales (JSON / PDF) |
| `type: ia-agent` | Integración con Google Gemini, prompts y extracción CIE-10 |
| `type: workflow` | Grafos de decisión condicional, reglas de negocio y n8n |
| `type: cloud-oci` | Integración con OCI Object Storage Always Free y VM Ampere A1 |
| `type: frontend` | Dashboard clínico en React (Vite + TS), Split-Screen y panel HITL |
| `type: docs` | Documentación técnica, diagramas de arquitectura y video demo |

### Definition of Done (DoD)

Referencia completa en [`docs/workflow.md`](./workflow.md#6-definition-of-done-dod).

Una tarea está **Done** cuando:
1. Todos los criterios de aceptación están cumplidos y verificados.
2. Respeta estrictamente los esquemas y contratos definidos en [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml).
3. Las pruebas unitarias y de integración pasan al 100% (`pytest backend-api/tests/ -v`).
4. No contiene claves privadas, contraseñas ni secretos en el código (usa variables en `.env`).
5. Pull Request creado con la plantilla del proyecto hacia `develop` incluyendo `Closes #XX`.
6. Commits siguen el estándar Conventional Commits (ej. `feat(T-04): prompt de extraccion multimodal`).
7. Code Review aprobado por el Team Leader.
8. Merge (squash) a la rama base, rama de trabajo eliminada e Issue cerrado automáticamente.

---

## Catálogo de Historias de Usuario y Tareas

```
HU-01: Ingesta Multicanal y Contratos de Entrada
  ├── T-01: Scaffolding Base del Proyecto, Contratos OpenAPI y Variables de Entorno [✅ Done]
  └── T-02: Datasets Clínicos de Prueba para los 3 Escenarios Obligatorios

HU-02: Extracción Clínica Estructurada y Codificación CIE-10
  ├── T-03: Modelos Pydantic v2 para Validación Clínica y Contratos Python [✅ Done]
  └── T-04: Prompt de Sistema y Extracción Multimodal con Google Gemini

HU-03: Detección y Notificación de Urgencias Médicas
  └── T-05: Grafo de Decisión Condicional y Reglas de Enrutamiento

HU-04: Enrutamiento Departamental y Automatización de Alertas
  └── T-06: Automatización y Alertas Hospitalarias en n8n

HU-05: Derivación y Auditoría Human-in-the-Loop (HITL)
  ├── T-07: Frontend: Panel Human-in-the-Loop para Auditoría Médica y Aprobación 1-clic
  └── T-08: Suite de Pruebas Automatizadas y Validación de Contratos

HU-06: Persistencia y Segregación en OCI Object Storage Always Free
  ├── T-09: Conector de Persistencia en OCI Object Storage con Instance Principal y Mock Local
  └── T-10: Guía y Script para Despliegue en OCI Compute VM Ampere A1

HU-07: Dashboard de Visualización y Triaje en Vivo
  ├── T-11: Frontend: Dashboard Clínico en React (Vite + TS), Selector de Casos Demo y Visor Split-Screen
  ├── T-12: Documentación Final: README.md del Proyecto y Diagramas de Arquitectura
  └── T-13: Preparación del Guión, Pitch y Video Demo
```

---

## Backlog de Tareas

---

### HU-01: Ingesta Multicanal y Contratos de Entrada
> **Como:** Personal administrativo de admisión hospitalaria o sistema clínico emisor.  
> **Quiero:** Enviar documentos médicos en texto crudo, PDF o imagen mediante la API/Webhook.  
> **Para:** Centralizar el procesamiento documental sin transcripciones manuales previas.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un payload con `documento_id`, `tipo_archivo` y contenido válido, *cuando* se envía a `POST /api/v1/triaje`, *entonces* se acepta y valida contra [`specs/openapi.yaml`](file:///home/wigsdev/GitHub/mediflow/specs/openapi.yaml).  
> * *Dado* un payload sin `documento_id`, *cuando* se valida, *entonces* retorna error `400 Bad Request`.

---

### T-01 — Scaffolding Base del Proyecto, Contratos OpenAPI y Variables de Entorno

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: critical` |
| **Tipo** | `type: structure` |
| **Dependencias** | Ninguna |
| **Complejidad** | Media (2 horas) |
| **Rol** | Team Leader / DevOps |
| **Estado** | ✅ Done |
| **Branch** | `feature/T-00-arquitectura-base` |
| **Commit ejemplo** | `chore(T-01): inicializar arquitectura base y contratos openapi` |

**Descripción:**  
Configurar el esqueleto arquitectónico del repositorio, el contrato canónico OpenAPI 3.0.3, las plantillas de variables de entorno, la exclusión de secretos y la orquestación inicial de Docker.

**Entregables:**
- `[CREAR]` `.gitignore` — Exclusiones para Python, Node, temporales, `.env`, `data_mock_oci/` y `.sf/`.
- `[CREAR]` `.env.example` — Plantilla con variables de entorno para Gemini (`GEMINI_API_KEY`, `GEMINI_MODEL`) y OCI (`OCI_MOCK_MODE`, `OCI_BUCKET_NAME`, etc.).
- `[CREAR]` `docker-compose.yml` — Orquestación de servicios locales (`backend-api` en puerto 8000).
- `[CREAR]` `specs/openapi.yaml` — Contrato formal OpenAPI 3.0.3 con 4 endpoints (`/health`, `/api/v1/triaje`, `/api/v1/auditoria/{documento_id}`, `/api/v1/metricas`).
- `[CREAR]` `.github/workflows/ci.yml` — Pipeline de validación de OpenAPI con Redocly y matriz de Python 3.11–3.13.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#1-configuración-del-entorno-de-desarrollo-local) para variables de entorno y comandos Docker.

**Criterios de aceptación:**
- [x] Contrato OpenAPI 3.0.3 validado sin errores con `npx @redocly/cli lint specs/openapi.yaml`.
- [x] `.gitignore` previene subida de secretos, credenciales de OCI o archivos `.env`.
- [x] `.env.example` documenta todas las claves y puertos requeridos con explicaciones claras.
- [x] Estructura base de carpetas inicializada para frontend, backend-api, datasets, docs y specs.

---

### T-02 — Datasets Clínicos de Prueba para los 3 Escenarios Obligatorios

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: critical` |
| **Tipo** | `type: dataset` |
| **Dependencias** | T-01 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | QA & Datasets Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-02-datasets-clinicos` |
| **Commit ejemplo** | `test(T-02): agregar datasets para los 3 casos clinicos obligatorios` |

**Descripción:**  
Crear los 3 archivos JSON de datasets clínicos requeridos por el pliego del proyecto para simular y validar los tres flujos del sistema: (1) Receta médica de rutina ambulatoria, (2) Urgencia médica de Tromboembolismo Pulmonar Agudo (TEP), y (3) Caso ambiguo con baja legibilidad que requiere derivación a Human-in-the-Loop (HITL).

**Entregables:**
- `[CREAR]` `datasets/caso_1_estandar_receta.json` — Payload JSON de receta médica ambulatoria (tratamiento crónico: Enalapril / Metformina) sin hallazgos de alarma.
- `[CREAR]` `datasets/caso_2_urgencia_tep.json` — Payload JSON basado en el caso oficial del pliego (`Carlos Mendes, 52 años`, AngioTC de tórax con diagnóstico de Tromboembolismo Pulmonar Agudo CIE-10 `I26.9`).
- `[CREAR]` `datasets/caso_3_ambiguo_hitl.json` — Payload JSON con texto médico fragmentado o imagen ilegible que fuerce un score de confianza `< 0.85`.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-02-datasets-clínicos-de-prueba-datasets) para la estructura canónica de entrada.

**Criterios de aceptación:**
- [ ] Los 3 JSON cumplen estrictamente el esquema `DocumentoClinicoInput` de `specs/openapi.yaml` (`documento_id`, `tipo_archivo`, `documento_texto`, `canal_origen`).
- [ ] El Caso 1 produce una prioridad resultante de `Rutina`, destino `Farmacia_Hospitalaria` y `requiere_auditoria_humana = false`.
- [ ] El Caso 2 produce una prioridad resultante de `Urgente`, código CIE-10 `I26.9`, destino `Cola_Emergencia_Medica` y payload de `notificacion_generada`.
- [ ] El Caso 3 produce `requiere_auditoria_humana = true`, destino `Cola_Auditoria_Humana` y `score_confianza < 0.85`.
- [ ] Los 3 archivos se pueden consumir directamente vía `curl` o script contra `POST /api/v1/triaje`.

---

### HU-02: Extracción Clínica Estructurada y Codificación CIE-10
> **Como:** Auditor médico hospitalario.  
> **Quiero:** Que el agente multimodal Gemini extraiga estructuradamente datos del paciente, médico tratante, diagnóstico, medicamentos y proponga el código CIE-10.  
> **Para:** Estandarizar la información médica en formato digital e interoperable sin errores manuales.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un informe médico legible, *cuando* el agente analiza el texto/imagen, *entonces* retorna el esquema de entidades clínicas tipado y validado.

---

### T-03 — Modelos Pydantic v2 para Validación Clínica y Contratos Python

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: high` |
| **Tipo** | `type: schema` |
| **Dependencias** | T-01 |
| **Complejidad** | Media (2 horas) |
| **Rol** | AI Engineer / Backend |
| **Estado** | ✅ Done |
| **Branch** | `feature/T-00-arquitectura-base` |
| **Commit ejemplo** | `feat(T-03): implementar modelos pydantic v2 sincronizados con openapi` |

**Descripción:**  
Implementar los modelos de datos en Python usando Pydantic v2, sincronizados 1:1 con el contrato `specs/openapi.yaml` para garantizar tipado estricto en la API y en los agentes.

**Entregables:**
- `[CREAR]` `backend-api/app/models/schemas.py` — Modelos Pydantic v2 (`DocumentoClinicoInput`, `DatosClinicosExtraidos`, `RespuestaTriaje`, `AuditoriaRequest`, etc.) con validaciones, enums y ejemplos.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-03--t-04-modelos-pydantic-y-agente-gemini-multimodal) para modelos y validaciones.

**Criterios de aceptación:**
- [x] Sincronización exacta 1:1 con `specs/openapi.yaml` (nombres de campos, tipos, enums y obligatoriedad).
- [x] Uso de sintaxis nativa de Pydantic v2 (`ConfigDict`, `Field(..., examples=[...])`).
- [x] Validación de enums clínicos: `NivelPrioridadEnum`, `DestinoPrincipalEnum`, `CanalOrigenEnum`.

---

### T-04 — Prompt de Sistema y Extracción Multimodal con Google Gemini

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: critical` |
| **Tipo** | `type: ia-agent` |
| **Dependencias** | T-03 |
| **Complejidad** | Alta (3 horas) |
| **Rol** | AI & Prompt Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-04-gemini-prompts-extraccion` |
| **Commit ejemplo** | `feat(T-04): implementar prompt de auditoria clinica y servicio gemini` |

**Descripción:**  
Diseñar y afinar el prompt de sistema clínico especializado para Google Gemini 1.5 Flash y completar la integración en `gemini.py` mediante el SDK `google-generativeai`, garantizando extracción JSON estructurada, propuesta de códigos CIE-10 y mecanismo de fallback determinista.

**Entregables:**
- `[CREAR]` `backend-api/app/agent/prompts.py` — Prompt de sistema médico con instrucciones de rol, directivas de cero alucinación, directivas de extracción de entidades (`paciente`, `medico`, `diagnostico`, `cie10`, `medicamentos`) y tabla de códigos CIE-10 de referencia.
- `[MODIFICAR]` `backend-api/app/services/gemini.py` — Implementación de la llamada a `google.generativeai`, soporte para texto e imágenes en base64, parseo estructurado a `DatosClinicosExtraidos` y fallback heurístico ante fallas de red o ausencia de API key.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-03--t-04-modelos-pydantic-y-agente-gemini-multimodal) para el prompt de sistema y el cliente Gemini.

**Criterios de aceptación:**
- [ ] El prompt extrae de forma confiable paciente (nombre, edad), médico (nombre, matrícula), diagnóstico, código CIE-10 sugerido y medicamentos.
- [ ] Soporta documentos en texto plano e imágenes médicas base64 (multimodal).
- [ ] Si la API Key no está presente o el servicio no responde, el fallback determinista devuelve una estructura válida en menos de 200ms sin romper la ejecución.
- [ ] La salida generada se valida limpiamente contra el modelo `DatosClinicosExtraidos`.

---

### HU-03: Detección y Notificación de Urgencias Médicas
> **Como:** Médico de guardia de emergencias.  
> **Quiero:** Que el sistema identifique de inmediato hallazgos clínicos críticos (ej. TEP, infarto, hemorragia).  
> **Para:** Intervenir precozmente al paciente y activar alertas en los canales de guardia médica.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento con hallazgo de riesgo vital, *cuando* el evaluador condicional lo procesa, *entonces* marca prioridad `Urgente`, deriva a `Cola_Emergencia_Medica` y despacha alerta inmediata.

---

### T-05 — Grafo de Decisión Condicional y Reglas de Enrutamiento

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: critical` |
| **Tipo** | `type: workflow` |
| **Dependencias** | T-03 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Backend Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-05-grafo-decision-enrutamiento` |
| **Commit ejemplo** | `feat(T-05): implementar bifurcaciones condicionales y reglas de enrutamiento` |

**Descripción:**  
Implementar el motor de enrutamiento y reglas clínicas condicionales en `graph.py` para evaluar la gravedad del documento, el score de confianza y determinar el destino departamental correspondiente.

**Entregables:**
- `[MODIFICAR]` `backend-api/app/agent/graph.py` — Grafo de decisión que evalúa el diagnóstico extraído, palabras clave de riesgo vital, nivel de confianza y tipo de documento para generar la clasificación y enrutamiento final.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-05-lógica-del-grafo-condicional-backend-apiappagentgraphpy) para reglas de bifurcación condicional.

**Criterios de aceptación:**
- [ ] Detecta hallazgos críticos (TEP, infarto, hemorragia, shock) y asigna prioridad `Urgente`, destino `Cola_Emergencia_Medica` y objeto `notificacion_generada`.
- [ ] Si `score_confianza < 0.85` o faltan datos esenciales, deriva a `Cola_Auditoria_Humana` con `requiere_auditoria_humana = true`.
- [ ] Documentos de rutina sin anomalías: asigna `Farmacia_Hospitalaria` si es receta o `Historia_Clinica_Electronica` si es estudio general.
- [ ] Genera el objeto completo `RespuestaTriaje` cumpliendo al 100% el contrato de la API.

---

### HU-04: Enrutamiento Departamental y Automatización de Alertas
> **Como:** Gestor hospitalario.  
> **Quiero:** Que los documentos procesados se sincronicen con automatizaciones de n8n para despachar alertas y notificaciones multicanal.  
> **Para:** Agilizar la entrega de información a los servicios hospitalarios sin demoras humanas.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento de rutina con score $\ge 0.85$, *cuando* se ejecuta el enrutamiento, *entonces* se asigna a Farmacia o HCE sin requerir intervención humana.

---

### T-06 — Automatización y Alertas Hospitalarias en n8n

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: high` |
| **Tipo** | `type: workflow` |
| **Dependencias** | T-04, T-05 |
| **Complejidad** | Alta (3 horas) |
| **Rol** | Workflow & DevOps Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-06-n8n-automatizacion-alertas` |
| **Commit ejemplo** | `feat(T-06): configurar servicio n8n y workflow de alertas de triaje` |

**Descripción:**  
Configurar el entorno de n8n en Docker y construir el workflow automatizado que recibe el webhook de triaje, evalúa la bifurcación condicional y despacha alertas a canales hospitalarios (Slack/Discord/Webhook).

**Entregables:**
- `[MODIFICAR]` `docker-compose.yml` — Agregar servicio `n8n` en puerto 5678 con volumen de datos persistente.
- `[CREAR]` `workflows/mediflow_triaje_workflow.json` — Workflow exportado de n8n con nodo Webhook de entrada, integración con la API de MediFlow, bifurcación condicional por severidad y nodos de alerta para guardia médica.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#️-t-06-automatización-y-alertas-hospitalarias-en-n8n) para la configuración de n8n y la estructura del workflow.

**Criterios de aceptación:**
- [ ] `docker compose up -d` levanta el servicio n8n accesible en `http://localhost:5678`.
- [ ] El workflow se puede importar en cualquier instancia de n8n sin errores de nodos faltantes.
- [ ] Ante documentos de prioridad `Urgente`, el workflow dispara la notificación de alerta con datos clínicos clave.
- [ ] Ante documentos de rutina o HITL, el workflow ejecuta la acción correspondiente sin disparar alertas sonoras de urgencia.

---

### HU-05: Derivación y Auditoría Human-in-the-Loop (HITL)
> **Como:** Auditor clínico de control de calidad.  
> **Quiero:** Que cualquier documento con baja legibilidad o confianza < 0.85 sea aislado en una cola de revisión para validación manual.  
> **Para:** Prevenir errores médicos antes de que la información impacte al paciente.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento borroso con confianza < 0.85, *cuando* se procesa, *entonces* su estado es `pendiente_auditoria`, destino `Cola_Auditoria_Humana` y se almacena en `/auditoria_humana/`.

---

### T-07 — Frontend: Panel Human-in-the-Loop para Auditoría Médica y Aprobación 1-clic

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: high` |
| **Tipo** | `type: frontend` |
| **Dependencias** | T-11 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Frontend Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-07-frontend-panel-hitl` |
| **Commit ejemplo** | `feat(T-07): crear componente PanelHITL para auditoria medica 1-clic` |

**Descripción:**  
Desarrollar el panel de auditoría clínica en la aplicación React para que un auditor médico pueda inspeccionar casos ambiguos (`score_confianza < 0.85`), corregir datos y aprobar o rechazar el triaje con 1 clic.

**Entregables:**
- `[CREAR]` `frontend/src/components/PanelHITL.tsx` — Componente interactivo de auditoría médica con formulario editable de campos clínicos.
- `[MODIFICAR]` `frontend/src/App.tsx` — Integración del panel que se activa condicionalmente cuando `requiere_auditoria_humana === true`.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-11--t-07-frontend-en-react-18--vite-dashboard-y-hitl) para el snippet de `PanelHITL.tsx`.

**Criterios de aceptación:**
- [ ] Se despliega automáticamente cuando el resultado del triaje indica `requiere_auditoria_humana = true`.
- [ ] Permite al auditor editar campos extraídos (nombre del paciente, diagnóstico principal, código CIE-10).
- [ ] Dispone de botones de acción: "✅ Aprobar Extracción (1-clic)" y "❌ Rechazar".
- [ ] Consume el endpoint `POST /api/v1/auditoria/{documento_id}` con `decision` (aprobado/rechazado), `auditor_nombre`, `comentarios` y `datos_corregidos`.
- [ ] Proporciona retroalimentación visual clara (toast o alerta) al completar la resolución.

---

### T-08 — Suite de Pruebas Automatizadas y Validación de Contratos

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: high` |
| **Tipo** | `type: dataset` |
| **Dependencias** | T-02, T-05 |
| **Complejidad** | Media (2 horas) |
| **Rol** | QA & Datasets Engineer / Backend |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-08-suite-pruebas-contrato` |
| **Commit ejemplo** | `test(T-08): ampliar tests de contrato para 3 casos y auditoria hitl` |

**Descripción:**  
Implementar la suite de pruebas automatizadas con `pytest` para validar de punta a punta los contratos OpenAPI y las reglas de negocio en los 3 casos clínicos obligatorios.

**Entregables:**
- `[MODIFICAR]` `backend-api/tests/test_contract.py` — Pruebas unitarias y de integración para Caso 1 (Rutina), Caso 2 (Urgencia TEP), Caso 3 (Ambiguo HITL), Endpoint de Auditoría (`POST /api/v1/auditoria/{id}`) y Métricas (`GET /api/v1/metricas`).

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-08-ejecución-de-pruebas-de-contrato-automatizadas) para comandos de ejecución y asserts esperados.

**Criterios de aceptación:**
- [ ] Ejecutar `pytest backend-api/tests/ -v` resulta en 100% de pruebas aprobadas (mínimo 5 tests).
- [ ] Valida esquemas de respuesta exitosa (200) y de error tipado (400, 404).
- [ ] Valida que el caso TEP active la alerta crítica y que el caso ambiguo active HITL.
- [ ] La suite se ejecuta limpiamente en el pipeline de GitHub Actions (`.github/workflows/ci.yml`).

---

### HU-06: Persistencia y Segregación en OCI Object Storage Always Free
> **Como:** Administrador de infraestructura y cumplimiento regulatorio.  
> **Quiero:** Que los documentos y sus metadatos procesados se almacenen en carpetas segregadas de OCI Object Storage Always Free.  
> **Para:** Mantener una pista de auditoría organizada y respaldada en la nube de Oracle.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento procesado, *cuando* se persiste, *entonces* se almacena en el bucket bajo `/recibidos`, `/procesados/urgentes`, `/procesados/farmacia` o `/auditoria_humana`.

---

### T-09 — Conector de Persistencia en OCI Object Storage con Instance Principal y Mock Local

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: high` |
| **Tipo** | `type: cloud-oci` |
| **Dependencias** | T-01 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Cloud & OCI Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-09-conector-oci-storage` |
| **Commit ejemplo** | `feat(T-09): implementar conector oci storage con instance principal y mock` |

**Descripción:**  
Implementar el servicio conector con OCI Object Storage en `oci.py` que soporte autenticación segura por Instance Principal (sin credenciales estáticas), persistencia de metadatos JSON y modo Mock local transparente.

**Entregables:**
- `[MODIFICAR]` `backend-api/app/services/oci.py` — Servicio OCI con soporte para autenticación Instance Principal, segregación en carpetas según triaje (`/recibidos/`, `/procesados/urgentes/`, `/procesados/farmacia/`, `/auditoria_humana/`) y persistencia local simulada en `data_mock_oci/`.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#️-t-09-persistencia-en-oci-object-storage-backend-apiappservicesocipy) para modos de trabajo y autenticación.

**Criterios de aceptación:**
- [ ] Si `OCI_MOCK_MODE=true`, persiste los archivos localmente en `data_mock_oci/` simulando la estructura del bucket sin requerir cuenta OCI activa.
- [ ] Si se ejecuta en una VM de OCI, se autentica mediante `InstancePrincipalsSecurityTokenSigner` sin claves privadas en disco.
- [ ] Los documentos y sus metadatos se organizan en las subcarpetas del bucket según la decisión del triaje.
- [ ] Permite consultar el estado de persistencia de un documento mediante su `documento_id`.

---

### T-10 — Guía y Script para Despliegue en OCI Compute VM Ampere A1 (Always Free)

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: medium` |
| **Tipo** | `type: cloud-oci` |
| **Dependencias** | T-01, T-09 |
| **Complejidad** | Media (2 horas) |
| **Rol** | Cloud & DevOps Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-10-guia-script-despliegue-oci` |
| **Commit ejemplo** | `docs(T-10): crear guia de despliegue en vm ampere a1 y script de setup` |

**Descripción:**  
Elaborar la guía técnica paso a paso y el script de aprovisionamiento automatizado para desplegar la arquitectura completa de MediFlow en una instancia OCI Compute VM Ampere A1 (Always Free: 4 OCPU, 24 GB RAM, Ubuntu 22.04).

**Entregables:**
- `[CREAR]` `docs/oci_deployment_guide.md` — Manual de arquitectura y despliegue en OCI con pasos para creación de VM, VCN, Security Lists e IAM Dynamic Group para Instance Principal.
- `[CREAR]` `scripts/deploy-oci.sh` — Script bash de aprovisionamiento en la VM (instalación de Docker, clonado, docker compose y apertura de puertos).

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#️-t-10-despliegue-en-oci-compute-vm-ampere-a1-always-free) para recursos Always Free y políticas IAM.

**Criterios de aceptación:**
- [ ] La guía cubre detalladamente la apertura de puertos en OCI Ingress Rules (8000, 8501, 5678).
- [ ] Documenta la configuración del Dynamic Group y política IAM para que la VM tenga permiso `manage objects` en el bucket sin claves estáticas.
- [ ] El script `deploy-oci.sh` es idempotente y funcional en Ubuntu 22.04 LTS aarch64/x86_64.

---

### HU-07: Dashboard de Visualización y Triaje en Vivo
> **Como:** Personal de salud / Auditor clínico.  
> **Quiero:** Una interfaz web interactiva con vista Split-Screen para cargar documentos, ver diagnósticos en tiempo real y métricas hospitalarias.  
> **Para:** Operar el triaje con máxima ergonomía y reducción de carga cognitiva.  
> **Criterios de Aceptación Gherkin:**  
> * *Dado* un documento procesado, *cuando* se consulta en pantalla, *entonces* se muestra el documento original al lado de los datos extraídos con badges semánticos de prioridad.

---

### T-11 — Frontend: Dashboard Clínico en React (Vite + TS), Selector de Casos Demo y Visor Split-Screen

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: critical` |
| **Tipo** | `type: frontend` |
| **Dependencias** | T-01, T-02 |
| **Complejidad** | Alta (3-4 horas) |
| **Rol** | Frontend Engineer |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-11-frontend-dashboard-splitscreen` |
| **Commit ejemplo** | `feat(T-11): crear dashboard clinico en react con visor split-screen` |

**Descripción:**  
Construir la interfaz de usuario en React 18 con Vite y TypeScript, incorporando el selector interactivo de los 3 casos demo, carga de archivos y el layout clínico Split-Screen para visualización ergonómica en tiempo real.

**Entregables:**
- `[MODIFICAR]` `frontend/package.json` — Dependencias de React 18, Vite, Lucide-React y tooling de build.
- `[MODIFICAR]` `frontend/vite.config.ts` — Configuración de Vite con proxy hacia backend en puerto 8000 y servidor en 8501.
- `[CREAR]` `frontend/src/App.tsx` — Aplicación principal con Header clínico, selector rápido de casos demo (1-clic), layout Split-Screen y badges cromáticos de prioridad.
- `[CREAR]` `frontend/src/index.css` — Estilos globales con paleta oscura hospitalaria de alto contraste.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-11--t-07-frontend-en-react-18--vite-dashboard-y-hitl) para la configuración de Vite y layout Split-Screen.

**Criterios de aceptación:**
- [ ] La interfaz corre en `http://localhost:8501` con tiempo de carga rápido y sin errores de consola.
- [ ] Los 3 botones demo cargan instantáneamente los textos correspondientes a los casos oficiales.
- [ ] El layout Split-Screen muestra el documento fuente a la izquierda y el diagnóstico estructurado con CIE-10 a la derecha.
- [ ] Muestra badges cromáticos dinámicos según la prioridad (Rojo Urgente pulsante, Ámbar Prioritario, Verde Rutina).
- [ ] Se conecta fluidamente con `POST /api/v1/triaje` y maneja estados de carga y errores.

---

### T-12 — Documentación Final: README.md del Proyecto y Diagramas de Arquitectura

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: critical` |
| **Tipo** | `type: docs` |
| **Dependencias** | T-06, T-09, T-11 |
| **Complejidad** | Media (2 horas) |
| **Rol** | Team Leader / QA |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-12-documentacion-final-readme` |
| **Commit ejemplo** | `docs(T-12): actualizar readme con arquitectura completa y casos demo` |

**Descripción:**  
Consolidar el `README.md` principal del repositorio con la presentación ejecutiva del proyecto, diagramas de arquitectura en Mermaid, tabla de cumplimiento de requisitos de la hackathon e instrucciones de ejecución local y en la nube.

**Entregables:**
- `[MODIFICAR]` `README.md` — Documento de presentación principal con badges de build, resumen del problema, arquitectura técnica, guía rápida de inicio (`docker compose up -d`) y evidencia de los 3 casos clínicos.

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-12--t-13-documentación-final-pitch-y-video-demo) para secciones y formato requerido.

**Criterios de aceptación:**
- [ ] Incluye diagrama de flujo del agente y grafo de decisión en sintaxis Mermaid.
- [ ] Describe claramente cómo MediFlow utiliza Oracle Cloud Infrastructure Always Free (Object Storage, VM Ampere A1).
- [ ] Explica los 3 casos clínicos de prueba obligatorios con ejemplos de entrada/salida.
- [ ] Enlaces funcionales a la documentación técnica interna (`docs/`).

---

### T-13 — Preparación del Guión, Pitch y Video Demo

| Campo | Valor |
|-------|-------|
| **Prioridad** | `priority: high` |
| **Tipo** | `type: docs` |
| **Dependencias** | T-11, T-12 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Team Leader & Equipo Completo |
| **Estado** | 🔲 Backlog |
| **Branch** | `feature/T-13-guion-video-demo` |
| **Commit ejemplo** | `docs(T-13): crear guion estructurado para pitch y video de 5 minutos` |

**Descripción:**  
Redactar el guión de presentación para el pitch de la hackathon y grabar el video de demostración técnica (máximo 5 minutos) mostrando la ejecución en vivo de los 3 escenarios clínicos y la persistencia en OCI.

**Entregables:**
- `[CREAR]` `docs/pitch_demo_script.md` — Guión minuto a minuto para el video de presentación (introducción del problema, demo del caso urgente TEP, demo del caso HITL, arquitectura OCI y cierre de impacto).

**Referencia técnica:** Ver [`docs/guia-desarrollo.md`](./guia-desarrollo.md#-t-12--t-13-documentación-final-pitch-y-video-demo) para la estructura temporal recomendada del video.

**Criterios de aceptación:**
- [ ] El guión está diseñado para un video demostrativo de no más de 5 minutos.
- [ ] Demuestra en vivo el procesamiento de los 3 casos clínicos obligatorios en la UI.
- [ ] Muestra evidencia visual de la alerta de urgencia y del panel de aprobación HITL en 1-clic.
- [ ] Muestra los archivos resultantes almacenados en OCI Object Storage.
