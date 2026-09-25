# 📋 MediFlow — Product Backlog & Cronograma Oficial Hackathon ONE G10

> **Producto:** MediFlow — Agente Autónomo de Triaje Clínico  
> **Rol Emisor:** Product Owner (PO)  
> **Programa:** Hackathon ONE G10 (Oracle & Alura) · Simulación Laboral No Country  
> **Metodología:** Spec-Driven Development (SDD) & Scrum Ágil por Sprints Semanales  
> **Rama Base:** `dev-wilmer-gulcochia` (Sincronizada con `develop` commit `7ef9ff6`)  
> **Fecha:** Septiembre - Octubre 2026  
> **Estado:** Documento Oficial de Ejecución — 100% Sincronizado con el Manual del Hackathon  

---

## 1. Visión del Producto y Desafío Oficial

### 1.1 El Desafío Oficial: *2 - MediFlow · HealthTech*
> *"Agente autónomo que recibe documentos clínicos y administrativos en distintos formatos, los clasifica, extrae los datos relevantes y los distribuye al destino correcto sin intervención humana. El equipo resuelve cómo automatizar un flujo de procesamiento documental completo con lógica de decisión y manejo de casos ambiguos en un contexto donde la precisión es crítica."*  
> — **Manual del Hackathon ONE - G10 Latam**

### 1.2 El Problema Clínico
En los centros de salud, la clasificación inicial de pacientes (triaje) suele ser un cuello de botella manual, propenso a demoras, saturación del personal y sesgos humanos. Los documentos clínicos (estudios de laboratorio, derivaciones, recetas, notas médicas manuscritas) llegan en múltiples formatos heterogéneos (texto, imágenes, PDF multipágina), lo que dificulta una evaluación inmediata para priorizar emergencias médicas frente a casos de rutina ambulatoria.

### 1.3 Nuestra Solución
Desarrollamos **MediFlow**, un agente autónomo de triaje clínico impulsado por Inteligencia Artificial multimodal (**Google Gemini**) y flujos de decisión cognitiva (**LangGraph**). El sistema automatiza el proceso de recepción, extracción y clasificación para reducir drásticamente los tiempos de espera hospitalarios, priorizando la urgencia sin descartar la intervención médica humana obligatoria (**Human-in-the-Loop**) ante casos ambiguos o de baja certeza.

### 1.4 Los Tres Pilares Técnicos
1. **Spec-Driven Development (SDD) — "API-First":** Definimos un contrato estricto en `specs/openapi.yaml`. A partir de allí, generamos automáticamente los modelos de datos tipados (Pydantic para Backend y tipos TypeScript para Frontend), garantizando integración sin fricciones.
2. **Flujo de Decisión Cognitiva (LangGraph):** El agente no es un simple llamado aislado al LLM. Diseñamos un grafo de estados donde el documento pasa por nodos funcionales: *Ingestión → Extracción de Entidades → Clasificación Clínica → Evaluación de Confianza → Enrutamiento Dinámico*.
3. **Persistencia "Serverless" en OCI y Contenedores:** Cumpliendo el reto oficial de Oracle, almacenamos los documentos originales y los resultados de triaje (JSON estructurado) directamente en la nube usando **Oracle Cloud Infrastructure (OCI) Object Storage**. Toda la arquitectura se orquesta mediante **Docker Compose y Nginx** para garantizar reproducibilidad local y en producción.

---

## 2. Cronograma Oficial y Criterios de Evaluación

### 2.1 Calendario Oficial del Hackathon (6 Semanas)

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CALENDARIO OFICIAL HACKATHON ONE - G10               │
├──────────────┬─────────────────────────────┬───────────────────────────┤
│ Etapa        │ Fechas Oficiales            │ Sprint & Hitos MediFlow   │
├──────────────┼─────────────────────────────┼───────────────────────────┤
│ Semana 0     │ 14/09/2026 a 20/09/2026     │ Alineación e inscripciones│
│ Semana 1     │ 21/09/2026 a 27/09/2026     │ 🟢 SPRINT 1: Contratos/SDD│
│ Semana 2 y 3 │ 28/09/2026 a 11/10/2026     │ 🟡 SPRINT 2: Dev Paralelo │
│ Semana 4     │ 12/10/2026 a 18/10/2026     │ 🟠 SPRINT 3: Integración  │
│ Semana 5     │ 19/10/2026 a 25/10/2026     │ 🔴 SPRINT 4: QA & Cierre  │
├──────────────┴─────────────────────────────┴───────────────────────────┤
│ ⏰ FECHA LÍMITE DE ENTREGA: 25/10/2026 (Carga de materiales finales)  │
├────────────────────────────────────────────────────────────────────────┤
│ 🎤 Demo Day 1 (Clasificatorias en vivo): 27/10/2026                   │
│ 🏆 Demo Day 2 (Finalistas y Premiación): 29/10/2026                   │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Criterios de Evaluación Oficiales
La calificación final de MediFlow ante Oracle y No Country se rige por:

