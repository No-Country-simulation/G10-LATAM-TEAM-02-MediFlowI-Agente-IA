# Research: Endpoints REST de Coordinación y Auditoría Médica (HITL)

**Feature**: `specs/006-coordination-audit-api`
**Date**: 2026-10-09

## Research Questions & Findings

### 1. ¿Cómo estructurar la consulta de bandeja de triajes pendientes (`/pending`)?
- **Decision**: Consultar documentos con estado que requiera intervención humana (ej. `PENDIENTE_AUDITORIA`, `REQUIERE_REVISION`, `ambiguo`, o confianza menor al umbral configurado) cruzados con sus episodios y datos del paciente desde PostgreSQL.
- **Rationale**: Los coordinadores necesitan ver el contexto completo del caso: código de triaje, paciente (DNI/HC, nombre), especialidad sugerida, prioridad/urgencia, nivel de confianza del LLM y tiempo transcurrido desde la ingesta.
- **Alternatives considered**: Consultar sólo la tabla cruda `documentos_triaje` sin cruces; rechazada porque obligaría al cliente frontend a realizar múltiples peticiones para reconstruir la ficha del paciente.

### 2. ¿Cómo persistir el dictamen y los cambios de estado en `POST /resolve/{documento_id}`?
- **Decision**: Ejecutar de forma transaccional:
  1. Inserción del dictamen en `auditorias_coordinacion` vía `AuditRepository.registrar_auditoria_coordinacion`.
  2. Registro inmutable del evento correspondiente (`AUDITORIA_APROBADA`, `AUDITORIA_RECLASIFICADA`, `AUDITORIA_RECHAZADA`) en `trazabilidad_eventos` vía `AuditRepository.registrar_evento_trazabilidad`.
  3. Actualización del estado del documento de triaje (a `procesado`, `reclasificado` o `rechazado`) y de la categoría enrutada en `documentos_triaje`.
- **Rationale**: Garantiza la inmutabilidad de la auditoría y al mismo tiempo actualiza el estado operativo del documento para que salga de la bandeja de pendientes.
- **Alternatives considered**: Dejar el estado del documento intacto y solo persistir la tabla de auditoría; rechazada porque el documento seguiría apareciendo en la bandeja de pendientes de los coordinadores.

### 3. ¿Cómo modelar la seguridad RBAC para estos endpoints?
- **Decision**: Utilizar `Depends(require_roles("COORDINADOR", "ADMINISTRADOR"))` de `backend/app/core/security.py`.
- **Rationale**: Cumple directamente con el principio constitucional IV de RBAC hospitalario y con el paso 2 de la Tarea 3.2.
- **Alternatives considered**: Permitir a cualquier usuario autenticado; rechazada por violar la confidencialidad médica y la gobernanza HITL.

### 4. ¿Qué validaciones Pydantic v2 aplicar a la resolución médica?
- **Decision**:
  - `decision`: Enum estricto `Literal["aprobar", "reclasificar", "rechazar"]`.
  - `justificacion_clinica`: `constr(min_length=5, strip_whitespace=True)`.
  - `categoria_destino`: Opcional, pero requerida o sugerida cuando la decisión es `reclasificar`.
  - `prioridad_sugerida`: Opcional (`Literal["ALTA", "MEDIA", "BAJA", "URGENTE", "RUTINA"]`).
- **Rationale**: Previene resoluciones ambiguas o sin sustento clínico y mantiene compatibilidad con OpenAPI v3.
