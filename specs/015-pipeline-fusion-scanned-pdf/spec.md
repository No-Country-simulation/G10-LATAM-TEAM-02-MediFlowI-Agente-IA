# Feature Specification: Actualización y extensión de Pipeline Fusion (Tarea 2.9 / IA-09) para documentos PDF escaneados e híbridos

**Feature Branch**: `dev-wilmer-gulcochia`  
**Referencia de Plan de Trabajo**: Tarea 2.9 (`plan de trabajo/PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md`)  
**Issues de GitHub Relacionadas**: [IA-09] #69 / PR #77  
**Created**: 2026-10-20  
**Status**: Ready for Planning / Implementation  

**Input**: User description: "Actualización y extensión de Pipeline Fusion (Tarea 2.9 / IA-09) para documentos PDF escaneados e híbridos: Regla 1 si el PDF tiene texto digital suficiente (>= 50 caracteres clínicos útiles) se extrae directamente con PyMuPDF en 0.01s sin rasterizar ni consumir visión; Regla 2 si el texto digital es insuficiente (< 50 caracteres o solo título/membrete) se detecta que el contenido clínico reside en la imagen y se activa de inmediato Pipeline Fusion rasterizando páginas en memoria con PyMuPDF a JPEG optimizado < 350 KB ejecutando pase único con Gemini Vision en < 7s reutilizando backend/app/agent/fusion.py, image_optimizer.py y liberando documento_base64 en LangGraph."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discriminación Inteligente y Extracción Inmediata de PDF con Texto Digital (Priority: P1) 🎯 MVP

Como evaluador o médico hospitalario en la consola de triaje, cuando ingreso un documento PDF con capa de texto digital seleccionable suficiente (≥ 50 caracteres clínicos útiles), quiero que el sistema extraiga dicho texto directamente en milisegundos sin rasterizar ni invocar llamadas de visión artificial innecesarias, para garantizar la máxima fidelidad tipográfica, cero riesgo de alucinación en dosis o diagnósticos y una respuesta instantánea.

**Why this priority**: Es el caso más frecuente en informes de laboratorio, epicrisis de software médico y recetas electrónicas; procesar el texto vectorial nativo ahorra cuota de API, evita errores de OCR y entrega resultados en menos de 1 segundo.

**Independent Test**: Se puede verificar de forma independiente enviando un PDF clínico digital sintético (ej. informe médico de 200 palabras) al nodo de ingesta y comprobando que `metodo_extraccion == "TEXT_EXTRACTION"`, la latencia de ingesta es inferior a 50 ms y no se emite ninguna llamada a Gemini Vision.

**Acceptance Scenarios**:

1. **Given** un documento PDF clínico recibido que posee capa de texto digital con longitud `len(texto_digital.strip()) >= 50`, **When** se ejecuta el nodo de ingesta, **Then** el sistema extrae el texto vectorial directamente mediante `PyMuPDF` asignando `metodo_extraccion = "TEXT_EXTRACTION"` y avanza a los nodos siguientes sin rasterizar imágenes ni invocar el LLM de visión.
2. **Given** un PDF digital con texto clínico y logotipo/gráfico incrustado, **When** el texto digital contiene la anamnesis y diagnóstico, **Then** el sistema prioriza el texto vectorial puro, evitando latencias de red y consumo de tokens de visión.

---

### User Story 2 - Activación Automática de Pipeline Fusion en PDFs Escaneados o con Texto Insuficiente (Priority: P2)

Como médico de urgencias o coordinador de triaje, cuando cargo un PDF escaneado (o un PDF que contiene únicamente un membrete/título de < 50 caracteres y el contenido médico real está en una imagen incrustada de una receta o estudio), quiero que el sistema detecte que el texto digital es insuficiente y active automáticamente Pipeline Fusion en memoria, para obtener la transcripción, extracción y clasificación en un único viaje de red con Gemini Vision en menos de 7 segundos.

**Why this priority**: En la práctica hospitalaria, una gran proporción de recetas y órdenes son escaneos o fotografías pegadas dentro de un PDF. Sin esta optimización, estos documentos tardaban entre 25 y 45 segundos o dependían de OCRs locales lentos e inexactos.

**Independent Test**: Se puede probar enviando un PDF escaneado (sin capa de texto o con solo "Hospital Central") y verificando que el sistema rasteriza la página en memoria, optimiza a JPEG < 350 KB, inyecta `ContextoTriaje`, ejecuta `_PROMPT_VISION_FUSION` y completa los nodos de extracción y clasificación mediante cortocircuito sin llamadas remotas redundantes.

