# Feature Specification: Endpoints REST de Coordinación y Auditoría Médica (HITL)

**Feature Branch**: `006-coordination-audit-api`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: "Implementar endpoints REST de Auditoría y Coordinación Médica en /api/v1/coordination (Tarea 3.2 / Issue #33): 1) Endpoint GET /api/v1/coordination/pending para bandeja de triajes pendientes de HITL con filtros opcionales por especialidad y tiempo de espera; 2) Endpoint POST /api/v1/coordination/resolve/{documento_id} para resolución médica HITL con dictamen (aprobar, reclasificar, rechazar), reasignación y justificación clínica; 3) Integración inmutable con AuditRepository (auditorias_coordinacion y trazabilidad_eventos); 4) Seguridad RBAC estricta con Depends(require_roles("COORDINADOR", "ADMINISTRADOR")) retornando 403 para otros roles; 5) Esquemas Pydantic v2, sincronización con OpenAPI y suite completa de tests en backend/tests/test_coordination_api.py."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bandeja de Casos Pendientes de Auditoría HITL (Priority: P1)

Como Médico Coordinador del hospital, necesito consultar la bandeja de triajes clínicos que fueron marcados para revisión humana (*Human-in-the-Loop* o HITL) debido a baja confianza o ambigüedad diagnóstica, con la capacidad de filtrar por especialidad médica y ordenar o filtrar por tiempo de espera, para priorizar y atender oportunamente los casos más urgentes.

**Why this priority**: Es el punto de entrada clínico fundamental para que los coordinadores visualicen el trabajo pendiente acumulado y garanticen la seguridad del paciente antes de derivaciones hospitalarias.

**Independent Test**: Se puede probar de forma independiente consultando `GET /api/v1/coordination/pending` con un usuario autenticado con rol `COORDINADOR` y verificando que devuelve la lista de documentos con estado pendiente de auditoría y metadatos clínicos asociados, respondiendo con datos vacíos o paginados según corresponda.

**Acceptance Scenarios**:

1. **Given** un Médico Coordinador autenticado con token JWT válido, **When** solicita `GET /api/v1/coordination/pending`, **Then** el sistema responde con HTTP 200 y una lista de triajes pendientes de revisión con su tiempo de espera, nivel de urgencia, confianza de la IA y diagnóstico preliminar.
2. **Given** un Médico Coordinador autenticado, **When** solicita `GET /api/v1/coordination/pending?especialidad=CARDIOLOGIA&minutos_espera=30`, **Then** el sistema retorna únicamente los casos asociados a dicha especialidad cuyo tiempo de espera supere los 30 minutos.
3. **Given** un usuario autenticado con rol `OPERADOR` o `MEDICO` no coordinador, **When** intenta acceder a `GET /api/v1/coordination/pending`, **Then** el sistema rechaza la solicitud con HTTP 403 Forbidden.

---

### User Story 2 - Resolución y Dictamen Clínico de Triaje HITL (Priority: P1)

Como Médico Coordinador, necesito registrar formalmente la resolución de un triaje en revisión mediante una decisión clínica obligatoria (`aprobar`, `reclasificar` o `rechazar`), especificando la justificación clínica médica y, en caso de reclasificación, el nuevo destino/especialidad y prioridad, para que el documento continúe su flujo hospitalario de manera auditada.

**Why this priority**: Cierra el ciclo de *Human-in-the-Loop* al permitir que el criterio médico humano valide o rectifique las decisiones de la IA, persistiendo la decisión en la bitácora inmutable.

**Independent Test**: Se puede probar enviando un `POST /api/v1/coordination/resolve/{documento_id}` con un cuerpo de resolución válido por un `COORDINADOR` y validando que el registro se guarda en `auditorias_coordinacion` y genera un evento de trazabilidad inmutable.

**Acceptance Scenarios**:

1. **Given** un documento en estado pendiente de auditoría, **When** el Coordinador envía un `POST /api/v1/coordination/resolve/{documento_id}` con decisión `aprobar` y justificación clínica de al menos 10 caracteres, **Then** el sistema persiste el dictamen, actualiza el estado del triaje a aprobado, registra el evento de trazabilidad y retorna HTTP 200 con el resumen del dictamen.
2. **Given** un triaje ambiguo, **When** el Coordinador envía `POST /api/v1/coordination/resolve/{documento_id}` con decisión `reclasificar`, nueva categoría destino `Farmacia_Hospitalaria` y justificación clínica, **Then** el sistema actualiza la clasificación y registra la auditoría con la reasignación.
3. **Given** una solicitud de resolución donde la justificación clínica está vacía o ausente, **When** el Coordinador envía la solicitud, **Then** el sistema la rechaza con HTTP 422 Unprocessable Entity exigiendo una justificación clínica válida.

---

### User Story 3 - Trazabilidad y Consulta de Eventos de Auditoría (Priority: P2)

Como Auditor Hospitalario o Coordinador, necesito consultar el historial inmutable de eventos y dictámenes clínicos asociados a un documento específico, para reconstruir la cadena de decisiones tomadas por el agente de IA y los profesionales médicos.

**Why this priority**: Garantiza el cumplimiento normativo hospitalario, la auditoría médico-legal y la transparencia en las decisiones tomadas durante el triaje.

**Independent Test**: Se prueba consultando `GET /api/v1/coordination/audit/{documento_id}` o listando eventos de trazabilidad del documento, comprobando que se devuelven todos los registros históricos cronológicos de PostgreSQL.

