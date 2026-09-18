#!/usr/bin/env bash
# ==============================================================================
# Script de Automatización: Creación de GitHub Issues para MediFlow
# Hackathon ONE Grupo 10 — Oracle Next Education & Alura
# Requiere: GitHub CLI (`gh`) instalado y autenticado (`gh auth login`)
# ==============================================================================

set -e

echo "🚀 Iniciando la creación automatizada de GitHub Issues para MediFlow..."

# 1. Verificar si GitHub CLI está disponible
if ! command -v gh &> /dev/null; then
    echo "❌ Error: GitHub CLI ('gh') no está instalado."
    echo "Instálalo desde: https://cli.github.com/ o ejecuta 'sudo apt install gh'"
    exit 1
fi

# 2. Verificar autenticación en GitHub
if ! gh auth status &> /dev/null; then
    echo "⚠️ No has iniciado sesión en GitHub CLI. Ejecuta primero: gh auth login"
    exit 1
fi

echo "🏷️ Configurando labels del proyecto en el repositorio..."
# Labels de Prioridad
gh label create "priority: critical" --color "B60205" --description "Bloqueante – Sin esto otros integrantes no avanzan" --force 2>/dev/null || true
gh label create "priority: high"     --color "D93F0B" --description "Core – Requisito obligatorio evaluable del pliego" --force 2>/dev/null || true
gh label create "priority: medium"   --color "FBCA04" --description "Importante – Componentes de integración y soporte" --force 2>/dev/null || true
gh label create "priority: low"      --color "0E8A16" --description "Diferenciales y mejoras complementarias" --force 2>/dev/null || true

# Labels de Estado
gh label create "status: assigned"    --color "1D76DB" --description "Asignada a un integrante con fecha límite" --force 2>/dev/null || true
gh label create "status: in-progress" --color "FBCA04" --description "En desarrollo activo en branch feature/..." --force 2>/dev/null || true
gh label create "status: in-review"   --color "5319E7" --description "Pull Request abierto esperando code review" --force 2>/dev/null || true

# Labels de Categoría / Tipo
gh label create "type: structure" --color "6366F1" --description "Estructura base, configuración y tooling" --force 2>/dev/null || true
gh label create "type: schema"    --color "EC4899" --description "Contratos de datos OpenAPI 3.0 y modelos Pydantic v2" --force 2>/dev/null || true
gh label create "type: dataset"   --color "8B5CF6" --description "Casos de prueba clínicos oficiales (JSON / PDF)" --force 2>/dev/null || true
gh label create "type: ia-agent"  --color "06B6D4" --description "Google Gemini, prompts y extracción CIE-10" --force 2>/dev/null || true
gh label create "type: workflow"  --color "F97316" --description "Grafos condicionales, reglas de negocio y n8n" --force 2>/dev/null || true
gh label create "type: cloud-oci" --color "EF4444" --description "Integración con OCI Object Storage y VM Ampere A1" --force 2>/dev/null || true
gh label create "type: frontend"  --color "10B981" --description "Dashboard en React (Vite + TS), Split-Screen y HITL" --force 2>/dev/null || true
gh label create "type: docs"      --color "64748B" --description "Documentación técnica, diagramas y video demo" --force 2>/dev/null || true

echo "📋 Creando Issues del Backlog Consolidado (T-01 a T-13)..."

