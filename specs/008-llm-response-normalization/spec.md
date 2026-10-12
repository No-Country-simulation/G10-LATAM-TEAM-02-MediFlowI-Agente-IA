# Feature Specification: Normalización y Deserialización Robusta de Respuestas LLM Multiformato

**Feature Branch**: `008-llm-response-normalization`

**Created**: 2026-10-12

**Status**: Draft

**Input**: User description: "Especificar los requisitos de normalización y deserialización de respuestas del LLM (soporte para bloques de contenido, listas y cadenas de texto)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extracción y Clasificación Clínica con Modelos Multimodales Modernos (Priority: P1)

Como profesional de salud u operador del sistema de triaje hospitalario, quiero que cuando el sistema envíe el texto extraído de un documento clínico al modelo de inteligencia artificial (Google Gemini u OpenAI), la respuesta estructurada sea recibida y parseada correctamente independientemente de si el proveedor la entrega como una cadena de texto simple o como una lista de bloques de contenido, para que el paciente, diagnósticos, códigos CIE-10 y prioridad clínica aparezcan reflejados en la pantalla y se cree el episodio clínico sin errores técnicos de tipo de datos.

**Why this priority**: Es la funcionalidad nuclear del agente de triaje. Si la respuesta del modelo no puede ser deserializada, todo el proceso de IA falla silenciosamente o se deriva a auditoría humana de forma innecesaria con confianza 0%, imposibilitando el triaje autónomo.

**Independent Test**: Procesar un documento clínico con texto completo (ej. PDF o texto directo) bajo un proveedor LLM real o simulado que retorna `AIMessage.content` como lista de fragmentos `[{"type": "text", "text": "..."}]` y verificar que el resultado entregue diagnósticos, entidades y score de confianza altos (> 80%) sin excepciones.

**Acceptance Scenarios**:

1. **Given** un documento clínico procesado por el agente donde el LLM responde con contenido estructurado en forma de lista de partes de texto, **When** el servicio de LLM completa la solicitud, **Then** el servicio debe devolver una cadena de texto consolidada continua (`str`) con todo el contenido generado.
2. **Given** una respuesta de LLM con bloques de texto o delimitadores Markdown (ej. ```json ... ```), **When** los nodos de extracción y clasificación procesan la respuesta, **Then** deben extraer los campos clínicos requeridos (paciente, médico, diagnóstico, CIE-10, hallazgos, prioridad) sin arrojar errores de atributos tipo `'list' object has no attribute 'strip'`.

---

### User Story 2 - Resiliencia Defensiva en Nodos del Grafo ante Respuestas No Canónicas (Priority: P2)

Como desarrollador del sistema y auditor clínico, quiero que los nodos de decisión del grafo LangGraph (`node_extraction` y `node_classification`) posean validaciones defensivas que manejen cualquier estructura de datos devuelta por la capa de integración de LLM, para que una respuesta atípica nunca desestabilice el flujo ni cause un error no controlado que anule los datos clínicos extraídos previamente.

**Why this priority**: Evita regresiones futuras ante actualizaciones de bibliotecas clientes (`langchain-google-genai`, `langchain-core`) donde el formato del mensaje devuelto varíe entre versiones menores.

**Independent Test**: Invocar las funciones de parseo de extracción y clasificación pasando directamente cadenas, listas de diccionarios, listas de strings o estructuras mixtas, validando que todas se transformen consistentemente al modelo Pydantic esperado.

**Acceptance Scenarios**:

1. **Given** una entrada al parser que es una lista de elementos (strings o dicts con clave `text`), **When** se ejecuta el parser de extracción o clasificación, **Then** concatena ordenadamente los fragmentos y deserializa el JSON con éxito.
2. **Given** una entrada nula o vacía, **When** se ejecuta el parser, **Then** retorna un estado por defecto con campos seguros sin lanzar excepciones de Python.

---

### Edge Cases