**Acceptance Scenarios**:

1. **Given** un documento PDF recibido cuya capa de texto digital es menor a 50 caracteres (`len(texto_digital.strip()) < 50`), **When** se ejecuta el nodo de ingesta con contexto de fusión, **Then** el sistema detecta la condición de PDF escaneado, rasteriza en memoria sus páginas clínicas clave a JPEG, las comprime con `image_optimizer.py` (< 350 KB) y ejecuta la llamada única de Gemini Vision vía `fusion.py`.
2. **Given** una ejecución de Pipeline Fusion sobre un PDF escaneado con respuesta JSON válida, **When** el flujo continúa hacia `extraction` y `classification`, **Then** ambos nodos detectan los datos precalculados en `ContextoTriaje` y aplican cortocircuito inmediato (tiempo < 1 ms) validando CIE-10 y reglas clínicas sin segundas o terceras llamadas al LLM.

---

### User Story 3 - Saneamiento de Memoria en LangGraph y Resiliencia Clínica (Priority: P3)

Como administrador de infraestructura y arquitecto de software, quiero que el procesamiento de PDFs escaneados y digitales libere inmediatamente `documento_base64 = None` al culminar el nodo de ingesta, reutilice el singleton del grafo compilado y degrade de forma limpia hacia auditoría médica asistida (`FALLBACK_AUDIT`) en caso de error, para garantizar la estabilidad de memoria del servidor y la continuidad del flujo hospitalario.

**Why this priority**: Los PDFs rasterizados pueden generar decenas de megabytes en memoria base64; mantenerlos en el estado de LangGraph saturaría la RAM del servidor FastAPI ante múltiples solicitudes concurrentes.

**Independent Test**: Procesar solicitudes concurrentes con PDFs de gran volumen y verificar que `state["documento_base64"] is None` en todos los nodos posteriores, que no quedan archivos temporales en disco y que ante un PDF corrupto el sistema responde HTTP 200 con derivación a `pendiente_auditoria` sin caer en bucles.

**Acceptance Scenarios**:

1. **Given** un documento PDF procesado exitosamente por cualquier vía (digital o escaneada), **When** finaliza `node_ingestion`, **Then** el diccionario retornado contiene `"documento_base64": None`, purgando la carga útil binaria del grafo de estados de LangGraph.
2. **Given** un PDF escaneado corrupto o un fallo irrecuperable en la respuesta de Gemini Vision, **When** se captura la excepción en el nodo de ingesta, **Then** el sistema asigna `metodo_extraccion = "FALLBACK_AUDIT"`, registra el error de forma segura y deriva el caso a revisión humana médica sin bloquear el servicio.

---

### Edge Cases

