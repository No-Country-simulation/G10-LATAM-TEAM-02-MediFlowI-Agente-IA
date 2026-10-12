# Tasks: Normalización y Deserialización Robusta de Respuestas LLM Multiformato

**Input**: Design documents from `/specs/008-llm-response-normalization/`
**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/llm-normalization-contract.yaml)

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Ejecutable en paralelo (archivos independientes, sin dependencias bloqueantes)
- **[Story]**: Historia de usuario a la que pertenece la tarea ([US1], [US2])
- Cada tarea define una acción clara con la ruta exacta del archivo a intervenir.

---

## Phase 1: Setup & Pruebas Unitarias TDD (Test-First)

**Propósito**: Crear los casos de prueba unitarios que reproduzcan la respuesta en bloques de contenido (`AIMessage.content` como lista) antes de implementar el código productivo.

- [X] T001 [P] [US1] Crear suite de pruebas unitarias `backend/tests/test_llm_service.py` con casos de prueba para:
  - Respuesta simple en string (`"hola"`).
  - Respuesta en lista de cadenas (`["bloque 1", "bloque 2"]`).
  - Respuesta en lista de diccionarios estructurados (`[{"type": "text", "text": "{\"paciente\": ...}"}]`).
  - Respuesta con objetos que contienen atributo `.text`.
  - Respuesta vacía o nula.

---

## Phase 2: Foundational (Normalización en Capa de Servicio LLM)

**Propósito**: Garantizar que `LLMService.completar()` retorne incondicionalmente un `str`.

- [X] T002 [US1] Implementar en `backend/app/services/llm_service.py` la rutina de consolidación de fragmentos dentro de `completar()`, deserializando listas y bloques a texto continuo antes de retornar.
- [X] T003 [US1] Ejecutar `pytest backend/tests/test_llm_service.py` y verificar que todas las pruebas pasen en verde.

---

## Phase 3: User Story 1 - Extracción y Clasificación Clínica con Modelos Multimodales (Priority: P1) 🎯 MVP

**Objetivo**: Permitir que el flujo completo de triaje procese respuestas multiformato de LLM sin arrojar errores de atributos tipo `'list' object has no attribute 'strip'`.
**Criterio de Prueba Independiente**: Invocar `node_extraction` y `node_classification` con un servicio LLM simulado que devuelva listas de bloques, verificando la extracción estructurada de diagnósticos y paciente.

- [X] T004 [P] [US1] Añadir pruebas en `backend/tests/test_agent_cases.py` que inyecten un mock de LLM retornando bloques multiformato a `node_extraction` y `node_classification`.
- [X] T005 [US1] Verificar que `node_extraction` en `backend/app/agent/nodes/extraction.py` no falle cuando el servicio entregue respuestas multiformato.

**Punto de Control**: User Story 1 operativa: el servicio LLM no transmite listas a los nodos del grafo.

---

## Phase 4: User Story 2 - Resiliencia Defensiva en Parsers de Nodos (Priority: P2)

**Objetivo**: Blindar defensivamente `_parsear_respuesta` en `extraction.py` y `classification.py` para manejar entradas no-string y limpiar tolerante bloques Markdown.
**Criterio de Prueba Independiente**: Pasar directamente argumentos tipo `list` o strings con bloques ```json con espacios a `_parsear_respuesta` de ambos nodos y constatar que deserializan correctamente.

- [X] T006 [P] [US2] Implementar sanitización defensiva en `_parsear_respuesta` de `backend/app/agent/nodes/extraction.py`:
  - Manejo de entradas tipo `list` y `dict`.
  - Limpieza tolerante de delimitadores Markdown (````json ... ````).
  - Bloque try/except con log estructurado y fallback a `DatosExtraidosState()` seguro.
- [X] T007 [P] [US2] Implementar sanitización defensiva en `_parsear_respuesta` de `backend/app/agent/nodes/classification.py`:
  - Manejo de entradas tipo `list` y `dict`.
  - Limpieza tolerante de delimitadores Markdown (````json ... ````).
  - Bloque try/except con log estructurado y fallback a `ClasificacionState(tipo_documento="Otro", nivel_prioridad="Ambiguo")`.
- [X] T008 [US2] Crear pruebas unitarias específicas para los parsers defensivos en `backend/tests/test_agent_cases.py`.
- [X] T008b [US2] Implementar validador defensivo `@field_validator("edad", mode="before")` en `backend/app/agent/state.py` para parsear cadenas con texto (ej. `"19 años"`) a entero sin error de validación en `PacienteState`.

**Punto de Control**: Los nodos del grafo y los modelos de estado son 100% inmunes a variaciones en la estructura de datos de entrada.

---

## Phase 5: Polish & Verificación E2E de Calidad (Regla de Oro)

**Propósito**: Asegurar cero regresiones en la suite de pruebas completa y validar empíricamente el procesamiento de documentos clínicos.

- [X] T009 Ejecutar la suite completa de pruebas en el backend: `pytest tests/` (100% pasando en verde sin mutar `mediflow_dev`).
- [X] T010 Reprocesar el documento `caso_3_medicina_amigdalitis.pdf` a través de la API y verificar la persistencia con paciente identificado, diagnóstico, CIE-10 y score de confianza > 0.80.
