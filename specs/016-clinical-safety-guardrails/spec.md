# Feature Specification: Guardrails de Seguridad Clínica: Filtro Fuera de Dominio, Inspección de PDFs Asimétricos y Validación Cruzada de Coherencia

**Feature Branch**: `dev-wilmer-gulcochia`  
**Referencia de Plan de Trabajo**: Tarea 2.10 (`plan de trabajo/PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md`)  
**Issues de GitHub Relacionadas**: [IA-10]  
**Created**: 2026-10-20  
**Status**: Ready for Planning / Implementation  

**Input**: User description: "Guardrails de seguridad clinica filtro fuera de dominio inspeccion de pdfs asimetricos y validacion cruzada de coherencia"

---

## Clarifications

### Session 2026-10-20
- Q: ¿Cuál debe ser el estado operacional (`status`) asignado a los documentos clasificados como fuera de dominio clínico antes de su revisión por el personal de salud? → A: Opción A (`status = "pendiente_auditoria"` y derivación obligatoria a `Cola_Revision_Ambigua` con motivo `"fuera_de_dominio_clinico"` para confirmación y descarte formal por el Coordinador Médico).
- Q: ¿Cuál debe ser el límite máximo de páginas escaneadas o visuales a procesar en un documento PDF multipágina asimétrico? → A: Opción A (Hasta un máximo de 3 páginas clínicas en memoria, preservando el presupuesto Base64 < 350 KB y latencia de respuesta ágil, en consistencia con Spec 015).
- Q: Cuando se detecta una patología de riesgo vital (ej. Infarto o TEP) clasificada erróneamente por el LLM como "Rutina", ¿cuál debe ser la acción de enrutamiento del sistema? → A: Opción A (Penalizar la confianza final a 0.0 y derivar forzosamente a `Cola_Revision_Ambigua` con `requiere_auditoria_humana = true`, `status = "pendiente_auditoria"` y motivo `"discordancia_critica_red_flags"`, respetando la gobernanza HITL de MediFlow).

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filtro Fuera de Dominio (Out-of-Domain Gate) y Prevención de Desvíos (Priority: P1) 🎯 MVP

Como coordinador médico o responsable de triaje hospitalario, cuando un usuario o sistema externo sube un documento que no pertenece al ámbito clínico (por ejemplo, una revista de viajes, un folleto publicitario, un afiche de concierto o un certificado administrativo ajeno a la salud), quiero que el agente identifique que el archivo está fuera de dominio y bloquee estrictamente su derivación a colas clínicas operativas de atención (como Cola de Rutina o Cola de Emergencia), canalizándolo obligatoriamente a revisión humana asistida (HITL) con justificación explícita de documento no clínico.

**Why this priority**: Evita la contaminación de las colas de atención clínica con documentos basura o ajenos. Si un documento publicitario o no médico se clasificara erróneamente como "Rutina" o "Urgente", saturaría innecesariamente la agenda de los facultativos de guardia o el despacho de farmacia con casos inexistentes.

**Independent Test**: Se puede verificar enviando documentos sintéticos no médicos (folleto de viajes, afiche musical, factura comercial) al pipeline de triaje y comprobando que en ningún caso se enrutan a colas de atención médica directa (`Cola_Rutina`, `Cola_Emergencia_Medica`, `Farmacia_Hospitalaria`), sino que se asignan a revisión ambigua con bandera de retención humana activa (`requiere_auditoria_humana = true`).

**Acceptance Scenarios**:

1. **Given** un documento ingresado cuyo contenido es ajeno al ámbito clínico y clasificado como "No_Clinico", "Otro" o "Desconocido", **When** se evalúa la decisión de enrutamiento, **Then** el sistema prohíbe el destino a colas de atención directa y deriva el caso a la cola de revisión ambigua con retención humana obligatoria (`requiere_auditoria_humana = true`).
2. **Given** un documento no médico que por alucinación del modelo sugiera prioridad "Urgente" o "Rutina", **When** el tipo de documento carece de validez clínica ("Otro" o fuera de catálogo médico), **Then** el guardrail de dominio prevalece sobre la sugerencia de prioridad, forzando estado de auditoría y documentando en la justificación que el archivo requiere verificación de pertenencia clínica.
3. **Given** un documento administrativo hospitalario que no es de triaje (ejemplo: comprobante de pago o constancia de asistencia), **When** se procesa en el sistema, **Then** se etiqueta como fuera de flujo clínico y se mantiene en espera de confirmación por el personal coordinador.

