# 👥 MediFlow — Definición de Roles y Responsabilidades del Equipo

> **Proyecto:** MediFlow — Agente Autónomo de Triaje Clínico  
> **Programa:** Hackathon ONE G10 (Oracle Next Education & Alura) · No Country Simulation  
> **Metodología:** Spec-Driven Development (SDD) & Agile / Scrum  
> **Fecha:** Septiembre 2026  

---

## 1. Introducción y Contexto

**MediFlow** es un sistema inteligente de triaje clínico autónomo diseñado para procesar documentos médicos multimodales (órdenes médicas, recetas, estudios clínicos en PDF o imágenes), extraer información estructurada mediante modelos de lenguaje (LLM), clasificar la urgencia con un grafo de decisión (**LangGraph**), enrutar los casos a colas clínicas específicas y almacenar la evidencia en **Oracle Cloud Infrastructure (OCI) Object Storage** y base de datos relacional.

Para garantizar una ejecución eficiente, modular y sin cuellos de botella bajo la metodología **Spec-Driven Development (SDD)**, se establecen los siguientes roles dentro del equipo de desarrollo multidisciplinario.

---

## 2. Catálogo de Roles

### 🎯 1. Product Owner (PO) / Product Manager (PM)
* **Propósito:** Maximizar el valor del producto, representando las necesidades del sector clínico y priorizando el trabajo del equipo.
* **Responsabilidades Principales:**
  * Liderar la definición y mantenimiento del **Product Backlog** (Épicas, Historias de Usuario, Criterios de Aceptación).
  * Validar las reglas de negocio médico: criterios de clasificación de triaje (Emergencia, Rutina, Auditoría Humana) y severidad clínica.
  * Planificar y facilitar los eventos ágiles (Sprint Planning, Dailies, Sprint Review / Demo y Retrospectivas).
  * Actuar como punto de contacto entre los stakeholders (mentores de No Country/Oracle) y el equipo técnico.
* **Entregables:**
  * Backlog priorizado con Historias de Usuario detalladas.
  * Criterios de Aceptación y Definición de Terminado (*Definition of Done* - DoD).
  * Cronograma y alcance de entregas por sprint.

---

### 🏛️ 2. Tech Lead / Arquitecto de Software
* **Propósito:** Definir y custodiar la arquitectura técnica, la gobernanza del contrato de API y los estándares de ingeniería.
* **Responsabilidades Principales:**
  * Diseñar y gobernar la especificación central en `specs/openapi.yaml` (**Single Source of Truth**).
  * Definir patrones de diseño para el desacoplamiento de capas (Frontend, Backend, Agente IA, Almacenamiento).
  * Realizar revisiones de código (*Code Reviews*) en Pull Requests garantizando consistencia, mantenibilidad y seguridad.
  * Garantizar el cumplimiento de normativas de privacidad y manejo de datos sensibles de salud (PII).
* **Entregables:**
  * Especificación OpenAPI 3.1 validada y sincronizada.
  * Documentación de arquitectura técnica (`Docs/ARQUITECTURA-SDD.md`).
  * Estándares de desarrollo, guías de contribución y branching strategy.

---

### 🧠 3. AI / LLM Engineer (Especialista en Agentes e Inteligencia Artificial)
* **Propósito:** Diseñar, implementar y calibrar el motor inteligente de triaje clínico automatizado.
* **Responsabilidades Principales:**
  * Desarrollar la máquina de estados y el grafo de decisión utilizando **LangGraph** (`backend/app/agent/graph.py`).
  * Implementar los nodos del agente: ingestión, extracción de entidades médicas, clasificación de prioridad, score de confianza y enrutamiento.
  * Diseñar y optimizar *prompts* multimodales con **Google Gemini** (primario) y **OpenAI** (fallback).
  * Calibrar el cálculo del `confidence_score` para determinar con precisión cuándo un caso requiere derivación obligatoria a **Auditoría Médica Humana**.
  * Mitigar alucinaciones y evaluar la precisión del modelo contra muestras clínicas reales.
* **Entregables:**
  * Grafo de LangGraph compilado y testeado unitariamente.
  * Catálogo de prompts estructurados con salida en esquema Pydantic/JSON.
  * Módulo de cálculo de métricas de confianza y evaluación de precisión.

---

### ⚙️ 4. Backend Developer (Python / FastAPI)
* **Propósito:** Construir los servicios REST, la lógica de negocio, integración del agente y persistencia de datos.
* **Responsabilidades Principales:**
  * Implementar los endpoints REST definidos en OpenAPI (`/api/v1/triage`, `/api/v1/documents`, `/api/v1/health`).
  * Procesar documentos clínicos multiformato (extracción de texto e imágenes con **PyMuPDF**, `Pillow`, `python-multipart`).
  * Diseñar e implementar el acceso a datos en **PostgreSQL** (modelado relacional de triajes, pacientes y documentos).
  * Integrar el SDK de **OCI Object Storage** para la persistencia segura de archivos adjuntos.
  * Conectar los endpoints de la API con los servicios de orquestación del Agente IA.
