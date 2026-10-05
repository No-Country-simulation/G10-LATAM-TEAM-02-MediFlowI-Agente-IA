# Feature Specification: Repositorio Asíncrono episode_repository para Gestión de Episodios Clínicos

**Feature Branch**: `003-episode-repository` (desarrollado en rama de trabajo `dev-wilmer-gulcochia`)  
**Created**: 2026-10-05  
**Status**: Completed (100% Tests Passed)  
**Input**: Implementar repositorio asíncrono episode_repository con asyncpg para gestionar la tabla episodios_clinicos  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Creación y Registro Atómico de Episodios Clínicos (Priority: P1)

Como operador de admisión, médico o servicio del backend de MediFlow, quiero crear y registrar nuevos episodios clínicos asociados a un paciente con su motivo de consulta, nivel de prioridad y operador responsable para iniciar formalmente el ciclo de atención del paciente.

**Why this priority**: Es el punto de entrada para toda la trazabilidad y la asignación clínica en el hospital; sin la creación de episodios no se pueden asociar documentos de triaje ni derivaciones.

**Independent Test**: Invocar la función `create_episode(data)` pasando los datos del paciente y motivo de consulta, verificando que devuelva el registro creado con su identificador UUID, código de episodio generado y estado inicial `ingresado`.

**Acceptance Scenarios**:
1. **Given** datos válidos de admisión con `paciente_id` y `operador_ingreso_id`, **When** se invoca `create_episode(...)`, **Then** se persiste el registro en PostgreSQL, se auto-genera un `codigo_episodio` único si no se proporciona (ej. `EP-YYYYMMDD-XXXX`), y el estado por defecto es `ingresado`.
2. **Given** un intento de registro sin disponibilidad en el pool de base de datos, **When** se ejecuta la operación, **Then** el repositorio eleva `DatabaseUnavailableError` de manera controlada y estructurada.

---

### User Story 2 - Consulta Detallada y Agregada de Episodios (Priority: P2)

Como médico general, especialista o coordinador hospitalario, quiero consultar un episodio por su ID o por su código único obteniendo toda la información demográfica del paciente (con edad calculada) y los médicos asignados para tener el contexto clínico completo de forma inmediata.

**Why this priority**: Evita la dispersión de datos y permite a la interfaz clínica y a los servicios de IA contar con la información consolidada en una sola llamada.

**Independent Test**: Invocar `get_episode_by_id(episode_id)` o `get_episode_by_code(codigo_episodio)` y validar que retorne el diccionario completo proyectado desde `v_episodios_detalle`.

**Acceptance Scenarios**:
1. **Given** un ID de episodio existente, **When** se llama a `get_episode_by_id(episode_id)`, **Then** retorna el detalle completo unificado proveniente de `v_episodios_detalle` incluyendo `paciente_nombre_completo`, `paciente_edad`, y datos de profesionales asignados.
2. **Given** un ID de episodio inexistente, **When** se llama a `get_episode_by_id(...)`, **Then** retorna `None` sin arrojar errores.

---

### User Story 3 - Transición de Estados, Asignación y Listado Filtrado (Priority: P3)

Como coordinador médico o especialista, quiero actualizar el estado del episodio (`ingresado` -> `en_triaje` -> `atendido` -> `derivado`), asignar médicos especialistas o generales, y listar episodios filtrando por estado o prioridad para gestionar la bandeja de trabajo clínico.

**Why this priority**: Permite coordinar la carga hospitalaria, seguir el avance de los pacientes y derivar casos entre niveles de atención.

**Independent Test**: Ejecutar `update_episode_status(episode_id, 'en_triaje')`, `assign_doctor(episode_id, ...)` y `list_episodes(estado='en_triaje')` comprobando las actualizaciones y filtros.

**Acceptance Scenarios**:
1. **Given** un episodio en estado `ingresado`, **When** se ejecuta `update_episode_status(episode_id, 'en_triaje')`, **Then** el campo `estado_atencion` se actualiza, el timestamp `updated_at` se renueva y la función retorna `True`.
2. **Given** múltiples episodios en la base de datos, **When** se llama a `list_episodes(estado='en_triaje', limit=50)`, **Then** devuelve la lista de episodios que cumplen con dicho criterio ordenados por prioridad y fecha de creación.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El módulo `episode_repository.py` DEBE encapsular todas las operaciones de acceso a datos para la tabla `episodios_clinicos` y la vista `v_episodios_detalle`.
- **FR-002**: La función `create_episode(data: dict[str, Any]) -> dict[str, Any]` DEBE insertar el nuevo episodio y devolver el registro creado en formato diccionario serializable.
- **FR-003**: La función `get_episode_by_id(episode_id: UUID | str) -> dict[str, Any] | None` DEBE consultar la vista `v_episodios_detalle` para devolver el registro agregado.
- **FR-004**: La función `get_episode_by_code(codigo_episodio: str) -> dict[str, Any] | None` DEBE permitir la búsqueda unificada por el código clínico único.
- **FR-005**: La función `update_episode_status(episode_id: UUID | str, nuevo_estado: str) -> bool` DEBE actualizar el estado de atención y renovar `updated_at = NOW()`.
- **FR-006**: La función `assign_doctor(episode_id: UUID | str, medico_id: UUID | str, rol: str, especialidad: str | None = None) -> bool` DEBE permitir asignar médico general (`medico_general_id`) o especialista (`medico_especialista_id`, `especialidad_requerida`).
- **FR-007**: La función `list_episodes(estado: str | None = None, nivel_prioridad: str | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]` DEBE retornar la lista paginada y filtrada.
- **FR-008**: Todas las operaciones DEBEN verificar la disponibilidad del pool (`_require_pool()`) y capturar fallos elevando `DatabaseUnavailableError`.
- **FR-009**: Todos los registros y operaciones críticas DEBEN emitir logs estructurados con `structlog`.

---

## Success Criteria

1. **Integridad de Datos**: 100% de los episodios creados conservan su trazabilidad con identificadores únicos UUID y códigos de episodio.
2. **Resiliencia Operativa**: Cualquier interrupción de conexión con la base de datos es interceptada sin generar caídas de la aplicación (0% crashes no controlados).
3. **Cobertura de Pruebas**: 100% de pruebas unitarias en verde en `backend/tests/test_episode_repository.py` utilizando simulación asíncrona aislada (mocks/fakes de `asyncpg`).

---

## Edge Cases

- **Valores UUID en formato string o UUID object**: Las funciones deben aceptar tanto instancias `UUID` como `str` válidos, convirtiéndolos adecuadamente.
- **Código de episodio duplicado**: Manejo seguro de violaciones de unicidad retornando error controlado o excepción descriptiva.
- **Transición a estado no válido**: Validación o control de estados permitidos (`ingresado`, `en_triaje`, `atendido`, `derivado`, `cerrado`).