---

### User Story 2 - Inspección Página por Página de PDFs Asimétricos e Híbridos (Priority: P2)

Como médico de urgencias o auditor clínico, cuando se recibe un documento PDF multipágina asimétrico (por ejemplo, donde la primera página contiene únicamente una nota de control rutinario o membrete digital, pero la segunda página contiene una imagen escaneada de una orden de urgencia, una receta o un electrocardiograma crítico), quiero que el sistema audite e inspeccione cada página de forma individual y procese visualmente las páginas que carezcan de capa de texto digital, para que ninguna indicación médica urgente o prescripción crítica quede invisibilizada o ignorada.

**Why this priority**: En la práctica clínica real es común grapar o consolidar varios folios en un único PDF donde la primera página es digital pero los anexos clínicos son imágenes escaneadas. Si el sistema solo lee el texto digital global o de la primera página, omitirá información vital que pone en riesgo la vida del paciente.

**Independent Test**: Se puede verificar construyendo un PDF de 2 páginas (página 1 con texto digital de control sano y página 2 con una imagen escaneada de sospecha de infarto o receta médica) y comprobando que el sistema extrae el contenido de ambas páginas, refleja los hallazgos de la página escaneada y no descarta la segunda página por el hecho de haber encontrado texto digital en la primera.

**Acceptance Scenarios**:

1. **Given** un documento PDF multipágina donde la página 1 contiene texto digital nativo y la página 2 contiene una imagen escaneada sin texto seleccionable, **When** se ejecuta la ingesta del documento, **Then** el sistema procesa el texto digital de la página 1 y rasteriza/inspecciona visualmente la página 2, consolidando la información de ambas páginas en el expediente extraído.
2. **Given** una orden de urgencia incrustada como imagen en una página secundaria de un PDF multipágina, **When** culmina la extracción clínica, **Then** los hallazgos críticos de dicha página secundaria forman parte de los datos evaluados para la clasificación de riesgo.
3. **Given** un PDF donde todas las páginas tienen texto digital completo (≥ 50 caracteres cada una), **When** se procesa el archivo, **Then** el sistema mantiene la extracción de texto digital sin consumir recursos de visión artificial innecesarios.

---

### User Story 3 - Validación Cruzada de Coherencia y Matriz de Red Flags Clínicas (Priority: P3)

Como especialista en calidad médica y seguridad del paciente, quiero que el sistema realice una validación cruzada determinista entre los hallazgos clínicos extraídos (patologías graves, diagnósticos presuntivos y códigos de severidad) y el nivel de prioridad asignado por el modelo, de modo que si se detectan afecciones de riesgo vital inminente (tales como infarto de miocardio, tromboembolismo pulmonar, shock, accidente cerebrovascular o hemorragia masiva) pero la clasificación asigna erróneamente un nivel de "Rutina" o baja prioridad, el sistema anule la confianza asignándole valor 0.0 y derive forzosamente el expediente a auditoría médica prioritaria con alerta de discordancia severa.

**Why this priority**: Constituye la última línea de defensa contra fallos catastróficos por alucinación de modelos de lenguaje en casos de vida o muerte (falso negativo de urgencia). Un paciente con tromboembolismo pulmonar o infarto clasificado como "Rutina" podría esperar horas en sala de espera con desenlace fatal.

**Independent Test**: Se puede probar inyectando un resultado clínico que contenga en sus hallazgos o diagnóstico términos de riesgo vital (ej. "Tromboembolismo pulmonar masivo", "Infarto agudo de miocardio con elevación del ST") junto a una clasificación simulada de "Rutina", comprobando que el puntaje de confianza se desploma a `0.0`, el caso se marca con discordancia clínica crítica y se enruta de inmediato a revisión obligatoria con requerimiento de intervención humana.