| Criterio Oficial | Ponderación | Reglas Clave y Condiciones |
|---|:---:|---|
| **1. Participación en Plataforma No Country** | **50%** | **EVALUACIÓN INDIVIDUAL Y ELIMINATORIA.**<br>⚠️ *Regla estricta:* Serán eliminados los estudiantes cuya participación total sea **inferior al 20%** de la actividad del grupo en la plataforma. Cada integrante debe registrar avances, interacciones y entregas semanalmente. |
| **2. Calidad, Integración y Solución** | **35%** | Arquitectura técnica, integración con OCI, calidad del código, robustez del agente LangGraph y resolución del desafío clínico. |
| **3. Presentación Final en Demo Day** | **15%** | Exposición en vivo de 5 minutos mostrando la solución funcionando (MVP real). |

---

## 3. Acuerdos de Calidad del Equipo

### 3.1 Definition of Ready (DoR) — Cuándo una Historia puede iniciar:
* [ ] La Historia de Usuario sigue el formato estándar: *Como [rol], quiero [acción] para [beneficio]*.
* [ ] La historia declara explícitamente su **Épica de pertenencia** y su **Sprint/Semana de ejecución**.
* [ ] Los Criterios de Aceptación están claramente definidos y son testeables.
* [ ] Si involucra API, los esquemas y endpoints están reflejados en `specs/openapi.yaml`.
* [ ] Dependencias técnicas identificadas y roles asignados según `Docs/roles-equipo.md`.

### 3.2 Definition of Done (DoD) — Cuándo una Historia se considera terminada:
* [ ] Código implementado en la rama correspondiente siguiendo el branch naming acordado.
* [ ] Pasa linters (`ruff` en Backend, `eslint` en Frontend) sin advertencias bloqueantes.
* [ ] Pruebas unitarias/integración escritas y pasando exitosamente (`pytest` / vitest).
* [ ] No rompe el contrato OpenAPI (`make validate` y `make test-contract` exitosos).
* [ ] Pull Request revisado y aprobado por al menos un par técnico y el Tech Lead.
* [ ] Desplegable y probado en entorno local Docker Compose (`make dev-docker`).
* [ ] **Avance reportado en la plataforma No Country** por los integrantes asignados.

---

## 4. Catálogo Formal de Épicas del Producto