# T-01
echo "📌 Creando T-01: Scaffolding Base del Proyecto, Contratos OpenAPI y Variables de Entorno..."
gh issue create \
  --title "T-01 — Scaffolding Base del Proyecto, Contratos OpenAPI y Variables de Entorno" \
  --label "type: structure,priority: critical" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: critical\` |
| **Tipo** | \`type: structure\` |
| **Dependencias** | Ninguna |
| **Complejidad** | Media (2 horas) |
| **Rol** | Team Leader / DevOps |
| **Branch** | \`feature/T-00-arquitectura-base\` |
| **Commit ejemplo** | \`chore(T-01): inicializar arquitectura base y contratos openapi\` |

### Descripción
Configurar el esqueleto arquitectónico del repositorio, el contrato canónico OpenAPI 3.0.3, las plantillas de variables de entorno, la exclusión de secretos y la orquestación inicial de Docker.

### Entregables
- \`[CREAR]\` \`.gitignore\` — Exclusiones para Python, Node, temporales, \`.env\`, \`data_mock_oci/\` y \`.sf/\`.
- \`[CREAR]\` \`.env.example\` — Plantilla con variables de entorno para Gemini y OCI.
- \`[CREAR]\` \`docker-compose.yml\` — Orquestación de servicios locales (\`backend-api\` en puerto 8000).
- \`[CREAR]\` \`specs/openapi.yaml\` — Contrato formal OpenAPI 3.0.3 con 4 endpoints.
- \`[CREAR]\` \`.github/workflows/ci.yml\` — Pipeline de validación de OpenAPI con Redocly y matriz de Python 3.11–3.13.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 1: Configuración del Entorno de Desarrollo Local).

### Criterios de Aceptación
- [ ] Contrato OpenAPI 3.0.3 validado sin errores con \`npx @redocly/cli lint specs/openapi.yaml\`.
- [ ] \`.gitignore\` previene subida de secretos o archivos \`.env\`.
- [ ] \`.env.example\` documenta todas las claves y puertos requeridos con explicaciones claras.
- [ ] Estructura base de carpetas inicializada para frontend, backend-api, datasets, docs y specs."

# T-02
echo "📌 Creando T-02: Datasets Clínicos de Prueba para los 3 Escenarios Obligatorios..."
gh issue create \
  --title "T-02 — Datasets Clínicos de Prueba para los 3 Escenarios Obligatorios" \
  --label "type: dataset,priority: critical" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: critical\` |
| **Tipo** | \`type: dataset\` |
| **Dependencias** | T-01 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | QA & Datasets Engineer |
| **Branch** | \`feature/T-02-datasets-clinicos\` |
| **Commit ejemplo** | \`test(T-02): agregar datasets para los 3 casos clinicos obligatorios\` |

### Descripción
Crear los 3 archivos JSON de datasets clínicos requeridos por el pliego del proyecto para simular y validar los tres flujos del sistema: (1) Receta médica de rutina ambulatoria, (2) Urgencia médica de Tromboembolismo Pulmonar Agudo (TEP), y (3) Caso ambiguo con baja legibilidad que requiere derivación a Human-in-the-Loop (HITL).

### Entregables
- \`[CREAR]\` \`datasets/caso_1_estandar_receta.json\` — Payload JSON de receta médica ambulatoria (Enalapril / Metformina) sin hallazgos de alarma.
- \`[CREAR]\` \`datasets/caso_2_urgencia_tep.json\` — Payload JSON basado en el caso oficial del pliego (\`Carlos Mendes, 52 años\`, AngioTC de tórax con TEP CIE-10 \`I26.9\`).
- \`[CREAR]\` \`datasets/caso_3_ambiguo_hitl.json\` — Payload JSON con texto médico fragmentado o ilegible que fuerce confianza < 0.85.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Datasets Clínicos de Prueba).

### Criterios de Aceptación
- [ ] Los 3 JSON cumplen estrictamente el esquema \`DocumentoClinicoInput\` de \`specs/openapi.yaml\`.
- [ ] El Caso 1 produce prioridad \`Rutina\`, destino \`Farmacia_Hospitalaria\` y \`requiere_auditoria_humana = false\`.
- [ ] El Caso 2 produce prioridad \`Urgente\`, CIE-10 \`I26.9\`, destino \`Cola_Emergencia_Medica\` y payload de \`notificacion_generada\`.
- [ ] El Caso 3 produce \`requiere_auditoria_humana = true\`, destino \`Cola_Auditoria_Humana\` y \`score_confianza < 0.85\`.
- [ ] Los 3 archivos se pueden consumir directamente vía \`curl\` o script contra \`POST /api/v1/triaje\`."

# T-03
echo "📌 Creando T-03: Modelos Pydantic v2 para Validación Clínica y Contratos Python..."
gh issue create \
  --title "T-03 — Modelos Pydantic v2 para Validación Clínica y Contratos Python" \
  --label "type: schema,priority: high" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: high\` |
| **Tipo** | \`type: schema\` |
| **Dependencias** | T-01 |
| **Complejidad** | Media (2 horas) |
| **Rol** | AI Engineer / Backend |
| **Branch** | \`feature/T-00-arquitectura-base\` |
| **Commit ejemplo** | \`feat(T-03): implementar modelos pydantic v2 sincronizados con openapi\` |

### Descripción
Implementar los modelos de datos en Python usando Pydantic v2, sincronizados 1:1 con el contrato \`specs/openapi.yaml\` para garantizar tipado estricto en la API y en los agentes.

### Entregables
- \`[CREAR]\` \`backend-api/app/models/schemas.py\` — Modelos Pydantic v2 (\`DocumentoClinicoInput\`, \`DatosClinicosExtraidos\`, \`RespuestaTriaje\`, \`AuditoriaRequest\`, etc.) con validaciones, enums y ejemplos.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Modelos Pydantic e IA).

### Criterios de Aceptación
- [ ] Sincronización exacta 1:1 con \`specs/openapi.yaml\` (nombres, tipos, enums y obligatoriedad).
- [ ] Uso de sintaxis nativa de Pydantic v2 (\`ConfigDict\`, \`Field(..., examples=[...])\`).
- [ ] Validación de enums clínicos: \`NivelPrioridadEnum\`, \`DestinoPrincipalEnum\`, \`CanalOrigenEnum\`."

# T-04
echo "📌 Creando T-04: Prompt de Sistema y Extracción Multimodal con Google Gemini..."
gh issue create \
  --title "T-04 — Prompt de Sistema y Extracción Multimodal con Google Gemini" \
  --label "type: ia-agent,priority: critical" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: critical\` |
| **Tipo** | \`type: ia-agent\` |
| **Dependencias** | T-03 |
| **Complejidad** | Alta (3 horas) |
| **Rol** | AI & Prompt Engineer |
| **Branch** | \`feature/T-04-gemini-prompts-extraccion\` |
| **Commit ejemplo** | \`feat(T-04): implementar prompt de auditoria clinica y servicio gemini\` |

### Descripción
Diseñar y afinar el prompt de sistema clínico especializado para Google Gemini 1.5 Flash y completar la integración en \`gemini.py\` mediante el SDK \`google-generativeai\`, garantizando extracción JSON estructurada, propuesta de códigos CIE-10 y mecanismo de fallback determinista.

### Entregables
- \`[CREAR]\` \`backend-api/app/agent/prompts.py\` — Prompt de sistema médico con instrucciones de rol, directivas de cero alucinación, directivas de extracción de entidades y tabla de códigos CIE-10 de referencia.
- \`[MODIFICAR]\` \`backend-api/app/services/gemini.py\` — Implementación de la llamada a \`google.generativeai\`, soporte para texto e imágenes en base64, parseo estructurado y fallback heurístico ante fallas de red o ausencia de API key.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Prompt de Sistema e Invocación Gemini).

### Criterios de Aceptación
- [ ] El prompt extrae de forma confiable paciente, médico, diagnóstico, código CIE-10 sugerido y medicamentos.
- [ ] Soporta documentos en texto plano e imágenes médicas base64 (multimodal).
- [ ] Si la API Key no está configurada o la red falla, el fallback heurístico responde en menos de 200ms sin romper la ejecución.
- [ ] La salida generada se valida limpiamente contra el modelo \`DatosClinicosExtraidos\`."

# T-05
echo "📌 Creando T-05: Grafo de Decisión Condicional y Reglas de Enrutamiento..."
gh issue create \
  --title "T-05 — Grafo de Decisión Condicional y Reglas de Enrutamiento" \
  --label "type: workflow,priority: critical" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: critical\` |
| **Tipo** | \`type: workflow\` |
| **Dependencias** | T-03 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Backend Engineer |
| **Branch** | \`feature/T-05-grafo-decision-enrutamiento\` |
| **Commit ejemplo** | \`feat(T-05): implementar bifurcaciones condicionales y reglas de enrutamiento\` |

### Descripción
Implementar el motor de enrutamiento y reglas clínicas condicionales en \`graph.py\` para evaluar la gravedad del documento, el score de confianza y determinar el destino departamental correspondiente.

### Entregables
- \`[MODIFICAR]\` \`backend-api/app/agent/graph.py\` — Grafo de decisión que evalúa el diagnóstico extraído, palabras clave de riesgo vital, nivel de confianza y tipo de documento para generar la clasificación y enrutamiento final.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Lógica del Grafo Condicional).

### Criterios de Aceptación
- [ ] Detecta hallazgos críticos (TEP, infarto, hemorragia, shock) y asigna prioridad \`Urgente\`, destino \`Cola_Emergencia_Medica\` y objeto \`notificacion_generada\`.
- [ ] Si \`score_confianza < 0.85\` o faltan datos esenciales, deriva a \`Cola_Auditoria_Humana\` con \`requiere_auditoria_humana = true\`.
- [ ] Documentos de rutina sin anomalías: asigna \`Farmacia_Hospitalaria\` si es receta o \`Historia_Clinica_Electronica\` si es estudio general.
- [ ] Genera el objeto completo \`RespuestaTriaje\` cumpliendo al 100% el contrato de la API."

# T-06
echo "📌 Creando T-06: Automatización y Alertas Hospitalarias en n8n..."
gh issue create \
  --title "T-06 — Automatización y Alertas Hospitalarias en n8n" \
  --label "type: workflow,priority: high" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: high\` |
| **Tipo** | \`type: workflow\` |
| **Dependencias** | T-04, T-05 |
| **Complejidad** | Alta (3 horas) |
| **Rol** | Workflow & DevOps Engineer |
| **Branch** | \`feature/T-06-n8n-automatizacion-alertas\` |
| **Commit ejemplo** | \`feat(T-06): configurar servicio n8n y workflow de alertas de triaje\` |

### Descripción
Configurar el entorno de n8n en Docker y construir el workflow automatizado que recibe el webhook de triaje, evalúa la bifurcación condicional y despacha alertas a canales hospitalarios (Slack/Discord/Webhook).

### Entregables
- \`[MODIFICAR]\` \`docker-compose.yml\` — Agregar servicio \`n8n\` en puerto 5678 con volumen de datos persistente.
- \`[CREAR]\` \`workflows/mediflow_triaje_workflow.json\` — Workflow exportado de n8n con nodo Webhook de entrada, integración con la API de MediFlow, bifurcación condicional por severidad y nodos de alerta para guardia médica.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Automatización y Alertas Hospitalarias en n8n).

### Criterios de Aceptación
- [ ] \`docker compose up -d\` levanta el servicio n8n accesible en \`http://localhost:5678\`.
- [ ] El workflow se puede importar en cualquier instancia de n8n sin errores de nodos faltantes.
- [ ] Ante documentos de prioridad \`Urgente\`, el workflow dispara la notificación de alerta con datos clínicos clave.
- [ ] Ante documentos de rutina o HITL, el workflow ejecuta la acción correspondiente sin disparar alertas sonoras de urgencia."

# T-07
echo "📌 Creando T-07: Frontend: Panel Human-in-the-Loop para Auditoría Médica y Aprobación 1-clic..."
gh issue create \
  --title "T-07 — Frontend: Panel Human-in-the-Loop para Auditoría Médica y Aprobación 1-clic" \
  --label "type: frontend,priority: high" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: high\` |
| **Tipo** | \`type: frontend\` |
| **Dependencias** | T-11 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Frontend Engineer |
| **Branch** | \`feature/T-07-frontend-panel-hitl\` |
| **Commit ejemplo** | \`feat(T-07): crear componente PanelHITL para auditoria medica 1-clic\` |

### Descripción
Desarrollar el panel de auditoría clínica en la aplicación React para que un auditor médico pueda inspeccionar casos ambiguos (\`score_confianza < 0.85\`), corregir datos y aprobar o rechazar el triaje con 1 clic.

### Entregables
- \`[CREAR]\` \`frontend/src/components/PanelHITL.tsx\` — Componente interactivo de auditoría médica con formulario editable de campos clínicos.
- \`[MODIFICAR]\` \`frontend/src/App.tsx\` — Integración del panel que se activa condicionalmente cuando \`requiere_auditoria_humana === true\`.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Panel Human-in-the-Loop).

### Criterios de Aceptación
- [ ] Se despliega automáticamente cuando el resultado del triaje indica \`requiere_auditoria_humana = true\`.
- [ ] Permite al auditor editar campos extraídos (nombre del paciente, diagnóstico principal, código CIE-10).
- [ ] Dispone de botones de acción: '✅ Aprobar Extracción (1-clic)' y '❌ Rechazar'.
- [ ] Consume el endpoint \`POST /api/v1/auditoria/{documento_id}\` con \`decision\` (aprobado/rechazado), \`auditor_nombre\`, \`comentarios\` y \`datos_corregidos\`.
- [ ] Proporciona retroalimentación visual clara al completar la resolución."

# T-08
echo "📌 Creando T-08: Suite de Pruebas Automatizadas y Validación de Contratos..."
gh issue create \
  --title "T-08 — Suite de Pruebas Automatizadas y Validación de Contratos" \
  --label "type: dataset,priority: high" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: high\` |
| **Tipo** | \`type: dataset\` |
| **Dependencias** | T-02, T-05 |
| **Complejidad** | Media (2 horas) |
| **Rol** | QA & Datasets Engineer / Backend |
| **Branch** | \`feature/T-08-suite-pruebas-contrato\` |
| **Commit ejemplo** | \`test(T-08): ampliar tests de contrato para 3 casos y auditoria hitl\` |

### Descripción
Implementar la suite de pruebas automatizadas con \`pytest\` para validar de punta a punta los contratos OpenAPI y las reglas de negocio en los 3 casos clínicos obligatorios.

### Entregables
- \`[MODIFICAR]\` \`backend-api/tests/test_contract.py\` — Pruebas unitarias y de integración para Caso 1 (Rutina), Caso 2 (Urgencia TEP), Caso 3 (Ambiguo HITL), Endpoint de Auditoría (\`POST /api/v1/auditoria/{id}\`) y Métricas (\`GET /api/v1/metricas\`).

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Ejecución de Pruebas de Contrato Automatizadas).

### Criterios de Aceptación
- [ ] Ejecutar \`pytest backend-api/tests/ -v\` resulta en 100% de pruebas aprobadas (mínimo 5 tests).
- [ ] Valida esquemas de respuesta exitosa (200) y de error tipado (400, 404).
- [ ] Valida que el caso TEP active la alerta crítica y que el caso ambiguo active HITL.
- [ ] La suite se ejecuta limpiamente en el pipeline de GitHub Actions (\`.github/workflows/ci.yml\`)."

# T-09
echo "📌 Creando T-09: Conector de Persistencia en OCI Object Storage con Instance Principal y Mock Local..."
gh issue create \
  --title "T-09 — Conector de Persistencia en OCI Object Storage con Instance Principal y Mock Local" \
  --label "type: cloud-oci,priority: high" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: high\` |
| **Tipo** | \`type: cloud-oci\` |
| **Dependencias** | T-01 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Cloud & OCI Engineer |
| **Branch** | \`feature/T-09-conector-oci-storage\` |
| **Commit ejemplo** | \`feat(T-09): implementar conector oci storage con instance principal y mock\` |

### Descripción
Implementar el servicio conector con OCI Object Storage en \`oci.py\` que soporte autenticación segura por Instance Principal (sin credenciales estáticas), persistencia de metadatos JSON y modo Mock local transparente.

### Entregables
- \`[MODIFICAR]\` \`backend-api/app/services/oci.py\` — Servicio OCI con soporte para autenticación Instance Principal, segregación en carpetas según triaje (\`/recibidos/\`, \`/procesados/urgentes/\`, \`/procesados/farmacia/\`, \`/auditoria_humana/\`) y persistencia local simulada en \`data_mock_oci/\`.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Persistencia en OCI Object Storage).

### Criterios de Aceptación
- [ ] Si \`OCI_MOCK_MODE=true\`, persiste los archivos localmente en \`data_mock_oci/\` simulando la estructura del bucket sin requerir cuenta OCI activa.
- [ ] Si se ejecuta en una VM de OCI, se autentica mediante \`InstancePrincipalsSecurityTokenSigner\` sin claves privadas en disco.
- [ ] Los documentos y sus metadatos se organizan en las subcarpetas del bucket según la decisión del triaje.
- [ ] Permite consultar el estado de persistencia de un documento mediante su \`documento_id\`."

# T-10
echo "📌 Creando T-10: Guía y Script para Despliegue en OCI Compute VM Ampere A1 (Always Free)..."
gh issue create \
  --title "T-10 — Guía y Script para Despliegue en OCI Compute VM Ampere A1 (Always Free)" \
  --label "type: cloud-oci,priority: medium" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: medium\` |
| **Tipo** | \`type: cloud-oci\` |
| **Dependencias** | T-01, T-09 |
| **Complejidad** | Media (2 horas) |
| **Rol** | Cloud & DevOps Engineer |
| **Branch** | \`feature/T-10-guia-script-despliegue-oci\` |
| **Commit ejemplo** | \`docs(T-10): crear guia de despliegue en vm ampere a1 y script de setup\` |

### Descripción
Elaborar la guía técnica paso a paso y el script de aprovisionamiento automatizado para desplegar la arquitectura completa de MediFlow en una instancia OCI Compute VM Ampere A1 (Always Free: 4 OCPU, 24 GB RAM, Ubuntu 22.04).

### Entregables
- \`[CREAR]\` \`docs/oci_deployment_guide.md\` — Manual de arquitectura y despliegue en OCI con pasos para creación de VM, VCN, Security Lists e IAM Dynamic Group para Instance Principal.
- \`[CREAR]\` \`scripts/deploy-oci.sh\` — Script bash de aprovisionamiento en la VM (instalación de Docker, clonado, docker compose y apertura de puertos).

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Despliegue en OCI Compute VM Ampere A1).

### Criterios de Aceptación
- [ ] La guía cubre detalladamente la apertura de puertos en OCI Ingress Rules (8000, 8501, 5678).
- [ ] Documenta la configuración del Dynamic Group y política IAM para que la VM tenga permiso \`manage objects\` en el bucket sin claves estáticas.
- [ ] El script \`deploy-oci.sh\` es idempotente y funcional en Ubuntu 22.04 LTS aarch64/x86_64."

# T-11
echo "📌 Creando T-11: Frontend: Dashboard Clínico en React (Vite + TS), Selector de Casos Demo y Visor Split-Screen..."
gh issue create \
  --title "T-11 — Frontend: Dashboard Clínico en React (Vite + TS), Selector de Casos Demo y Visor Split-Screen" \
  --label "type: frontend,priority: critical" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: critical\` |
| **Tipo** | \`type: frontend\` |
| **Dependencias** | T-01, T-02 |
| **Complejidad** | Alta (3-4 horas) |
| **Rol** | Frontend Engineer |
| **Branch** | \`feature/T-11-frontend-dashboard-splitscreen\` |
| **Commit ejemplo** | \`feat(T-11): crear dashboard clinico en react con visor split-screen\` |

### Descripción
Construir la interfaz de usuario en React 18 con Vite y TypeScript, incorporando el selector interactivo de los 3 casos demo, carga de archivos y el layout clínico Split-Screen para visualización ergonómica en tiempo real.

### Entregables
- \`[MODIFICAR]\` \`frontend/package.json\` — Dependencias de React 18, Vite, Lucide-React y tooling de build.
- \`[MODIFICAR]\` \`frontend/vite.config.ts\` — Configuración de Vite con proxy hacia backend en puerto 8000 y servidor en 8501.
- \`[CREAR]\` \`frontend/src/App.tsx\` — Aplicación principal con Header clínico, selector rápido de casos demo (1-clic), layout Split-Screen y badges cromáticos de prioridad.
- \`[CREAR]\` \`frontend/src/index.css\` — Estilos globales con paleta oscura hospitalaria de alto contraste.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Frontend en React 18 + Vite).

### Criterios de Aceptación
- [ ] La interfaz corre en \`http://localhost:8501\` con tiempo de carga rápido y sin errores de consola.
- [ ] Los 3 botones demo cargan instantáneamente los textos correspondientes a los casos oficiales.
- [ ] El layout Split-Screen muestra el documento fuente a la izquierda y el diagnóstico estructurado con CIE-10 a la derecha.
- [ ] Muestra badges cromáticos dinámicos según la prioridad (Rojo Urgente pulsante, Ámbar Prioritario, Verde Rutina).
- [ ] Se conecta fluidamente con \`POST /api/v1/triaje\` y maneja estados de carga y errores."

# T-12
echo "📌 Creando T-12: Documentación Final: README.md del Proyecto y Diagramas de Arquitectura..."
gh issue create \
  --title "T-12 — Documentación Final: README.md del Proyecto y Diagramas de Arquitectura" \
  --label "type: docs,priority: critical" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: critical\` |
| **Tipo** | \`type: docs\` |
| **Dependencias** | T-06, T-09, T-11 |
| **Complejidad** | Media (2 horas) |
| **Rol** | Team Leader / QA |
| **Branch** | \`feature/T-12-documentacion-final-readme\` |
| **Commit ejemplo** | \`docs(T-12): actualizar readme con arquitectura completa y casos demo\` |

### Descripción
Consolidar el \`README.md\` principal del repositorio con la presentación ejecutiva del proyecto, diagramas de arquitectura en Mermaid, tabla de cumplimiento de requisitos de la hackathon e instrucciones de ejecución local y en la nube.

### Entregables
- \`[MODIFICAR]\` \`README.md\` — Documento de presentación principal con badges de build, resumen del problema, arquitectura técnica, guía rápida de inicio (\`docker compose up -d\`) y evidencia de los 3 casos clínicos.

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Documentación Final).

### Criterios de Aceptación
- [ ] Incluye diagrama de flujo del agente y grafo de decisión en sintaxis Mermaid.
- [ ] Describe claramente cómo MediFlow utiliza Oracle Cloud Infrastructure Always Free (Object Storage, VM Ampere A1).
- [ ] Explica los 3 casos clínicos de prueba obligatorios con ejemplos de entrada/salida.
- [ ] Enlaces funcionales a la documentación técnica interna (\`docs/\`)."

# T-13
echo "📌 Creando T-13: Preparación del Guión, Pitch y Video Demo..."
gh issue create \
  --title "T-13 — Preparación del Guión, Pitch y Video Demo" \
  --label "type: docs,priority: high" \
  --body "| Campo | Valor |
|---|---|
| **Prioridad** | \`priority: high\` |
| **Tipo** | \`type: docs\` |
| **Dependencias** | T-11, T-12 |
| **Complejidad** | Media (2-3 horas) |
| **Rol** | Team Leader & Equipo Completo |
| **Branch** | \`feature/T-13-guion-video-demo\` |
| **Commit ejemplo** | \`docs(T-13): crear guion estructurado para pitch y video de 5 minutos\` |

### Descripción
Redactar el guión de presentación para el pitch de la hackathon y grabar el video de demostración técnica (máximo 5 minutos) mostrando la ejecución en vivo de los 3 escenarios clínicos y la persistencia en OCI.

### Entregables
- \`[CREAR]\` \`docs/pitch_demo_script.md\` — Guión minuto a minuto para el video de presentación (introducción del problema, demo del caso urgente TEP, demo del caso HITL, arquitectura OCI y cierre de impacto).

### Referencia técnica
Ver \`docs/guia-desarrollo.md\` (Sección 2: Preparación del Guión y Pitch).

### Criterios de Aceptación
- [ ] El guión está diseñado para un video demostrativo de no más de 5 minutos.
- [ ] Demuestra en vivo el procesamiento de los 3 casos clínicos obligatorios en la UI.
- [ ] Muestra evidencia visual de la alerta de urgencia y del panel de aprobación HITL en 1-clic.
- [ ] Muestra los archivos resultantes almacenados en OCI Object Storage."

echo "✅ Todos los 13 issues del backlog han sido procesados exitosamente."