**Acceptance Scenarios**:

1. **Given** un expediente clínico cuyos hallazgos o diagnósticos incluyen términos o códigos pertenecientes a la matriz de señales de alarma de riesgo vital (*Red Flags*), **When** la clasificación asignada por el componente inteligente es "Rutina", **Then** el guardrail de coherencia semántica detecta la discordancia grave, reduce el puntaje de confianza final a 0.0 y activa la retención para auditoría médica prioritaria.
2. **Given** una discordancia clínica crítica detectada entre diagnóstico grave y prioridad rutina, **When** se genera el resultado de triaje, **Then** se registra en los metadatos y en la justificación de auditoría la causa exacta: `"discordancia_critica_red_flags"`, detallando el hallazgo de riesgo omitido.
3. **Given** un documento cuyos hallazgos graves son clasificados correctamente como "Urgente", **When** se evalúa la consistencia clínica, **Then** el guardrail valida la concordancia positiva y preserva la calificación de confianza normal sin penalizaciones.

---

### Edge Cases

- **Documento mixto publicitario con términos médicos aislados**: Un folleto comercial de una farmacia o un anuncio de seguros médicos puede mencionar palabras como "salud" o "médico", pero no constituye un acto médico; el filtro fuera de dominio debe evaluar la estructura del documento y enviarlo a auditoría ambigua si no es un informe, receta o estudio formal.
- **PDF multipágina con páginas totalmente en blanco**: Páginas intermedias o finales vacías deben ser ignoradas limpiamente sin generar fallos ni activar procesos de visión artificial redundantes.
- **Términos de riesgo vital en contexto negativo o descartado**: Si el documento consigna "Se descarta infarto agudo de miocardio" o "Sin signos de tromboembolismo pulmonar", el guardrail de red flags debe contemplar el contexto de negación para no generar falsas discordancias cuando sea posible, o ante la duda derivar con confianza moderada a revisión humana.
- **Límite de páginas para análisis visual en PDFs híbridos**: En PDFs asimétricos extensos, se debe auditar hasta un límite seguro de páginas clínicas útiles (hasta un máximo de 3 páginas en memoria) para garantizar la celeridad del triaje hospitalario y respetar el presupuesto Base64 (< 350 KB).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE evaluar el tipo de documento clasificado antes de permitir el enrutamiento a colas operativas de rutina o emergencia.
- **FR-002**: Si el tipo de documento es catalogado como "No_Clinico", "Otro", "Desconocido" o no corresponde a una categoría clínica formal, el sistema DEBE prohibir su enrutamiento a `Cola_Rutina` y a `Cola_Emergencia_Medica`.
- **FR-003**: Todo documento catalogado fuera de dominio DEBE ser derivado obligatoriamente a `Cola_Revision_Ambigua` con la propiedad `requiere_auditoria_humana = true`, estado operacional `status = "pendiente_auditoria"` y motivo de retención `"fuera_de_dominio_clinico"`, permitiendo su descarte o reasignación formal por el Coordinador Médico.
- **FR-004**: En la fase de ingesta de documentos PDF, el sistema DEBE evaluar cada página de forma individual para identificar la presencia de texto digital seleccionable vs. contenido exclusivamente visual/escaneado.
- **FR-005**: Si en un PDF multipágina se detecta que una o más páginas carecen de texto digital suficiente (< 50 caracteres) o contienen imágenes clínicas incrustadas sin texto nativo, el sistema DEBE rasterizar y procesar visualmente hasta un máximo de 3 páginas clínicas en memoria, consolidando su contenido con el texto de las páginas digitales.
- **FR-006**: La consolidación de texto y hallazgos provenientes de páginas digitales y páginas escaneadas DEBE realizarse en memoria antes de la fase de extracción clínica, asegurando que ninguna prescripción o diagnóstico anexo sea descartado.
- **FR-007**: El sistema DEBE disponer de una matriz determinista de señales de alarma clínica (*Red Flags*) que incluya patologías y términos de riesgo vital (ej. infarto agudo de miocardio / IAM, tromboembolismo pulmonar / TEP, shock séptico/cardiogénico, paro cardiorrespiratorio, hemorragia masiva / exanguinante, accidente cerebrovascular / ACV / ictus, neumotórax a tensión).
- **FR-008**: El componente de calibración de confianza DEBE comparar los hallazgos clave, el diagnóstico principal y el código sugerido contra la matriz de *Red Flags* clínicas.
- **FR-009**: Si se detecta al menos un elemento de la matriz de *Red Flags* y la prioridad asignada es "Rutina" o no urgente, el sistema DEBE penalizar de inmediato el puntaje de confianza final a `0.0`.
- **FR-010**: Toda penalización por discordancia crítica DEBE provocar que el documento caiga a puntaje de confianza 0.0 (por debajo del umbral de 0.75), forzando su enrutamiento a `Cola_Revision_Ambigua` con `requiere_auditoria_humana = true`, estado operacional `status = "pendiente_auditoria"` y motivo `"discordancia_critica_red_flags"` para intervención médica prioritaria.
- **FR-011**: El sistema DEBE registrar en los metadatos de auditoría y en los eventos de trazabilidad el motivo específico de la retención y procesamiento: `"fuera_de_dominio_clinico"`, `"documento_asimetrico_detectado"` o `"discordancia_critica_red_flags"`.
- **FR-012**: Las decisiones tomadas por los guardrails deterministas DEBEN prevalecer sobre las respuestas generadas por los modelos de lenguaje probabilísticos.

