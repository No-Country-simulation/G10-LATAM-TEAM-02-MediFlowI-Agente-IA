# Feature Specification: Integración de Base de Datos Hospitalaria, Episodios Clínicos y Flujo HITL

**Feature Branch**: `001-base-hospitalaria`  
**Created**: 2026-09-30  
**Status**: Implemented  
**Input**: Propuesta de base de datos hospitalaria MediFlow (Hackathon ONE G10), cálculo dinámico de edad, enrutamiento a destinos clínicos y supervisión Human-in-the-Loop.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro de Pacientes con Edad Dinámica y Canales de Admisión (Priority: P1)

Como personal de Admisión (Operador), necesito registrar pacientes capturando su fecha de nacimiento, género binario clínico (`FEMENINO`/`MASCULINO`) y número de teléfono, para que el sistema calcule automáticamente la edad sin requerir actualizaciones periódicas y asigne por defecto `'Admision'` como canal de origen de sus documentos.

**Why this priority**: Es la puerta de entrada de todos los pacientes e historiales al sistema MediFlow.

**Independent Test**: Registrar un paciente con fecha de nacimiento `1990-05-15` y verificar que la API devuelva automáticamente la edad calculada exacta sin almacenar un campo estático desactualizable.

**Acceptance Scenarios**:
1. **Given** un operador en el módulo de pacientes, **When** registra un paciente con fecha de nacimiento válida, **Then** el sistema calcula la edad dinámicamente en tiempo real mediante `EXTRACT(YEAR FROM age(CURRENT_DATE, fecha_nacimiento))` en PostgreSQL.
2. **Given** un nuevo documento clínico ingresado por la interfaz, **When** no se especifica canal emisor, **Then** el sistema asigna automáticamente `'Admision'`.

---

### User Story 2 - Bandeja Designada Human-in-the-Loop para el Coordinador Médico (Priority: P2)

Como Coordinador Médico o Administrador, necesito una pantalla dedicada (`/auditoria`) que liste todos los documentos con score de confianza $< 0.5$ o clasificados como ambiguos, para evaluar discrepancias, reclasificar urgencias y reasignar profesionales médicos con fundamentación clínica obligatoria.

**Why this priority**: Garantiza la seguridad del paciente y el control de calidad médica ante incertidumbre del LLM.

**Independent Test**: Ingresar con rol `COORDINADOR`, acceder a `/auditoria` y emitir una resolución de reclasificación o aprobación en un caso pendiente.

**Acceptance Scenarios**:
1. **Given** un usuario con rol `OPERADOR`, **When** intenta acceder a la consola `/auditoria`, **Then** el sistema bloquea el acceso por RBAC.
2. **Given** un usuario con rol `COORDINADOR` o `ADMINISTRADOR`, **When** accede a `/auditoria`, **Then** visualiza la cola de casos ambiguos y puede registrar un dictamen en `auditorias_coordinacion`.

---

### User Story 3 - Ciclo de Vida Médico Escalable con Especialidades (Priority: P3)

Como Administrador del hospital, necesito registrar profesionales asignando su rol (`ADMINISTRADOR`, `COORDINADOR`, `OPERADOR`) y su especialidad médica (`Medicina General`, `Cardiología`, `Neumonología`), permitiendo derivar episodios clínicos hacia especialistas o a destinos ampliados (`Cola_Emergencia_Medica`, `Cola_Rutina`, `Farmacia_Hospitalaria`).

**Why this priority**: Permite el enrutamiento y la trazabilidad de derivaciones entre medicina general y especialidades.

**Independent Test**: Crear un usuario con especialidad `Cardiología` y rol `COORDINADOR`, verificando que se persista en `usuarios` y se refleje en la tabla de gestión y en los episodios clínicos.