- ¿Qué sucede cuando el LLM devuelve una lista vacía `[]`? El servicio debe retornar una cadena vacía `""` y los nodos deben tratarla como ausencia de texto sin lanzar excepción de tipo.
- ¿Qué sucede cuando el LLM devuelve una lista que combina diccionarios con clave `text` y objetos o cadenas nativas? La normalización debe extraer el texto de cada elemento de forma segura mediante inspección de tipo (`isinstance(part, dict)`, `hasattr(part, "text")`, `str(part)`).
- ¿Qué sucede si el contenido devuelto contiene bloques de código Markdown con saltos de línea adicionales o espacios antes de los corchetes o llaves JSON? El parser defensivo debe extraer el bloque JSON interno descartando los delimitadores de Markdown de forma tolerante.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El servicio `LLMService.completar` DEBE garantizar que el valor de retorno sea estrictamente un `str`, consolidando listas de fragmentos de contenido devueltas por los clientes LangChain (`AIMessage.content`).
- **FR-002**: Si `AIMessage.content` es una lista de diccionarios que contienen claves como `text`, el servicio DEBE extraer y concatenar en orden el valor de dichas claves.
- **FR-003**: Si `AIMessage.content` es una lista de strings o tipos mixtos, el servicio DEBE convertir cada fragmento a texto y concatenarlos en el orden original.
- **FR-004**: Las funciones de deserialización `_parsear_respuesta` en `extraction.py` y `classification.py` DEBEN incorporar manejo defensivo de tipo, asegurando que cualquier entrada recibida (sea `str`, `list`, o similar) se convierta a una cadena limpia antes de invocar operaciones de formato (`.strip()`).
- **FR-005**: Las funciones de deserialización DEBEN conservar la capacidad de limpiar bloques Markdown circundantes (```json ... ```) sin fallar cuando existan espacios o caracteres de control previos o posteriores.
- **FR-006**: Si el contenido no contiene un JSON válido tras la normalización, DEBE registrarse un log estructurado claro y retornar el estado por defecto sin propagar excepciones no controladas.
- **FR-007**: El modelo de estado `PacienteState` DEBE incorporar validación defensiva en el campo `edad` (`@field_validator(mode="before")`), parseando automáticamente cadenas con sufijos textuales (ej. `"19 años"`, `"19 a"`) a su valor numérico entero (`19`) sin provocar excepciones de validación de Pydantic.

## Key Entities *(include if feature involves data)*

- **ContenidoRespuestaLLM**: Representación del payload devuelto por el proveedor de IA, que puede manifestarse como `str`, `list[str]`, `list[dict[str, Any]]` o instancias de bloques de mensaje de LangChain.
- **TextoNormalizadoLLM**: Cadena unificada de texto UTF-8 resultante de la consolidación de fragmentos, lista para ser analizada por el deserializador JSON.
- **DatosExtraidosState / ClasificacionState**: Modelos de estado del grafo LangGraph que reciben la información clínica estructurada final.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las respuestas de LLM devueltas como listas de bloques de contenido se procesan sin generar excepciones de tipo `'list' object has no attribute 'strip'`.
- **SC-002**: Al procesar documentos clínicos reales con Gemini o proveedores configurados, los campos de paciente, médico, diagnósticos y CIE-10 se extraen y visualizan en la interfaz de usuario con score de confianza mayor a 0.80 en casos claros.
- **SC-003**: El 100% de la suite de pruebas automatizadas existentes del backend pasa en verde (`pytest`) sin fallos ni regresiones.
- **SC-004**: Se incorporan pruebas unitarias y de integración específicas que simulan respuestas multiformato de LLM y verifican su normalización exitosa.

## Assumptions

- Se mantiene el soporte primario para Google Gemini activo en la versión vigente (`gemini-3.5-flash-lite` y `gemini-3.8-flash`) tras la descontinuación de `gemini-2.0-flash` y las restricciones de cuota de `gemini-3.6-flash`, manteniendo fallback para OpenAI.
- Las bibliotecas `langchain-google-genai` y `langchain-core` no requerirán cambios de versión en `pyproject.toml`, solo la adaptación robusta del código de la aplicación.
- No se altera la estructura del grafo LangGraph de 5 nodos ni las firmas de los endpoints REST de `/triage`.