* **Entregables:**
  * Endpoints de FastAPI implementados y documentados en Swagger.
  * Capa de servicios y repositorios de base de datos.
  * Cliente de integración para OCI Object Storage.

---

### 💻 5. Frontend Developer (React / TypeScript)
* **Propósito:** Desarrollar una interfaz clínica intuitiva, ágil y reactiva para el personal de salud.
* **Responsabilidades Principales:**
  * Implementar la aplicación web SPA con **React 18 + Vite + TypeScript**.
  * Construir el Dashboard de Triaje Clínico: visualización de métricas, colas de atención por severidad y detalle de paciente.
  * Desarrollar el módulo de carga de documentos clínicos con soporte Drag & Drop y visualización previa de archivos (PDF/JPG/PNG).
  * Consumir las APIs del backend respetando estrictamente los contratos generados desde OpenAPI.
  * Implementar manejo de estados globales, indicadores de carga (loaders) y gestión amigable de errores.
* **Entregables:**
  * Dashboard de Triaje interactivo y responsivo.
  * Componentes modulares y reutilizables documentados.
  * Capa de cliente API tipada en TypeScript.

---

### 🎨 6. UI/UX Designer
* **Propósito:** Diseñar experiencias de usuario centradas en el flujo de trabajo clínico, reduciendo la fatiga cognitiva del personal médico.
* **Responsabilidades Principales:**
  * Diseñar la arquitectura de información y los flujos de interacción clínica (desde la recepción del documento hasta la auditoría médica).
  * Diseñar un sistema de diseño visual con códigos de color clínicos estandarizados (Rojo: Emergencia, Amarillo: Urgente, Verde: Rutina, Azul/Gris: Auditoría).
  * Asegurar la accesibilidad visual (contrastes WCAG, legibilidad tipográfica).
  * Elaborar prototipos interactivos en Figma para validación temprana con el equipo y usuarios.
* **Entregables:**
  * Prototipos en alta fidelidad en Figma (Desktop y Tablet).
  * Guía de estilos (paleta de colores, tipografía, componentes UI y espaciados).
  * Flujos de usuario y mapas de experiencia clínica.

---

### 🧪 7. QA Engineer / Software Tester
* **Propósito:** Asegurar la calidad, confiabilidad, seguridad y apego al contrato técnico de toda la plataforma.
* **Responsabilidades Principales:**
  * Implementar **Contract Testing** automatizado utilizando herramientas como **Schemathesis** para validar la API contra `specs/openapi.yaml`.
  * Desarrollar suites de pruebas unitarias y de integración con **pytest** y **pytest-asyncio** en el backend.
  * Crear bancos de prueba con casos clínicos reales y sintéticos (documentos nítidos, borrosos, diagnósticos complejos, recetas ambiguas).
  * Ejecutar pruebas funcionales y End-to-End (E2E) para verificar la correcta sincronización entre Frontend, Backend y Agente IA.
* **Entregables:**
  * Plan y matriz de pruebas clínicas y técnicas.
  * Suites de pruebas automatizadas en `backend/tests/`.
  * Reportes periódicos de cobertura, defectos y validación de contrato.

---

### ☁️ 8. DevOps / Cloud Engineer
* **Propósito:** Asegurar la reproducibilidad del entorno de desarrollo, automatización de integración y el despliegue en la nube.
* **Responsabilidades Principales:**
  * Mantener y optimizar los entornos basados en contenedores (**Docker** y **Docker Compose**) para desarrollo y producción.
  * Aprovisionar y administrar los servicios en **Oracle Cloud Infrastructure (OCI)**: Buckets de Object Storage, Compute Instances, redes virtuales y credenciales IAM.
  * Implementar pipelines de **CI/CD** (GitHub Actions) que ejecuten automáticamente validación de spec (`make validate`), linters (`ruff`), chequeo de tipos (`mypy`) y suite de pruebas en cada PR.
  * Monitorizar logs, salud del sistema y variables de entorno del despliegue.
* **Entregables:**
  * Configuración reproducible de Docker (`docker-compose.dev.yml`, `Dockerfile`).
  * Flujos de GitHub Actions para Integración Continua (CI).
  * Infraestructura configurada y operativa en OCI Always Free.

---

## 3. Matriz RACI de Entregables Principales

> **Leyenda:**
> * **R (Responsible):** Quien ejecuta la tarea.
> * **A (Accountable):** Quien aprueba y responde por el resultado final.
> * **C (Consulted):** Quien aporta información o retroalimentación clave.
> * **I (Informed):** Quien debe ser notificado del avance o resultado.

| Entregable / Hito | PO / PM | Tech Lead | AI Eng | Backend | Frontend | UI/UX | QA | DevOps |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Definición del Backlog e Historias** | **A / R** | C | C | C | C | C | I | I |
| **Diseño UI/UX en Figma** | C | I | I | I | C | **A / R** | I | I |
| **Contrato OpenAPI (`specs/`)** | C | **A / R** | C | R | R | I | C | I |
| **Grafo del Agente (`LangGraph`)** | I | A | **R** | C | I | I | C | I |
| **Implementación API y DB (FastAPI)** | I | A | C | **R** | C | I | C | I |
| **Dashboard y Vistas (React / TS)** | C | A | I | C | **R** | C | C | I |
| **Almacenamiento OCI Object Storage** | I | A | I | R | I | I | I | **R** |
| **Contract Testing y Suites Pytest** | I | A | C | C | C | I | **R** | C |
| **Contenedores Docker y CI/CD** | I | A | I | C | C | I | C | **R** |
| **Release & Demo Final** | **A / R** | R | R | R | R | R | R | R |