Las Épicas agrupan los **dominios funcionales y arquitectónicos** de la solución (el *QUÉ* se construye a lo largo de todo el proyecto):

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   CATÁLOGO FORMAL DE ÉPICAS: MEDIFLOW                  │
├───────────────────────────────────┬────────────────────────────────────┤
│ ÉPICA 1: Ingestión Multimodal &   │ ÉPICA 4: Dashboard Clínico, UI/UX  │
│          Extracción Clínica       │          & Human-in-the-Loop       │
├───────────────────────────────────┼────────────────────────────────────┤
│ ÉPICA 2: Grafo de Decisión        │ ÉPICA 5: Aseguramiento de Calidad, │
│          Cognitiva (LangGraph)    │          Contract Testing & Pytest │
├───────────────────────────────────┼────────────────────────────────────┤
│ ÉPICA 3: Core API REST &          │ ÉPICA 6: Infraestructura Cloud OCI,│
│          Persistencia Serverless  │          Nginx, CI/CD & Entrega    │
└───────────────────────────────────┴────────────────────────────────────┘
```

### Descripción de Alcance por Épica:
* **🏥 ÉPICA 1: Ingestión Multimodal y Extracción Clínica Inteligente**  
  *Alcance:* Recepción, validación y parsing de documentos médicos heterogéneos (PDF multipágina, JPG, PNG con `PyMuPDF`) y extracción estructurada de entidades clínicas (datos de paciente, síntomas, diagnósticos, signos vitales) mediante LLM multimodal (**Google Gemini 1.5**).
* **🧠 ÉPICA 2: Grafo de Decisión Cognitiva y Triaje Autónomo (LangGraph)**  
  *Alcance:* Implementación de la máquina de estados clínicos, clasificación de prioridad (Emergencia, Urgente, Rutina), algoritmo ponderado de score de confianza (`confidence_score`) y enrutamiento dinámico a colas clínicas o auditoría médica.
* **⚙️ ÉPICA 3: Core API REST, Arquitectura SDD y Persistencia Serverless**  
  *Alcance:* Gobernanza del contrato `specs/openapi.yaml`, generación automática de código tipado (Pydantic / TypeScript), endpoints transaccionales en FastAPI y persistencia serverless de evidencias y triajes en **OCI Object Storage** (con base de datos relacional de soporte).
* **💻 ÉPICA 4: Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX**  
  *Alcance:* Prototipado clínico en Figma con código de colores de severidad, SPA en React 18 + Vite + TypeScript, tarjetas de métricas en tiempo real, módulo Drag & Drop y el panel interactivo de auditoría médica para validación humana de casos dudosos.
* **🧪 ÉPICA 5: Aseguramiento de Calidad, Contract Testing y Validación Clínica**  
  *Alcance:* Pruebas de contrato automatizadas contra el spec con **Schemathesis**, suites de pruebas unitarias y de integración en backend con `pytest`, banco de pruebas con documentos médicos sintéticos y validación de cobertura.
* **☁️ ÉPICA 6: Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales**  
  *Alcance:* Orquestación multicapa con Docker Compose, reverse proxy unificado con **Nginx** (puerto `:80`), automatización de pipelines CI/CD con GitHub Actions, smoke tests E2E y producción del Video Demo en YouTube y presentación para el Demo Day.

---

## 5. Tabla Resumen de Roles y Responsabilidades

| Rol del Proyecto | Integrantes Responsables | Enfoque y Responsabilidades Principales | Épicas Vinculadas |
|---|---|---|:---:|
| **Frontend Developer** | **Damaris**, **Samuel** | Implementación de la SPA en React 18 + TypeScript, desarrollo del Dashboard de Triaje, integración de APIs REST y visor de documentos. | **ÉPICA 4** |
| **UI/UX Designer** | **Samuel**, **Damaris** | Diseño del sistema visual clínico en Figma, accesibilidad de colores de severidad (Rojo/Amarillo/Verde), flujos de usuario y panel Human-in-the-Loop. | **ÉPICA 4** |
| **Backend Developer** | **Erick**, **Kristopher**, **Wilmer** | Desarrollo de servicios REST en FastAPI, procesamiento de documentos clínicos con PyMuPDF, persistencia serverless en OCI y base relacional de soporte. | **ÉPICA 1, ÉPICA 3** |
| **Tech Lead / Arquitecto SDD** | **Wilmer**, **Erick** | Gobernanza del contrato OpenAPI 3.1 (`specs/`), ejecución de scripts de generación SDD (`make generate`), code reviews y directrices de seguridad. | **ÉPICA 3, ÉPICA 5** |
| **AI / LLM & Data Engineer** | **Kristopher**, **Jefte Reyes**<br>*(Apoyo: Henry)* | Construcción del grafo de decisión con **LangGraph**, ingeniería de prompts multimodales con **Google Gemini**, extracción de entidades y calibración del score de confianza. | **ÉPICA 1, ÉPICA 2** |
| **QA Engineer / Tester** | **Alonso** | Contract Testing automatizado con **Schemathesis**, suites de pruebas unitarias/integración con `pytest`, smoke tests E2E y video demo final. | **ÉPICA 5, ÉPICA 6** |
| **DevOps & Cloud Engineer** | **Henry** | Optimización de contenedores Docker, proxy Nginx, aprovisionamiento de **OCI Object Storage**, automatización de pipelines CI/CD y soporte en inferencia LLM. | **ÉPICA 3, ÉPICA 6** |
| **Product Owner (PO)** | *Coordinación de Proyecto* | Gestión y priorización del Backlog, definición de criterios médicos de aceptación, facilitación de ceremonias ágiles y preparación de demos de sprint. | **Transversal** |

---

## 6. Product Backlog Secuencial por Sprints Semanales

El desarrollo se organiza en **4 Sprints cronológicos** que cubren las Semanas 1 a 5 del cronograma oficial del Hackathon:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   MAPA DE EJECUCIÓN SECUENCIAL (SPRINTS 1 AL 4)        │
├──────────────────────────┬─────────────────────────────────────────────┤
│ 🟢 SPRINT 1 (Semana 1)   │ 🟡 SPRINT 2 (Semanas 2 y 3)                 │
│ 21/09/2026 - 27/09/2026  │ 28/09/2026 - 11/10/2026                     │
│ Fundamentos y Contratos  │ Desarrollo en Paralelo con Mocks (SDD)      │
│ [US-01, US-02, US-03]    │ [US-04, US-05, US-06, US-07, US-08, US-09]  │
├──────────────────────────┼─────────────────────────────────────────────┤
│ 🟠 SPRINT 3 (Semana 4)   │ 🔴 SPRINT 4 (Semana 5)                      │
│ 12/10/2026 - 18/10/2026  │ 19/10/2026 - 25/10/2026                     │
│ Integración del Núcleo   │ Orquestación, QA, Video YouTube y Cierre    │
│ [US-10, US-11, US-12]    │ [US-13, US-14, US-15, US-16]                │
├──────────────────────────┴─────────────────────────────────────────────┤
│ ⏰ CIERRE DE ENTREGAS: 25/10/2026 | 🎤 DEMO DAY EN VIVO: 27/10 y 29/10  │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 🟢 SPRINT 1: Fundamentos y Contratos (Semana 1: 21/09 al 27/09)
> **Meta del Sprint:** Establecer el contrato único OpenAPI, generar los modelos tipados para Backend y Frontend, diseñar los mockups en Figma y estabilizar el entorno Docker. Sin este sprint, ningún squad puede programar.

#### US-01: Definición del Contrato OpenAPI 3.1 y Generación de Tipos (SDD)
* **Épica:** **ÉPICA 3 — Core API REST, Arquitectura SDD y Persistencia Serverless**
* **Sprint:** Sprint 1 (Semana 1: 21/09 - 27/09)
* **Como:** Tech Lead y Desarrolladores (Backend/Frontend).
* **Quiero:** Definir el contrato central en `specs/openapi.yaml` con endpoints (`/triage`, `/documents`, `/health`), schemas de datos médicos y respuestas HTTP tipadas, y generar el código base con `make generate`.
* **Para:** Que Frontend y Backend cuenten con una única fuente de verdad técnica y tipos fuertemente tipados (Pydantic y TypeScript) desde el día 1.
* **Prioridad:** MUST HAVE (Alta - Bloqueante) | **Estimación:** 5 SP
* **Roles Responsables:** Tech Lead (SDD) & Backend Developer
* **🛑 Depende de:** Ninguna. Es el punto de partida del proyecto.
* **Criterios de Aceptación:**
  * [ ] `specs/openapi.yaml` es válido según Spectral (`make validate` pasa con 0 errores).
  * [ ] El comando `make generate` compila los modelos Pydantic en `backend/app/_generated/` y tipos TS en `frontend/src/_generated/`.
  * [ ] Esquemas clínicos modelados: `DocumentoClinico`, `ResultadoTriaje`, `EntidadesMedicas`, `PrioridadTriaje`.

#### US-02: Sistema de Diseño Clínico y Mockups UX/UI en Figma
* **Épica:** **ÉPICA 4 — Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX**
* **Sprint:** Sprint 1 (Semana 1: 21/09 - 27/09)
* **Como:** Diseñador UI/UX y Equipo Frontend.
* **Quiero:** Diseñar en Figma los flujos e interfaces de alta fidelidad: Uploader de documentos, Dashboard de colas de triaje y Panel de Auditoría médica.
* **Para:** Guiar la maquetación visual del frontend sin ambigüedades y asegurando ergonomía clínica para personal bajo estrés.
* **Prioridad:** MUST HAVE (Alta - Bloqueante) | **Estimación:** 3 SP
* **Roles Responsables:** UI/UX Designer & Frontend Developer
* **🛑 Depende de:** Requerimientos clínicos de la visión del producto.
* **Criterios de Aceptación:**
  * [ ] Prototipo navegable en Figma de las 3 vistas principales (Dashboard, Detalle/Auditoría, Carga de Archivos).
  * [ ] Paleta de severidad médica estandarizada: Emergencia (#EF4444), Urgente (#F59E0B), Rutina (#10B981), Auditoría (#3B82F6).
  * [ ] Aprobación visual del Product Owner.

#### US-03: Estabilización de Entorno Local Docker Compose
* **Épica:** **ÉPICA 6 — Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales**
* **Sprint:** Sprint 1 (Semana 1: 21/09 - 27/09)
* **Como:** Desarrollador del equipo.
* **Quiero:** Contar con un entorno Docker Compose funcional (`make dev-docker`) con hot-reload tanto para Backend como Frontend.
* **Para:** Levantar el proyecto en un comando sin discrepancias de librerías ni fallos de empaquetado en local.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 3 SP
* **Roles Responsables:** DevOps / Cloud Engineer & Backend Developer
* **🛑 Depende de:** Configuración base del repositorio en `dev-wilmer-gulcochia`.
* **Criterios de Aceptación:**
  * [ ] `backend/Dockerfile` compila limpiamente sin errores de Hatchling (`README.md` y `app/` copiados en orden).
  * [ ] `docker-compose.dev.yml` levanta Backend (:8000) y Frontend (:5173) con hot-reload activo.
  * [ ] `backend/.env.example` documenta todas las variables requeridas (Gemini, OCI, App).

---

### 🟡 SPRINT 2: Desarrollo en Paralelo con Mocks (Semanas 2 y 3: 28/09 al 11/10)
> **Meta del Sprint:** Desarrollar en paralelo y de forma 100% independiente cada capa del sistema: los nodos del Agente IA en LangGraph, la API FastAPI con datos mockeados, el SDK de OCI y la interfaz React con cliente tipado.

#### US-04: Ingestión y Parsing de Documentos Clínicos (PyMuPDF)
* **Épica:** **ÉPICA 1 — Ingestión Multimodal y Extracción Clínica Inteligente**
* **Sprint:** Sprint 2 (Semanas 2 y 3: 28/09 - 11/10)
* **Como:** Médico / Administrativo de admisión.
* **Quiero:** Subir archivos médicos (PDF, JPG, PNG) al endpoint `POST /api/v1/documents` y extraer su texto íntegro.
* **Para:** Alimentar al agente de triaje sin requerir transcripción manual de recetas u órdenes.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** Backend Developer & AI/LLM Engineer
* **🛑 Depende de:** Modelos Pydantic generados en US-01 (Sprint 1).
* **Criterios de Aceptación:**
  * [ ] Soporte para `multipart/form-data` hasta 10 MB con validación de tipos MIME.
  * [ ] Extracción de texto de PDFs multipágina mediante `PyMuPDF`.
  * [ ] Manejo de errores devolviendo HTTP 400 descriptivo ante archivos corruptos.

#### US-05: Nodos de Extracción Clínica y Clasificación en LangGraph
* **Épica:** **ÉPICA 1 & ÉPICA 2 — Extracción Multimodal y Grafo de Decisión Cognitiva**
* **Sprint:** Sprint 2 (Semanas 2 y 3: 28/09 - 11/10)
* **Como:** Agente de Triaje IA.
* **Quiero:** Enviar el texto médico a Google Gemini 1.5 con prompts estructurados y clasificar el nivel de prioridad (Emergencia, Urgente, Rutina).
* **Para:** Extraer entidades clínicas estructuradas (síntomas, diagnóstico, signos vitales) y clasificar la severidad preliminar.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 8 SP
* **Roles Responsables:** AI / LLM & Data Engineer
* **🛑 Depende de:** Modelos Pydantic de salida generados en US-01 (Sprint 1).
* **Criterios de Aceptación:**
  * [ ] Nodos `extraction` y `classification` construidos dentro de `backend/app/agent/nodes/`.
  * [ ] Invocación a Gemini (`ChatGoogleGenerativeAI`) con fallback configurado a OpenAI.
  * [ ] Salida validada estrictamente contra el schema Pydantic `ExtractedMedicalData`.

#### US-06: Algoritmo de Score de Confianza y Lógica de Enrutamiento
* **Épica:** **ÉPICA 2 — Grafo de Decisión Cognitiva y Triaje Autónomo (LangGraph)**
* **Sprint:** Sprint 2 (Semanas 2 y 3: 28/09 - 11/10)
* **Como:** Auditor Médico de Calidad.
* **Quiero:** Que el agente calcule un `confidence_score` (0.0 a 1.0) para cada triaje.
* **Para:** Enrutar automáticamente a **Auditoría Humana** si `score < 0.8` o a la cola clínica respectiva si `score >= 0.8`.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** AI / LLM & Data Engineer & DevOps (Apoyo)
* **🛑 Depende de:** Nodos de extracción y clasificación (US-05).
* **Criterios de Aceptación:**
  * [ ] Nodo `confidence` pondera completitud de datos, certeza del LLM y consistencia de signos vitales.
  * [ ] Aristas condicionales de LangGraph derivan a `COLA_AUDITORIA_HUMANA`, `COLA_EMERGENCIA` o `COLA_RUTINA`.
  * [ ] Se registra la justificación clínica del score dentro del resultado.

#### US-07: Implementación de Endpoints FastAPI con Respuestas Mockeadas
* **Épica:** **ÉPICA 3 — Core API REST, Arquitectura SDD y Persistencia Serverless**
* **Sprint:** Sprint 2 (Semanas 2 y 3: 28/09 - 11/10)
* **Como:** Desarrollador Frontend.
* **Quiero:** Que los endpoints `/api/v1/triage`, `/api/v1/triage/{id}` y `/api/v1/health` respondan en FastAPI con datos mock basados en el schema.
* **Para:** Conectar el frontend y probar interacciones de red sin esperar a que el motor de IA esté 100% terminado.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** Backend Developer
* **🛑 Depende de:** Modelos y stubs generados en US-01 (Sprint 1).
* **Criterios de Aceptación:**
  * [ ] Endpoints implementados en `backend/app/api/v1/` devolviendo payloads conformes a `ResultadoTriaje`.
  * [ ] Endpoint `GET /api/v1/health` operativo respondiendo status de salud.

#### US-08: SDK de Almacenamiento Serverless en OCI Object Storage
* **Épica:** **ÉPICA 3 & ÉPICA 6 — Persistencia Serverless e Infraestructura Cloud**
* **Sprint:** Sprint 2 (Semanas 2 y 3: 28/09 - 11/10)
* **Como:** Arquitecto de Software y Desarrollador Backend.
* **Quiero:** Un módulo cliente (`oci_storage.py`) para subir y descargar archivos médicos y resultados JSON desde buckets de Oracle Cloud Infrastructure.
* **Para:** Cumplir el reto de persistencia serverless sin depender obligatoriamente de base de datos local.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** DevOps / Cloud Engineer & Backend Developer
* **🛑 Depende de:** Aprovisionamiento de Bucket y credenciales OCI en `.env`.
* **Criterios de Aceptación:**
  * [ ] Métodos funcionales: `upload_file`, `upload_json`, `get_file_url` (URLs pre-autenticadas PAR).
  * [ ] Modo Mock local automático cuando no se configuren credenciales OCI en desarrollo.

#### US-09: Maquetación del Dashboard y Componentes UI con Cliente Tipado
* **Épica:** **ÉPICA 4 — Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX**
* **Sprint:** Sprint 2 (Semanas 2 y 3: 28/09 - 11/10)
* **Como:** Personal médico de guardia.
* **Quiero:** Una interfaz interactiva en React + Vite que muestre tarjetas de KPIs, tabla de casos por severidad y módulo Drag & Drop.
* **Para:** Gestionar el triaje con estados de carga, filtros y consumo tipado del backend mockeado.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 8 SP
* **Roles Responsables:** Frontend Developer
* **🛑 Depende de:** Mockups Figma (US-02) y cliente TypeScript autogenerado (US-01).
* **Criterios de Aceptación:**
  * [ ] Dashboard maquetado con filtros por prioridad (Emergencia, Urgente, Rutina, Auditoría).
  * [ ] Zona Drag & Drop con previsualizador inmediato de archivos (.pdf, .jpg, .png).
  * [ ] Consumo del cliente API tipado manejando estados de carga (loaders) y errores.

---

### 🟠 SPRINT 3: Integración del Núcleo (Semana 4: 12/10 al 18/10)
> **Meta del Sprint:** Sustituir todos los mocks conectando las piezas reales: FastAPI invoca el grafo real de LangGraph y Gemini, los resultados y archivos se guardan en OCI Object Storage, y el Frontend muestra el triaje en vivo con soporte para el panel Human-in-the-Loop.

#### US-10: Conexión FastAPI con el Motor Real de LangGraph y Gemini
* **Épica:** **ÉPICA 2 & ÉPICA 3 — Grafo de Decisión Cognitiva y Core API REST**
* **Sprint:** Sprint 3 (Semana 4: 12/10 - 18/10)
* **Como:** Sistema MediFlow Integrado.
* **Quiero:** Que el endpoint `POST /api/v1/triage` procese el archivo entrante a través del grafo real de LangGraph.
* **Para:** Emitir un diagnóstico automatizado, score de confianza y prioridad clínica real basada en LLM multimodal.
* **Prioridad:** MUST HAVE (Alta - Ruta Crítica) | **Estimación:** 8 SP
* **Roles Responsables:** Backend Developer & AI / LLM Engineer
* **🛑 Depende de:** Endpoints FastAPI (US-07) y Grafo LangGraph completo (US-05, US-06).
* **Criterios de Aceptación:**
  * [ ] Reemplazo total de datos mock por la ejecución del grafo `compiled_graph.ainvoke()`.
  * [ ] Respuesta HTTP 200 con payload real cumpliendo estrictamente `specs/openapi.yaml`.
  * [ ] Tiempo de inferencia optimizado y control de timeouts de API externa.

#### US-11: Persistencia Activa Serverless en OCI Object Storage y DB Soporte
* **Épica:** **ÉPICA 3 & ÉPICA 6 — Persistencia Serverless e Infraestructura Cloud**
* **Sprint:** Sprint 3 (Semana 4: 12/10 - 18/10)
* **Como:** Oficial de Cumplimiento y Seguridad.
* **Quiero:** Que cada triaje procesado almacene automáticamente el archivo original y el JSON de resultado en OCI Object Storage, e indexe el caso en PostgreSQL.
* **Para:** Garantizar respaldo duradero en la nube de Oracle y permitir consultas indexadas inmediatas desde el dashboard.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** Backend Developer & DevOps / Cloud Engineer
* **🛑 Depende de:** SDK OCI (US-08) y pipeline del agente activo (US-10).
* **Criterios de Aceptación:**
  * [ ] El resultado JSON y el documento se suben a OCI organizados por carpeta de severidad (`/urgentes/`, `/rutina/`, `/auditoria/`).
  * [ ] Registro de metadatos clínicos en tablas PostgreSQL (`triage_cases`, `patients`) según `schema.sql`.

#### US-12: Panel Human-in-the-Loop y Auditoría Médica en Vivo
* **Épica:** **ÉPICA 4 — Dashboard Clínico, Human-in-the-Loop y Experiencia UI/UX**
* **Sprint:** Sprint 3 (Semana 4: 12/10 - 18/10)
* **Como:** Médico Auditor / Supervisor de Triaje.
* **Quiero:** Una vista especializada en el frontend para revisar casos ambiguos (`confidence_score < 0.8`), ver el documento original lado a lado con el resultado del agente, y corregir o aprobar la prioridad clínica.
* **Para:** Mantener la seguridad del paciente como regla inquebrantable mediante validación humana.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 8 SP
* **Roles Responsables:** Frontend Developer & Backend Developer
* **🛑 Depende de:** Dashboard frontend (US-09) y API real integrada (US-10, US-11).
* **Criterios de Aceptación:**
  * [ ] Vista comparativa: Documento original (PDF/imagen) vs datos clínicos extraídos por la IA y motivo de la baja confianza.
  * [ ] Formulario interactivo para ajustar diagnóstico o nivel de prioridad.
  * [ ] Botón de "Confirmar Auditoría" que envía `PUT /api/v1/triage/{id}/audit`, actualiza el estado en backend y remueve el caso de la cola de pendientes.

---

### 🔴 SPRINT 4: Orquestación, QA, Video YouTube y Cierre (Semana 5: 19/10 al 25/10)
> **Meta del Sprint:** Asegurar la calidad con Contract Testing, empaquetar la aplicación tras Nginx, validar el flujo E2E, publicar el Video Demo en YouTube y preparar al expositor para el Demo Day en vivo.

#### US-13: Orquestación con Reverse Proxy Nginx y Docker Compose de Producción
* **Épica:** **ÉPICA 6 — Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales**
* **Sprint:** Sprint 4 (Semana 5: 19/10 - 25/10)
* **Como:** DevOps Engineer y Equipo de Desarrollo.
* **Quiero:** Empaquetar Frontend, Backend y Nginx en un Docker Compose unificado para producción.
* **Para:** Servir la plataforma en un puerto único (:80) con ruteo transparente (`/` para React y `/api` para FastAPI) sin problemas de CORS ni puertos expuestos dispersos.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** DevOps / Cloud Engineer & Backend Developer
* **🛑 Depende de:** Frontend y Backend completamente funcionales e integrados (Sprint 3).
* **Criterios de Aceptación:**
  * [ ] Configuración de Nginx en `infrastructure/nginx/nginx.conf` ruteando peticiones correctamente.
  * [ ] `docker compose up` levanta todos los servicios de forma limpia y orquestada.

#### US-14: Contract Testing Automatizado (Schemathesis) y Suites Pytest
* **Épica:** **ÉPICA 5 — Aseguramiento de Calidad, Contract Testing y Validación Clínica**
* **Sprint:** Sprint 4 (Semana 5: 19/10 - 25/10)
* **Como:** QA Engineer y Tech Lead.
* **Quiero:** Ejecutar pruebas automáticas de contrato contra `specs/openapi.yaml` y pruebas unitarias/integración de todos los módulos.
* **Para:** Certificar que el sistema cumple 100% con la especificación y asegurar que no existan regresiones de código.
* **Prioridad:** MUST HAVE (Alta) | **Estimación:** 5 SP
* **Roles Responsables:** QA Engineer & Tech Lead (SDD)
* **🛑 Depende de:** API completa e integrada (Sprint 3).
* **Criterios de Aceptación:**
  * [ ] `make test-contract` ejecuta Schemathesis con 0 discrepancias contractuales.
  * [ ] `make test-backend` corre suites con `pytest` y `pytest-asyncio` con cobertura superior al 75%.

#### US-15: Pipeline de CI/CD en GitHub Actions
* **Épica:** **ÉPICA 6 — Infraestructura Cloud OCI, Nginx, CI/CD y Entregables Finales**
* **Sprint:** Sprint 4 (Semana 5: 19/10 - 25/10)
* **Como:** Tech Lead y Product Owner.
* **Quiero:** Un pipeline que valide automáticamente cada Pull Request antes de fusionarlo a `develop`.
* **Para:** Garantizar que ningún commit rompa el linter, los tests ni el contrato de la API.
* **Prioridad:** SHOULD HAVE (Media) | **Estimación:** 3 SP
* **Roles Responsables:** DevOps / Cloud Engineer & QA Engineer
* **🛑 Depende de:** Suites de prueba (US-14) y Docker funcional (US-13).
* **Criterios de Aceptación:**
  * [ ] Workflow de GitHub Actions que corre: `ruff`, `make validate` y `pytest`.
  * [ ] Bloqueo automático de PRs que no superen los checks.

#### US-16: Smoke Tests E2E, Video Demo en YouTube y Preparación Demo Day
* **Épica:** **ÉPICA 5 & ÉPICA 6 — Aseguramiento de Calidad y Entregables Oficiales del Hackathon**
* **Sprint:** Sprint 4 (Semana 5: 19/10 - 25/10)
* **Como:** Jurado de Oracle & No Country / Evaluadores del Hackathon.
* **Quiero:** Un video demostrativo público en YouTube y una presentación técnica en vivo de 5 minutos mostrando el sistema en funcionamiento.
* **Para:** Evaluar la propuesta de valor médica, la viabilidad técnica, la integración cloud en OCI y el impacto clínico para la clasificación final.
* **Prioridad:** MUST HAVE (Alta - Entrega Obligatoria) | **Estimación:** 5 SP
* **Roles Responsables:** QA Engineer, Product Owner & DevOps
* **🛑 Depende de:** Todo el sistema operativo e integrado (US-10 a US-14).
* **Criterios de Aceptación (Requisitos Oficiales del Manual):**
  * [ ] **Smoke Test E2E validado:** Subida de PDF real → Procesamiento LangGraph/Gemini → Guardado en OCI → Renderizado en Dashboard.
  * [ ] **Video Demo Obligatorio:** Duración sugerida de **5 minutos** (máximo 10 min), publicado en **YouTube** y enlace cargado en la plataforma No Country antes del 25/10/2026.
  * [ ] **Inscripción al Demo Day:** Formulario completado por el representante antes de la fecha límite.
  * [ ] **Presentación en Vivo (Demo Day 1 y 2):** Pitch estricto de **5 minutos** realizado por **una sola persona** representante, demostrando el software funcionando en vivo (MVP).
  * [ ] **Carga de materiales:** Repositorio GitHub con README y enlaces cargados antes del **25/10/2026**.

---

## 7. Matriz Cruzada de Trazabilidad: Épica vs. Sprint vs. Rol

| Épica del Producto | Sprint 1 (Semana 1) | Sprint 2 (Sem. 2-3) | Sprint 3 (Semana 4) | Sprint 4 (Semana 5) | Rol Líder |
|---|:---:|:---:|:---:|:---:|---|
| **ÉPICA 1: Ingestión & Extracción** | — | **US-04**, **US-05** | — | — | Backend Developer & AI Engineer |
| **ÉPICA 2: Grafo LangGraph** | — | **US-05**, **US-06** | **US-10** | — | AI / LLM & Data Engineer |
| **ÉPICA 3: Core API REST & OCI** | **US-01** | **US-07**, **US-08** | **US-10**, **US-11** | — | Backend Developer & Tech Lead |
| **ÉPICA 4: Dashboard UI & HITL** | **US-02** | **US-09** | **US-12** | — | Frontend Developer & UI/UX |
| **ÉPICA 5: QA & Contract Testing** | — | — | — | **US-14**, **US-16** | QA Engineer / Tester |
| **ÉPICA 6: Infraestructura OCI & Demo** | **US-03** | **US-08** | **US-11** | **US-13**, **US-15**, **US-16** | DevOps / Cloud Engineer |
