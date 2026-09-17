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
gh label create "priority: high"     --color "D93F0B" --description "Core – Funcionalidad esencial del MVP" --force 2>/dev/null || true
gh label create "priority: medium"   --color "FBCA04" --description "Importante – Componentes de integración y soporte" --force 2>/dev/null || true
gh label create "priority: low"      --color "0E8A16" --description "Diferenciales y mejoras visuales/documentales" --force 2>/dev/null || true

# Labels de Estado
gh label create "status: assigned"    --color "1D76DB" --description "Asignada a un integrante con fecha límite" --force 2>/dev/null || true
gh label create "status: in-progress" --color "FBCA04" --description "En desarrollo activo en branch feature/..." --force 2>/dev/null || true
gh label create "status: in-review"   --color "5319E7" --description "Pull Request abierto esperando code review" --force 2>/dev/null || true

# Labels de Categoría / Tipo
gh label create "type: structure" --color "6366F1" --description "Estructura base, configuración y tooling" --force 2>/dev/null || true
gh label create "type: schema"    --color "EC4899" --description "Contratos de datos JSON Schema / SDD" --force 2>/dev/null || true
gh label create "type: dataset"   --color "8B5CF6" --description "Casos de prueba clínicos (PDF/imagen/texto)" --force 2>/dev/null || true
gh label create "type: ia-agent"  --color "06B6D4" --description "Google Gemini, prompts y extracción CIE-10" --force 2>/dev/null || true
gh label create "type: workflow"  --color "F97316" --description "Nodos de n8n, grafos condicionales y Webhooks" --force 2>/dev/null || true
gh label create "type: cloud-oci" --color "EF4444" --description "Integración con OCI Object Storage Always Free" --force 2>/dev/null || true
gh label create "type: frontend"  --color "10B981" --description "UI en React (Vite + TS), visor y panel HITL" --force 2>/dev/null || true
gh label create "type: docs"      --color "64748B" --description "Documentación, diagramas y video demo" --force 2>/dev/null || true

echo "📋 Creando Issues del Backlog Atómico (T-01 a T-18)..."

# T-01
echo "📌 Creando T-01: Scaffolding Base del Proyecto y Variables de Entorno..."
gh issue create \
  --title "T-01 — Scaffolding Base del Proyecto y Variables de Entorno" \
  --label "type: structure,priority: critical" \
  --body "### Descripción