---

## 4. Dinámica de Trabajo bajo el Flujo SDD

En el flujo **Spec-Driven Development**, los roles interactúan de forma paralela y desacoplada gracias al contrato de API:

```text
               1. Definición & Diseño
         ┌────────────────────────────────┐
         │ PO/PM: Historias & Reglas     │
         │ UI/UX: Prototipos en Figma     │
         └───────────────┬────────────────┘
                         │
                         ▼
               2. Contrato Único (SDD)
         ┌────────────────────────────────┐
         │ Tech Lead: specs/openapi.yaml  │
         └───────────────┬────────────────┘
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
 3A. Frontend     3B. Backend & DB   3C. AI Agent
 [Frontend Dev]    [Backend Dev]      [AI Engineer]
 Consume API       Implementa rutas   Compila nodos
 con mocks/spec    y persistencia     de LangGraph
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
               4. Validación & Pruebas
         ┌────────────────────────────────┐
         │ QA: Contract Testing           │
         │ (Schemathesis + Pytest + E2E)  │
         └───────────────┬────────────────┘
                         │
                         ▼
               5. Despliegue en OCI
         ┌────────────────────────────────┐
         │ DevOps: Docker + CI/CD + OCI   │
         └────────────────────────────────┘
```

---

## 5. Asignación Nominal del Equipo y Distribución de Trabajo

Con base en la reunión de alineación del equipo, los integrantes se distribuyen en las siguientes áreas de trabajo, integrando las recomendaciones técnicas para cubrir la totalidad del stack de **MediFlow**:

| Área de Trabajo | Integrantes Asignados | Enfoque y Responsabilidades Específicas |
|---|---|---|
| **Frontend & UI/UX** | **Damaris**, **Samuel** | • Desarrollo de la SPA en React 18 + Vite + TypeScript.<br>• Implementación del Dashboard Clínico, métricas y visualizador de documentos.<br>• Componentes del panel Human-in-the-Loop y gestión de colas de triaje.<br>• Prototipado y definición de estilos clínicos en Figma (códigos de severidad visual). |
| **Backend & Arquitectura SDD** | **Erick**, **Kristopher**, **Wilmer** | • Implementación de endpoints REST en FastAPI (`/triage`, `/documents`, `/health`).<br>• Procesamiento de documentos con PyMuPDF y validación multipart.<br>• Persistencia relacional en PostgreSQL (modelos de datos clínicos y triaje).<br>• Gobernanza del contrato `specs/openapi.yaml` y ejecución de scripts SDD (`make validate`, `make generate`). |
| **AI / LLM & Data Engineering** | **Kristopher**, **Jefte Reyes**<br>*(Apoyo: Henry)* | • Construcción y mantenimiento del grafo de decisión en **LangGraph** (`backend/app/agent/`).<br>• Nodos del agente: ingestión, extracción de entidades médicas, clasificación y enrutamiento.<br>• Diseño e ingeniería de prompts multimodales con **Google Gemini** (y fallback OpenAI).<br>• Calibración del algoritmo de `confidence_score` para derivación a auditoría humana. |
| **QA & Testing** | **Alonso** | • **Contract Testing** automatizado con **Schemathesis** contra `specs/openapi.yaml`.<br>• Suites de pruebas unitarias y de integración con `pytest` y `pytest-asyncio`.<br>• Diseño del banco de pruebas con documentos clínicos sintéticos y reales.<br>• Validación funcional End-to-End (E2E) del flujo clínico. |
| **DevOps & Cloud (OCI)** | **Henry**<br>*(con apoyo en IA/LLMs)* | • Orquestación y optimización de contenedores Docker (`docker-compose.dev.yml`).<br>• Aprovisionamiento y conexión con **Oracle Cloud Infrastructure (OCI Object Storage)**.<br>• Automatización de pipelines CI/CD con GitHub Actions.<br>• Apoyo transversal en infraestructura de inferencia y optimización de modelos LLM. |
| **Product Owner / Coordinación** | *Coordinación de Proyecto* | • Priorización del Backlog clínico y definición de Historias de Usuario.<br>• Validación de criterios médicos de severidad (Emergencia vs Rutina).<br>• Facilitación de ceremonias ágiles (Dailies, Review, Retrospectivas) y demos para No Country/Oracle. |

---

## 6. Próximos Pasos

Con los roles y la asignación de personas formalizada, el siguiente paso es la **definición del Product Backlog en `Docs/backlog.md`**, donde cada sub-equipo (Frontend, Backend, AI/Data, QA, DevOps) replanteará sus épicas e historias de usuario tomando como base la propuesta implementada en la rama `develop`.