- **PDF con caracteres invisibles o basura tipográfica**: Si un PDF escaneado contiene texto OCR previo de mala calidad con caracteres de control o espacios vacíos, la verificación `len(texto_digital.strip()) < 50` asegura que no se tome como texto digital válido y se derive a Pipeline Fusion.
- **PDF multipágina escaneado**: La rasterización se limita a un máximo de 3 páginas clínicas en memoria para respetar el presupuesto de red y tamaño Base64 (< 350 KB por imagen).
- **Procesamiento 100% en memoria**: Todo el rasterizado de páginas mediante `PyMuPDF (fitz)` y compresión con `Pillow` opera en buffers `io.BytesIO`, prohibiendo la creación de archivos temporales en `/tmp` o en disco.
- **Concurrencia y aislamiento**: Cada solicitud dispone de su propia instancia de `ContextoTriaje`, evitando colisiones de datos de pacientes o resultados cruzados al reutilizar el grafo compilado en caché.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE inspeccionar la capa de texto vectorial de todo documento PDF recibido mediante `PyMuPDF` (`fitz`) en el nodo de ingesta.
- **FR-002**: Si la longitud del texto digital extraído es mayor o igual a 50 caracteres (`len(texto_digital.strip()) >= 50`), el sistema DEBE adoptar inmediatamente dicho texto, asignar `metodo_extraccion = "TEXT_EXTRACTION"` y omitir cualquier rasterizado o llamada a visión artificial.
- **FR-003**: Si la longitud del texto digital extraído es menor a 50 caracteres (`len(texto_digital.strip()) < 50`), el sistema DEBE catalogar el archivo como PDF escaneado/híbrido y activar automáticamente la ruta de Pipeline Fusion.
- **FR-004**: Para PDFs escaneados, el sistema DEBE rasterizar en memoria las páginas del documento a imágenes JPEG utilizando `PyMuPDF` (`fitz.Matrix(1.5, 1.5)` o equivalente a 100-120 DPI) sin escribir archivos en disco.
- **FR-005**: Las imágenes rasterizadas DEBEN optimizarse mediante `backend/app/services/image_optimizer.py`, garantizando auto-orientación, normalización RGB, reducción a máximo 1280 px y un payload Base64 estrictamente inferior a 350,000 bytes.
- **FR-006**: La ingesta de PDFs escaneados DEBE invocar el pase único de Gemini Vision reutilizando `_PROMPT_VISION_FUSION` y poblando el modelo estructurado `ResultadoFusionVision` en `ContextoTriaje`.
- **FR-007**: Los nodos `extraction` y `classification` DEBEN reutilizar los datos clínicos precalculados en `ContextoTriaje` cuando provengan de un PDF escaneado procesado por fusión, validando el catálogo CIE-10 y la identidad del paciente en memoria sin realizar llamadas LLM adicionales.
- **FR-008**: Al culminar el nodo de ingesta (tanto en flujo digital como en fusión escaneada), el sistema DEBE retornar obligatoriamente `"documento_base64": None` para liberar la memoria en LangGraph.
- **FR-009**: Ante fallos en la rasterización o en la respuesta de visión de un PDF escaneado, el sistema DEBE registrar el error y retornar `metodo_extraccion = "FALLBACK_AUDIT"` derivando el expediente a revisión asistida (HITL) sin reintentos costosos redundantes.
- **FR-010**: El grafo LangGraph DEBE mantenerse cacheado como singleton mediante `@functools.cache` en `backend/app/agent/graph.py` asegurando aislamiento estricto por solicitud mediante `ContextoTriaje`.

---

### Key Entities

- **ContextoTriaje**: Entidad de contexto por solicitud (`backend/app/agent/fusion.py`) que vincula el cliente LLM y el resultado temporal de la fusión (`ResultadoFusionVision`), permitiendo cortocircuitar nodos subsiguientes sin mutar el esquema canónico de `AgentState`.
- **PDFEscaneadoPayload**: Representación en memoria (`io.BytesIO`) de las páginas rasterizadas y optimizadas de un documento PDF, tipada y limitada en bytes para su envío a Gemini Vision.
- **ResultadoFusionVision**: Modelo Pydantic v2 que consolida en un único JSON `texto_extraido`, `datos_extraidos` (paciente, diagnóstico, CIE-10, medicamentos) y `clasificacion` (prioridad, especialidad, justificación).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los PDFs con texto digital suficiente (≥ 50 caracteres) completan la fase de ingesta en menos de 100 ms sin consumir llamadas al modelo de visión.
- **SC-002**: El 100% de los PDFs escaneados procesados por Pipeline Fusion completan la transcripción, extracción y clasificación en una latencia de percentil 95 (**p95 < 8.0 segundos**) en condiciones normales de red.
- **SC-003**: El tamaño del payload Base64 generado para las imágenes de PDFs escaneados no supera en ningún caso los 350,000 bytes (350 KB).
- **SC-004**: Cero fugas de memoria: `state.documento_base64` se libera en el 100% de las ejecuciones tras la ingesta.
- **SC-005**: La suite de pruebas de `tests/test_pipeline_fusion.py` y `tests/test_pipeline_fusion_benchmark.py` aprueba con el 100% de tests en verde en `pytest`.

---

## Assumptions

- Se reutiliza la infraestructura ya consolidada en `develop` proveniente del PR #77 (`fusion.py`, `image_optimizer.py`, `ContextoTriaje`).
- Las páginas rasterizadas en memoria de un PDF escaneado son procesadas de manera análoga a un archivo `IMAGEN` (JPEG/PNG/WebP), unificando el backend visual de LangGraph.
- El almacenamiento canónico de los archivos físicos originales permanece inalterado en PostgreSQL y el disco local (`backend/storage/recibidos/`), siendo preservado por `TriageService`.
- No se requiere crear una tarea 2.10 adicional; esta especificación actualiza y completa al 100% el alcance de la Tarea 2.9 ([IA-09]) del plan de trabajo.