---

### Key Entities

- **MatrizRedFlagsClinicas**: Catálogo determinista inmutable de términos diagnósticos, sintomatología de alarma y códigos CIE-10 que representan riesgo vital inmediato para el paciente.
- **PaginaEvaluada**: Estructura que describe las características de cada folio de un documento (índice de página, longitud de texto digital detectado, presencia de imágenes incrustadas y método de extracción aplicado).
- **EvaluacionCoherenciaClinica**: Resultado de la validación cruzada entre la severidad clínica intrínseca de los hallazgos y el nivel de prioridad asignado, con indicador de concordancia, discordancia severa y penalización de confianza aplicada.
- **GuardrailDecision**: Registro de intervención determinista que ajusta el flujo de enrutamiento o el estado de auditoría ante transgresiones de seguridad clínica.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los documentos clasificados como no clínicos o ajenos al dominio de salud son retenidos para revisión humana, con una tasa de fuga a colas operativas de rutina o emergencia de exactamente **0%**.
- **SC-002**: En el 100% de los PDFs multipágina asimétricos (combinación de texto digital y páginas escaneadas), el contenido clínico de las páginas escaneadas es capturado e integrado en el análisis de triaje sin omisión de folios.
- **SC-003**: En casos sintéticos de prueba con discordancia deliberada entre patología de riesgo vital (matriz de *Red Flags*) y prioridad "Rutina", el 100% de los casos son interceptados con puntaje de confianza final reducido a **0.0** y derivados a auditoría asistida.
- **SC-004**: La ejecución acumulada de los tres guardrails de seguridad añade menos de 100 ms de sobrecarga al tiempo total de procesamiento local del expediente.

---

## Assumptions

- Se asume que el catálogo de *Red Flags* se mantiene enfocado en patologías y síntomas de riesgo vital inminente (prioridad 1 / reanimación / emergencia) para evitar sobrefrenar casos de rutina con síntomas leves o crónicos.
- Se asume que para documentos no clínicos ("Otro"), el enrutamiento a auditoría permite al personal coordinador descartar el archivo o reasignarlo si se tratara de un formato clínico atípico.
- Se asume que la inspección página por página de PDFs respeta el límite máximo de memoria y tamaño de imágenes definido en las políticas de optimización del sistema.