**Acceptance Scenarios**:
1. **Given** un administrador creando un usuario, **When** ingresa rol `COORDINADOR` y especialidad `Neumonología`, **Then** el registro se guarda con éxito y se muestra en la tabla.
2. **Given** una receta médica clasificada por el agente IA, **When** se valida la prescripción, **Then** el sistema permite enrutar hacia `Farmacia_Hospitalaria`.

---

## Edge Cases

- **Fecha de nacimiento futura o nula:** Si la fecha de nacimiento es nula o inválida, el cálculo de edad retorna `null` sin interrumpir la operación clínica.
- **Acceso concurrente a dictámenes HITL:** Si dos coordinadores intentan auditar el mismo documento simultáneamente, la base de datos persiste cada auditoría con su timestamp y actualiza el estado atómicamente.
- **Documentos sin paciente previo:** Si se procesa un documento antes de crear la ficha del paciente, el documento queda disponible en la cola para vinculación manual posterior.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE calcular la edad del paciente en tiempo real a partir de `fecha_nacimiento` sin mantener una columna estática desactualizada en la tabla `pacientes`.
- **FR-002**: La columna `genero` DEBE restringirse a los valores clínicos `'FEMENINO'` y `'MASCULINO'`.
- **FR-003**: El campo de contacto de pacientes DEBE estar normalizado como `numero_telefono`.
- **FR-004**: Los documentos de triaje DEBEN admitir como canal emisor por defecto `'Admision'`.
- **FR-005**: El enum de enrutamiento DEBE incluir `Cola_Emergencia_Medica`, `Cola_Rutina` (Historia Clínica Electrónica), `Farmacia_Hospitalaria` y `Cola_Auditoria_Humana` / `Cola_Revision_Ambigua`.
- **FR-006**: La tabla `usuarios` DEBE incluir la columna `especialidad_medica` y admitir el rol unificado `COORDINADOR`.
- **FR-007**: El acceso a la pantalla de Auditoría Clínica (`/auditoria`) DEBE restringirse exclusivamente a `COORDINADOR` y `ADMINISTRADOR`.
- **FR-008**: La infraestructura de contenedores DEBE etiquetar la imagen del backend con el nombre del proyecto (`mediflow:latest`).

### Key Entities

- **`usuarios`**: Personal médico y administrativo (`id`, `nombres`, `apellidos`, `correo`, `rol`, `especialidad_medica`, `estado`).
- **`pacientes`**: Ficha del paciente (`id`, `numero_documento`, `historia_clinica`, `nombres`, `apellidos`, `fecha_nacimiento`, `genero`, `numero_telefono`).
- **`episodios_clinicos`**: Episodio de atención escalable (`id`, `codigo_episodio`, `paciente_id`, `operador_ingreso_id`, `medico_general_id`, `medico_especialista_id`, `estado_atencion`).
- **`documentos_triaje`**: Documentos clínicos y resultados de triaje IA (`id`, `documento_id`, `episodio_id`, `paciente_id`, `canal_origen`, `prioridad_ia`, `score_confianza`, `destino_principal`).
- **`auditorias_coordinacion`**: Dictámenes del Coordinador en casos HITL (`id`, `episodio_id`, `documento_id`, `coordinador_id`, `decision`, `justificacion_clinica`).
- **`trazabilidad_eventos`**: Bitácora inmutable de ciclo de vida (`id`, `episodio_id`, `documento_id`, `usuario_id`, `evento`, `descripcion`, `metadata`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de consultas a pacientes retornan la edad calculada al día de hoy sin necesidad de tareas por lotes nocturnas.
- **SC-002**: 100% de casos ambiguos o con score $< 0.5$ son derivados a la bandeja del Coordinador (`/auditoria`).
- **SC-003**: 100% de la suite de pruebas unitarias y de integración de backend (109 tests) se ejecuta con resultado exitoso.
- **SC-004**: El despliegue con Docker Compose utiliza la imagen `mediflow:latest` sin requerir configuraciones manuales adicionales.
