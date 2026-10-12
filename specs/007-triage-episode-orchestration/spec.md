# Feature Specification: Orquestación de Triaje con Creación y Vinculación Automática de Episodios Clínicos

**Feature Branch**: `dev-wilmer-gulcochia`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: "Orquestación en triage_service.py con creación y vinculación automática de episodios clínicos (Tarea 3.3 / Issue #34): 1) Tras la ejecución del grafo LangGraph en triage_service.py, si el paciente existe o fue resuelto y no cuenta con un episodio activo, crear automáticamente un registro en episodios_clinicos vía episode_repository; 2) Vincular el episodio_id generado a la tabla documentos_triaje; 3) Registrar el evento inmutable DOCUMENTO_ASOCIADO_A_EPISODIO en trazabilidad_eventos mediante AuditRepository; 4) Asegurar resiliencia ante errores de persistencia sin interrumpir la respuesta al cliente; 5) Cobertura de pruebas unitarias y E2E en backend/tests/test_e2e_hospital_flow.py y tests del servicio de triaje."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apertura Automática de Episodio para Paciente Identificado (Priority: P1)

Como personal clínico o de admisión, cuando ingreso un documento médico de un paciente ya registrado en el hospital pero que no tiene una atención activa en curso, requiero que el sistema inicie automáticamente un nuevo episodio de atención clínica vinculado al documento procesado, para que el paciente entre de inmediato al flujo de triaje y atención médica sin requerir pasos manuales adicionales de apertura de ficha.

**Why this priority**: Es el flujo principal y crítico (P1). Garantiza la continuidad asistencial hospitalaria uniendo la extracción autónoma de IA con la trazabilidad del proceso de atención del paciente desde su primer documento.

**Independent Test**: Puede probarse de forma independiente procesando un documento clínico de un paciente registrado sin atenciones abiertas; el sistema debe retornar el triaje completado y confirmar la existencia de un nuevo episodio clínico en estado inicial asociado al documento.

**Acceptance Scenarios**:

1. **Given** un paciente registrado en el sistema que no tiene ningún episodio clínico abierto o activo,
   **When** se procesa un documento médico que coincide con su identidad (por documento de identidad o historia clínica),
   **Then** se crea automáticamente un nuevo episodio clínico con los datos clínicos extraídos (prioridad, motivo de consulta, especialidad sugerida) y el documento queda vinculado a dicho episodio.

2. **Given** un documento procesado que genera un nuevo episodio clínico,
   **When** se consulta la información del documento procesado en el sistema,
   **Then** este incluye la referencia al identificador único del nuevo episodio clínico generado.

---

### User Story 2 - Vinculación a Episodio Clínico Activo Existente (Priority: P2)

Como médico o coordinador clínico, cuando un paciente ya tiene un episodio de atención activo (por ejemplo, en sala de espera, triaje o evaluación general) y se ingresa un documento complementario (como un informe de laboratorio o imagenología), requiero que el documento se asocie directamente al episodio existente sin duplicar la atención del paciente.

**Why this priority**: Evita la fragmentación de la historia de atención y previene atenciones duplicadas o concurrentes para un mismo paciente en el servicio de urgencias o consulta.

**Independent Test**: Puede probarse procesando un nuevo documento para un paciente con un episodio en estado activo; el sistema debe asociar el documento al episodio activo sin crear un nuevo registro de atención.

**Acceptance Scenarios**:

1. **Given** un paciente que cuenta con un episodio clínico activo en curso,
   **When** se procesa un nuevo documento médico para dicho paciente,
   **Then** el sistema vincula el documento al episodio clínico activo existente en lugar de crear uno nuevo.

---

### User Story 3 - Registro Inmutable de Trazabilidad Hospitalaria (Priority: P3)

Como auditor clínico o coordinador hospitalario, requiero que cada vez que un documento de triaje sea vinculado a un episodio clínico (nuevo o existente), se genere un evento inmutable en la bitácora de trazabilidad hospitalaria, para garantizar la rendición de cuentas, auditoría médica y cumplimiento normativo de la atención.

**Why this priority**: Cumple con el principio de trazabilidad inmutable y auditoría médica E2E exigido por la gobernanza hospitalaria y los estándares sanitarios.

**Independent Test**: Puede probarse verificando la bitácora de eventos tras la ingesta de un documento; debe constar el evento `DOCUMENTO_ASOCIADO_A_EPISODIO` con los metadatos correspondientes de documento, paciente y episodio.

**Acceptance Scenarios**:

1. **Given** un documento de triaje que ha sido vinculado a un episodio clínico,
   **When** se completa la operación de vinculación,
   **Then** la bitácora de trazabilidad registra un evento inmutable `DOCUMENTO_ASOCIADO_A_EPISODIO` que contiene los identificadores del documento y del episodio.

---

### User Story 4 - Resiliencia y Continuidad Operativa ante Fallos de Orquestación (Priority: P4)

Como personal asistencial de guardia, si por alguna contingencia técnica temporal o degradación transitoria de un subsistema secundario la vinculación del episodio clínico no puede completarse, requiero que el servicio no bloquee la entrega del análisis de triaje y la extracción de datos al personal clínico, registrando la advertencia para subsanación posterior sin interrumpir la atención del paciente.