**Acceptance Scenarios**:

1. **Given** un documento que ha pasado por procesamiento de IA y resolución humana, **When** un `COORDINADOR` o `ADMINISTRADOR` consulta los eventos del documento, **Then** el sistema responde con HTTP 200 conteniendo la cronología completa de eventos y dictámenes.

---

### Edge Cases

- **Documento inexistente**: Cuando se intenta resolver un `documento_id` que no existe en `documentos_triaje`, el sistema debe responder con HTTP 404 Not Found y un mensaje descriptivo.
- **Documento ya resuelto previamente**: Cuando un coordinador intenta resolver un documento que ya fue auditado y cerrado, el sistema debe responder con HTTP 409 Conflict o registrar la auditoría sucesiva según la regla de re-evaluación médica sin romper la inmutabilidad de la bitácora anterior.
- **PostgreSQL no disponible**: Si el pool de base de datos se interrumpe temporalmente, el repositorio debe levantar un error semántico que el endpoint traduzca a HTTP 503 Service Unavailable sin exponer trazas internas sensibles.
- **Filtros con parámetros inválidos**: Si se envían valores de tiempo de espera negativos o cadenas maliciosas en los filtros de búsqueda, el sistema debe responder con HTTP 422 o sanear la consulta mediante parámetros posicionales asíncronos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE exponer el endpoint `GET /api/v1/coordination/pending` accesible exclusivamente para usuarios autenticados con roles `COORDINADOR` y `ADMINISTRADOR`.
- **FR-002**: El endpoint `GET /api/v1/coordination/pending` DEBE admitir parámetros opcionales de filtrado: `especialidad` (cadena), `tiempo_espera_min` (entero >= 0) y paginación (`limit`, `offset`).
- **FR-003**: El sistema DEBE exponer el endpoint `POST /api/v1/coordination/resolve/{documento_id}` para registrar la decisión médica sobre un triaje.
- **FR-004**: La carga útil de `POST /api/v1/coordination/resolve/{documento_id}` DEBE exigir los campos: `decision` (enum: `aprobar`, `reclasificar`, `rechazar`), `justificacion_clinica` (texto no vacío, mínimo 5 caracteres) y campos opcionales para reasignación (`categoria_destino`, `prioridad_sugerida`).
- **FR-005**: Toda resolución médica DEBE persistirse de forma inmutable a través de `AuditRepository.registrar_auditoria_coordinacion` y registrar el correspondiente evento en `trazabilidad_eventos` vía `AuditRepository.registrar_evento_trazabilidad`.
- **FR-006**: El sistema DEBE denegar el acceso con HTTP 403 Forbidden a cualquier usuario autenticado cuyo rol no sea `COORDINADOR` o `ADMINISTRADOR` (ej. `OPERADOR`, `MEDICO`, `PACIENTE`).
- **FR-007**: Las solicitudes no autenticadas (sin cabecera `Authorization: Bearer <token>` o con token inválido/expirado) DEBEN ser rechazadas con HTTP 401 Unauthorized.
- **FR-008**: Todos los modelos de entrada y salida DEBEN implementarse con Pydantic v2 (`ConfigDict(from_attributes=True)`) y estar debidamente documentados y sincronizados en la especificación OpenAPI (`specs/openapi.yaml`).

### Key Entities *(include if feature involves data)*

- **BandejaPendientesTriaje**: Representa el conjunto de documentos en estado de revisión HITL (`PENDIENTE_AUDITORIA` o `REQUIERE_REVISION`), incluyendo identificador, fecha de ingesta, especialidad requerida, nivel de prioridad, nivel de confianza del modelo y paciente asociado.
- **DictamenAuditoriaCoordinacion**: Registro inmutable de la decisión tomada por el médico coordinador, vinculado a `documentos_triaje` y al usuario coordinador, con fecha y hora (`created_at`), decisión formal y justificación clínica.
- **EventoTrazabilidad**: Registro cronológico de auditoría médica hospitalaria que documenta cada transición de estado en el ciclo de vida del documento.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Los coordinadores médicos pueden consultar su bandeja de triajes pendientes y recibir la respuesta completa en menos de 500 milisegundos bajo condiciones normales de carga.
- **SC-002**: El 100% de las resoluciones médicas registradas persisten de manera inmutable en PostgreSQL sin pérdida de datos clínicos ni fallos de clave foránea.
- **SC-003**: El 100% de los intentos de acceso por parte de roles no autorizados (`OPERADOR`, etc.) son bloqueados con HTTP 403 Forbidden.
- **SC-004**: La suite completa de pruebas unitarias y de integración (`backend/tests/test_coordination_api.py`) pasa al 100% en verde con 0 fallos y 0 regresiones en el backend general.

---

## Assumptions

- **A-001**: Los usuarios con rol `COORDINADOR` y `ADMINISTRADOR` ya cuentan con credenciales y sesiones generadas válidas mediante el módulo `security.py`.
- **A-002**: La tabla `auditorias_coordinacion`, `trazabilidad_eventos` y las vistas relacionales ya se encuentran creadas en la base de datos PostgreSQL de desarrollo.
- **A-003**: La lógica de negocio para persistir dictámenes y eventos delega directamente en los métodos asíncronos de `AuditRepository`.
- **A-004**: Los identificadores de documentos corresponden al formato estándar de código único de triaje (`documento_id`).