Inicializar el esqueleto del repositorio con el archivo de ignorados \`.gitignore\`, la plantilla de configuración \`.env.example\` con las claves necesarias para Gemini y OCI, y el archivo base \`requirements.txt\`.

### Entregables
- Archivo \`.gitignore\` con exclusiones para Python, Node, \`.env\`, \`.oci/\` y temporales.
- Archivo `requirements.txt` con dependencias base (`pydantic`, `jsonschema`, `google-generativeai`, `oci`, `pytest`).

### Criterios de Aceptación
- [ ] \`.gitignore\` previene subir credenciales o archivos sensibles al repositorio.
- [ ] \`.env.example\` contiene todas las variables descritas con comentarios claros.
- [ ] \`pip install -r requirements.txt\` se instala sin errores."

# T-02
echo "📌 Creando T-02: Dataset Caso 1: Flujo Estándar de Receta Médica..."
gh issue create \
  --title "T-02 — Dataset Caso 1: Flujo Estándar de Receta Médica" \
  --label "type: dataset,priority: high" \
  --body "### Descripción
Crear el primer caso de prueba oficial obligatorio: una receta médica ambulatoria de rutina (tratamiento de mantenimiento crónico) sin signos de alarma que debe derivarse a Farmacia con alta confianza.

### Entregables
- Archivo \`datasets/caso_1_estandar_receta.json\` conforme a \`schemas/input_document.json\`.
- Documento de texto simulado con datos claros: paciente, médico, matrícula, diagnóstico, fármaco y posología.
- JSON esperado de respuesta de triaje validado contra \`schemas/triage_response.json\`.

### Criterios de Aceptación
- [ ] El payload de entrada valida al 100% con \`schemas/input_document.json\`.
- [ ] La prioridad clínica resultante esperada es \`Rutina\`.
- [ ] El destino de enrutamiento esperado es \`Farmacia_Hospitalaria\`.
- [ ] \`requiere_auditoria_humana\` esperado es \`false\`."

# T-03
echo "📌 Creando T-03: Dataset Caso 2: Urgencia Médica de Tromboembolismo Pulmonar (TEP)..."
gh issue create \
  --title "T-03 — Dataset Caso 2: Urgencia Médica de Tromboembolismo Pulmonar (TEP)" \
  --label "type: dataset,priority: critical" \
  --body "### Descripción
Crear el segundo caso oficial: informe radiológico de tomografía con hallazgo crítico de Tromboembolismo Pulmonar Agudo (TEP / CIE-10: I26.9). Debe activar la prioridad Urgente, derivación a Emergencias y disparo de alerta médica.

### Entregables
- Archivo \`datasets/caso_2_urgencia_tep.json\` basado en el texto del enunciado oficial de la hackathon.
- Payload de salida esperada con \`notificacion_generada\` y ruta en OCI \`procesados/urgentes/\`.

### Criterios de Aceptación
- [ ] El documento simula el caso de alta gravedad descrito en \`proyecto.md\`.
- [ ] \`clasificacion.nivel_prioridad\` es \`Urgente\`.
- [ ] \`decision_enrutamiento.destino_principal\` es \`Cola_Emergencia_Medica\`.
- [ ] Contiene objeto \`notificacion_generada\` completo con canal y mensaje de alerta."

# T-04
echo "📌 Creando T-04: Dataset Caso 3: Caso Ambiguo con Derivación a Human-in-the-Loop (HITL)..."
gh issue create \
  --title "T-04 — Dataset Caso 3: Caso Ambiguo con Derivación a Human-in-the-Loop (HITL)" \
  --label "type: dataset,priority: high" \
  --body "### Descripción
Crear el tercer caso oficial: un documento médico escaneado con baja resolución, letra manuscrita de difícil lectura o datos clínicos contradictorios que produzcan un score de confianza < 0.85 y obliguen a revisión humana.

### Entregables
- Archivo \`datasets/caso_3_ambiguo_hitl.json\`.
- Payload de salida esperado con \`status: pendiente_auditoria\`, destino \`Cola_Auditoria_Humana\` y \`requiere_auditoria_humana: true\`.

### Criterios de Aceptación
- [ ] \`score_confianza_clasificacion\` es inferior a 0.85 (ej. 0.62).
- [ ] \`decision_enrutamiento.destino_principal\` es \`Cola_Auditoria_Humana\`.
- [ ] Se documenta el campo \`motivo_ambiguedad\` explicando los datos ilegibles.
- [ ] La ruta de persistencia esperada es \`auditoria_humana/\`."

# T-05
echo "📌 Creando T-05: Modelos Pydantic para Validación Clínica en Python..."
gh issue create \
  --title "T-05 — Modelos Pydantic para Validación Clínica en Python" \
  --label "type: schema,priority: high" \
  --body "### Descripción
Implementar las clases Pydantic v2 en \`src/models.py\` correspondientes a los JSON Schemas de entrada, extracción clínica y respuesta de triaje, permitiendo tipado estricto en los scripts de Python y en la UI.

### Entregables
- Módulo \`src/models.py\` con \`DocumentoInput\`, \`Paciente\`, \`Medico\`, \`ExtraccionClinica\`, \`DecisionEnrutamiento\` y \`RespuestaTriaje\`.
- Métodos de serialización y validación \`model_validate_json()\`.

### Criterios de Aceptación
- [ ] Validación estricta con Pydantic v2 sin errores de tipos.
- [ ] Serialización con alias compatibles (\`nome\` / \`nombre\`).
- [ ] Métodos auxiliares para determinar automáticamente si requiere auditoría humana."

# T-06
echo "📌 Creando T-06: Prompt de Sistema y Agente Extractor Multimodal con Google Gemini..."
gh issue create \
  --title "T-06 — Prompt de Sistema y Agente Extractor Multimodal con Google Gemini" \
  --label "type: ia-agent,priority: critical" \
  --body "### Descripción
Diseñar e implementar el módulo en Python (\`src/gemini_extractor.py\`) que consume la API de Google Gemini (Gemini 1.5 Flash / 2.0 Flash) con *Structured Outputs* o modo JSON para extraer las entidades clínicas y calcular el score de confianza.

### Entregables
- Módulo \`src/gemini_extractor.py\`.
- Prompt clínico en \`src/prompts.py\` con instrucciones de rol, detección de CIE-10 y reglas de evaluación de legibilidad.
- Soporte para entrada en texto plano e imágenes/PDFs en base64.

### Criterios de Aceptación
- [ ] La salida de Gemini se ajusta al modelo \`ExtraccionClinica\` sin fallos de parseo.
- [ ] Reconoce correctamente cuadros de riesgo vital marcando \`nivel_prioridad: Urgente\`.
- [ ] Infiere el código CIE-10 adecuado (ej. \`I26.9\` para TEP)."

# T-07
echo "📌 Creando T-07: Motor de Lógica de Decisión Condicional y Reglas de Enrutamiento..."
gh issue create \
  --title "T-07 — Motor de Lógica de Decisión Condicional y Reglas de Enrutamiento" \
  --label "type: workflow,priority: critical" \
  --body "### Descripción
Construir la función de evaluación condicional (\`src/routing_engine.py\`) que recibe la extracción de Gemini y aplica el árbol de decisiones: evalúa score de confianza (< 0.85 ➔ Auditoría), detecta urgencias críticas (➔ Guardia + Alerta) y enruta el resto según especialidad/tipo de documento.

### Entregables
- Módulo \`src/routing_engine.py\` con función \`evaluar_enrutamiento(extraccion) -> DecisionEnrutamiento\`.
- Pruebas unitarias en \`tests/test_routing.py\` validando las tres ramas del árbol de decisión.

### Criterios de Aceptación
- [ ] Confianza < 0.85 desvía obligatoriamente a \`Cola_Auditoria_Humana\` con \`requiere_auditoria_humana = true\`.
- [ ] Prioridad \`Urgente\` desvía a \`Cola_Emergencia_Medica\` y genera mensaje de alerta médica.
- [ ] Recetas estándar van a \`Farmacia_Hospitalaria\` y estudios a \`Historia_Clinica_Electronica\`."

# T-08
echo "📌 Creando T-08: Conector de Persistencia en OCI Object Storage (Always Free)..."
gh issue create \
  --title "T-08 — Conector de Persistencia en OCI Object Storage (Always Free)" \
  --label "type: cloud-oci,priority: high" \
  --body "### Descripción
Implementar el cliente de integración con Oracle Cloud Infrastructure (\`src/oci_storage.py\`) utilizando el SDK de Python \`oci\`. Debe soportar subida de objetos y segregación por carpetas (\`/recibidos\`, \`/procesados/urgentes\`, \`/auditoria_humana\`), con modo fallback/mock para desarrollo local.

### Entregables
- Módulo \`src/oci_storage.py\` con métodos \`subir_documento()\` y \`verificar_bucket()\`.
- Soporte para autenticación por archivo de configuración de OCI (\`~/.oci/config\`) o variables de entorno.
- Modo simulación local para pruebas cuando no se cuente con credenciales activas.

### Criterios de Aceptación
- [ ] Sube correctamente el archivo JSON y el documento original con la ruta segregada por estado.
- [ ] Retorna el bloque \`almacenamiento_oci\` conforme al schema (\`bucket\`, \`ruta_objeto\`, \`status_backup: exito\`).
- [ ] Incluye manejo de excepciones y reintentos en caso de timeout de red."

# T-09
echo "📌 Creando T-09: Configuración de Docker Compose para n8n Local..."
gh issue create \
  --title "T-09 — Configuración de Docker Compose para n8n Local" \
  --label "type: workflow,priority: medium" \
  --body "### Descripción
Crear el archivo \`docker-compose.yml\` para levantar una instancia local de n8n con persistencia en volumen y variables de entorno preconfiguradas, permitiendo que el equipo diseñe y pruebe flujos sin coste.

### Entregables
- Archivo \`docker-compose.yml\` en la raíz configurando el servicio \`n8n\`.
- Documentación breve en \`docs/n8n_setup.md\` con comandos \`docker compose up -d\` y credenciales por defecto.

### Criterios de Aceptación
- [ ] \`docker compose up -d\` levanta n8n en el puerto \`5678\`.
- [ ] Los datos y credenciales persisten tras reiniciar el contenedor (\`n8n_data\` volumen)."

# T-10
echo "📌 Creando T-10: Workflow de n8n: Webhook, Nodos de IA y Bifurcación Condicional..."
gh issue create \
  --title "T-10 — Workflow de n8n: Webhook, Nodos de IA y Bifurcación Condicional" \
  --label "type: workflow,priority: critical" \
  --body "### Descripción
Construir y exportar el workflow visual completo en n8n: Webhook de entrada (\`POST /webhook/triaje\`), nodo de consulta al LLM Gemini (o API Python), nodos de bifurcación condicional (\`Switch\` / \`IF\`) y nodo de respuesta HTTP con el JSON estructurado.

### Entregables
- Archivo exportado \`workflows/mediflow_triaje_workflow.json\` importable en cualquier n8n.
- Diagrama del workflow en captura de pantalla para el README.
- Conexión con los 3 flujos de salida (Urgente, Estándar, Auditoría).

### Criterios de Aceptación
- [ ] El webhook recibe un payload de entrada y responde con el JSON de salida formal de MediFlow.
- [ ] El nodo condicional evalúa el score de confianza y el nivel de urgencia.
- [ ] El archivo exportado se importa sin errores en una instalación limpia de n8n."

# T-11
echo "📌 Creando T-11: Integración de Notificaciones de Alerta en n8n (Slack / Webhook)..."
gh issue create \
  --title "T-11 — Integración de Notificaciones de Alerta en n8n (Slack / Webhook)" \
  --label "type: workflow,priority: medium" \
  --body "### Descripción
Añadir al workflow de n8n un nodo de notificación instantánea (Slack Webhook, Discord o Email) que se dispare exclusivamente cuando el triaje detecte prioridad \`Urgente\`.

### Entregables
- Nodo de Slack/Webhook integrado en \`workflows/mediflow_triaje_workflow.json\`.
- Mensaje formateado con icono de alerta roja, nombre del paciente, diagnóstico crítico (ej. TEP) y canal emisor.

### Criterios de Aceptación
- [ ] Se envía un mensaje al canal configurado cuando la prioridad es \`Urgente\`.
- [ ] No envía notificaciones en casos de \`Rutina\` o \`Prioritario\`."

# T-12
echo "📌 Creando T-12: UI React: Selector de Casos Demo y Subida de Archivos..."
gh issue create \
  --title "T-12 — UI React: Selector de Casos Demo y Subida de Archivos" \
  --label "type: frontend,priority: high" \
  --body "### Descripción
Construir la pantalla principal en React 18 + Vite (\`frontend/src/App.tsx\`) con la barra superior de métricas del hospital, selector de casos preconfigurados de prueba (Caso 1, 2 y 3) y componente de subida de archivos para PDFs o imágenes.

### Entregables
- Proyecto configurado con Vite + React + TypeScript en \`frontend/\`.
- Tipos de TypeScript autogenerados con \`frontend/scripts/generate-api.sh\`.
- Selector rápido con un clic para cargar los datos de \`datasets/\` sin necesidad de buscar archivos.

### Criterios de Aceptación
- [ ] La aplicación inicia limpiamente con \`npm run dev\` en el puerto 8501.
- [ ] Permite alternar entre los 3 casos demo cargando sus textos y metadatos al instante.
- [ ] Soporta subir archivos PDF o imágenes vía drag & drop."

# T-13
echo "📌 Creando T-13: UI React: Visor Split-Screen y Panel de Resultados de Triaje..."
gh issue create \
  --title "T-13 — UI React: Visor Split-Screen y Panel de Resultados de Triaje" \
  --label "type: frontend,priority: high" \
  --body "### Descripción
Implementar el layout Split-Screen en React (2 columnas): columna izquierda mostrando el documento fuente y columna derecha mostrando los datos clínicos extraídos, badges cromáticos de prioridad (Rojo/Ámbar/Verde), código CIE-10 y destino de enrutamiento.

### Entregables
- Componentes modulares en \`frontend/src/\`.
- Badges con la paleta de \`docs/design_system.md\` para prioridad y CIE-10.
- Integración con la API FastAPI en \`http://localhost:8000/api/v1/triaje\`.

### Criterios de Aceptación
- [ ] Muestra el documento original al lado de los datos extraídos por la IA.
- [ ] Muestra badge rojo pulsante ante casos de urgencia con la notificación generada.
- [ ] Visualiza el estado y ruta de respaldo en OCI Object Storage."

# T-14
echo "📌 Creando T-14: UI React: Panel Human-in-the-Loop (Auditoría Médica)..."
gh issue create \
  --title "T-14 — UI React: Panel Human-in-the-Loop (Auditoría Médica)" \
  --label "type: frontend,priority: high" \
  --body "### Descripción
Construir la sección interactiva de auditoría humana: cuando el documento tenga baja confianza (< 0.85) o esté en \`auditoria_humana\`, la interfaz debe habilitar un formulario editable donde el médico pueda corregir campos dudosos y pulsar \`[Aprobar y Enrutar]\` o \`[Rechazar]\`.

### Entregables
- Componente de auditoría en \`frontend/src/\`.
- Botón de aprobación con retroalimentación visual inmediata conectando a \`POST /api/v1/auditoria/{id}\`.
- Actualización simulada o directa del estado en OCI Object Storage a \`/procesados/\`.

### Criterios de Aceptación
- [ ] Se activa automáticamente en casos con score < 0.85 o marcados como ambiguos.
- [ ] Permite modificar el diagnóstico, médico o CIE-10 antes de aprobar.
- [ ] Al hacer clic en Aprobar, muestra confirmación visual y actualiza el estado a \`procesado\`."

# T-15
echo "📌 Creando T-15: Suite de Pruebas Automatizadas de Extracción y Enrutamiento..."
gh issue create \
  --title "T-15 — Suite de Pruebas Automatizadas de Extracción y Enrutamiento" \
  --label "type: dataset,priority: high" \
  --body "### Descripción
Crear el script de prueba integral \`tests/test_pipeline.py\` (usando \`pytest\` o \`unittest\`) que ejecute los 3 datasets de prueba contra el motor de routing y verifique que las respuestas cumplen 100% con los esquemas y las decisiones esperadas.

### Entregables
- Archivo \`tests/test_pipeline.py\`.
- Ejecución reproducible con un comando (\`python -m pytest tests/\`).

### Criterios de Aceptación
- [ ] Pasan las 3 pruebas unitarias de los 3 casos clínicos obligatorios.
- [ ] Todas las respuestas validan contra `schemas/triage_response.json`."

# T-16
echo "📌 Creando T-16: Documentación Final: README.md del Proyecto y Diagrama de Arquitectura..."
gh issue create \
  --title "T-16 — Documentación Final: README.md del Proyecto y Diagrama de Arquitectura" \
  --label "type: docs,priority: critical" \
  --body "### Descripción
Redactar el `README.md` principal del repositorio según las exigencias del pliego de la hackathon: resumen ejecutivo, arquitectura visual, diagrama del grafo del agente, instrucciones paso a paso para clonar y ejecutar (React + n8n + OCI) y resumen de los 3 casos de demostración.

### Entregables
- Archivo `README.md` en la raíz con badges de tecnologías (ONE, OCI, Gemini, n8n, Python, React).
- Diagrama de arquitectura y flujo del agente en Mermaid y capturas.
- Guía de inicio rápido para los evaluadores.

### Criterios de Aceptación
- [ ] Contiene todas las secciones evaluables requeridas por el pliego.
- [ ] Instrucciones claras que permiten a un tercero levantar el proyecto en 3 comandos.
- [ ] Enlaces funcionales a la documentación en `docs/`."

# T-17
echo "📌 Creando T-17: Guía y Script para Despliegue en OCI Compute VM (Always Free)..."
gh issue create \
  --title "T-17 — Guía y Script para Despliegue en OCI Compute VM (Always Free)" \
  --label "type: cloud-oci,priority: low" \
  --body "### Descripción
Documentar y preparar los scripts para el recurso diferencial opcional: despliegue de los contenedores de n8n y React en una máquina virtual Always Free de Oracle Cloud (Ubuntu/Oracle Linux) con IP pública.

### Entregables
- Guía \`docs/oci_deployment_guide.md\` con comandos para abrir puertos (5678, 8501) en Security Lists e iptables.
- Script de aprovisionamiento \`scripts/deploy_oci_vm.sh\`.

### Criterios de Aceptación
- [ ] Instrucciones claras y probadas para desplegar en OCI Compute.
- [ ] Explica cómo configurar las reglas de ingreso (*Ingress Rules*) en la VCN de Oracle Cloud."

# T-18
echo "📌 Creando T-18: Preparación del Guión y Grabación del Video de Demostración..."
gh issue create \
  --title "T-18 — Preparación del Guión y Grabación del Video de Demostración" \
  --label "type: docs,priority: high" \
  --body "### Descripción
Elaborar el guión de la demostración para el jurado cubriendo los 3 casos de prueba en menos de 5 minutos: 1. Demostración de receta rutinaria a farmacia, 2. Alerta de urgencia crítica TEP, 3. Caso ambiguo resuelto mediante Human-in-the-Loop, y persistencia en buckets de OCI.

### Entregables
- Guión de presentación en \`docs/pitch_demo_script.md\`.
- Checklist de preparación para la grabación o presentación en vivo ante el jurado de Alura/Oracle.

### Criterios de Aceptación
- [ ] El guión cubre todos los puntos de la rúbrica de evaluación en el tiempo establecido.
- [ ] Muestra explícitamente el bucket de OCI Object Storage con los archivos generados."

echo "✅ ¡Todas las GitHub Issues de MediFlow (T-01 a T-18) y sus etiquetas han sido creadas con éxito!"