**Why this priority**: Asegura la disponibilidad clínica (*High Availability*) en entornos hospitalarios de emergencia, priorizando la entrega de información diagnóstica crítica al médico tratante.

**Independent Test**: Puede probarse simulando una falla controlada en el repositorio de episodios durante el triaje; el servicio debe responder con éxito entregando los resultados de IA extraídos y dejando constancia en los logs operativos del fallo secundario.

**Acceptance Scenarios**:

1. **Given** una contingencia técnica al intentar persistir o vincular el episodio clínico,
   **When** la extracción diagnóstica y clasificación de IA se completaron satisfactoriamente,
   **Then** el sistema responde al usuario con los datos clínicos extraídos sin fallar con error 500, y registra el incidente en el registro de auditoría/logs para su conciliación.

---

### Edge Cases

- **Paciente no resuelto o desconocido**: Si el documento no contiene datos suficientes para resolver un paciente, o no coincide con ningún paciente registrado, el sistema procesa el documento con normalidad sin crear un episodio huérfano, permitiendo la asignación posterior en coordinación.
- **Conflicto de identidad de paciente**: Si el documento presenta un conflicto (por ejemplo, número de documento e historia clínica pertenecen a pacientes distintos), el sistema no crea automáticamente un episodio y preserva la derivación a revisión humana/ambigua.
- **Ingesta concurrente de múltiples documentos para el mismo paciente**: Si ingresan dos documentos simultáneamente para un paciente sin episodio previo, el sistema gestiona la concurrencia garantizando que ambos queden vinculados a una atención coherente sin generar colisiones ni bloqueos.
- **Episodios finalizados previamente**: Si el paciente solo tiene episodios en estado `'cerrado'` o `'atendido'`, se considera que no tiene un episodio activo y se crea un nuevo episodio para la nueva consulta.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El servicio de triaje DEBE verificar la asociación o resolución del paciente tras la ejecución exitosa del análisis de extracción y clasificación.
- **FR-002**: El sistema DEBE determinar si el paciente resuelto posee un episodio clínico activo en el hospital (considerando activos los estados previos al alta o cierre de atención, tales como `'ingresado'`, `'en_triaje'`, `'evaluacion_general'`).
- **FR-003**: El sistema DEBE crear automáticamente un nuevo episodio clínico si el paciente no cuenta con un episodio activo, asignándole un código identificador único de episodio y poblando su prioridad y motivo de consulta a partir de los hallazgos extraídos.
- **FR-004**: El sistema DEBE asociar el identificador del episodio clínico (generado o existente) al registro del documento de triaje.
- **FR-005**: El sistema DEBE registrar un evento inmutable denominado `DOCUMENTO_ASOCIADO_A_EPISODIO` en la bitácora de trazabilidad de eventos hospitalarios cada vez que un documento quede vinculado a un episodio.
- **FR-006**: La orquestación DEBE aislar las fallas secundarias de gestión de episodios, asegurando que ante un error en la capa de episodios no se interrumpa la entrega de los resultados del análisis clínico al cliente solicitante.
- **FR-007**: El flujo hospitalario de extremo a extremo (E2E) DEBE validar la integridad entre la admisión del paciente, la ingesta del documento, la vinculación del episodio clínico y la trazabilidad de auditoría.

### Key Entities

- **Paciente**: Persona sujeta a atención médica, con documento de identidad, número de historia clínica y datos demográficos.
- **Episodio Clínico**: Unidad temporal de atención asistencial que agrupa los actos médicos, documentos y evoluciones desde el ingreso del paciente hasta el cierre de su consulta.
- **Documento de Triaje**: Registro digital o físico procesado (informe médico, analítica, receta) que contiene la extracción clínica, prioridad y enrutamiento sugerido.
- **Evento de Trazabilidad**: Registro inmutable de auditoría que documenta una acción relevante del ciclo de vida clínico con marca de tiempo, usuario y metadatos asociados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los documentos procesados pertenecientes a un paciente identificado sin atención previa cuentan con un episodio clínico generado automáticamente y vinculado.
- **SC-002**: La vinculación automática y el registro de auditoría agregan un tiempo de procesamiento inferior a 150 milisegundos por solicitud de triaje.
- **SC-003**: Cero interrupciones de disponibilidad clínica: el 100% de las solicitudes de triaje con extracción válida entregan respuesta exitosa incluso si ocurre una degradación secundaria en el subsistema de episodios.
- **SC-004**: 100% de las pruebas automatizadas (unitarias, integración y flujo E2E hospitalario) pasan en verde sin modificar ni mutar la base de datos de desarrollo.

## Assumptions

- Se reutiliza el catálogo existente de estados de atención hospitalaria (`'ingresado'`, `'en_triaje'`, `'evaluacion_general'`, `'derivado_especialista'`, `'atendido'`, `'cerrado'`).
- La resolución de pacientes mediante documento de identidad o historia clínica ya está provista por el repositorio de pacientes.
- Los eventos inmutables se registran a través de la infraestructura de auditoría y trazabilidad ya consolidada en el sistema.
- En caso de contingencia técnica en la creación del episodio, se registra una advertencia en los registros del sistema para auditoría y reintento.
