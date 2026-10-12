# Research: Orquestación de Triaje y Episodios Clínicos

**Feature**: `007-triage-episode-orchestration`
**Date**: 2026-10-10
**Author**: MediFlow Architecture Team

## Decisiones de Arquitectura y Patrones Técnicos

### 1. Detección de Episodio Activo del Paciente

- **Decisión**: Implementar `get_active_episode_by_patient(paciente_id: UUID | str)` en `episode_repository.py` que consulte el episodio más reciente donde `estado_atencion != 'cerrado'`.
- **Racional**:
  - Evita duplicar registros de atención cuando un paciente ya se encuentra en el circuito asistencial (`ingresado`, `en_triaje`, `evaluacion_general`, `derivado_especialista`).
  - La consulta se apoya en el índice existente `idx_episodios_paciente` sobre `episodios_clinicos(paciente_id)`.
- **Alternativas consideradas**:
  - *Crear siempre un episodio nuevo por cada documento*: Rechazada porque viola el principio de ciclo de vida hospitalario, donde múltiples documentos (analíticas, notas, recetas) forman parte de la misma estancia o episodio de atención.
  - *Usar `list_episodes` genérico filtrando en memoria*: Rechazada para consultas de alta concurrencia; un método especializado con `LIMIT 1` es más óptimo y limpio.

### 2. Creación Automática de Episodio

- **Decisión**: Utilizar `episode_repository.create_episode(...)` pasando los datos clínicos ya estructurados por los nodos de LangGraph:
  - `paciente_id`: ID del paciente resuelto.
  - `operador_ingreso_id`: `usuario_registro_id` (proveniente de la autenticación del usuario que subió el documento).
  - `nivel_prioridad`: Prioridad clínica inferida por el modelo (`resultado.clasificacion.nivel_prioridad` o `"Rutina"`).
  - `motivo_consulta`: Hipótesis diagnóstica o resumen de hallazgos (`resultado.datos_extraidos.diagnostico_principal`).
  - `especialidad_requerida`: Especialidad sugerida por el agente de triaje (`resultado.clasificacion.especialidad`).
  - `estado_atencion`: `"ingresado"`.
- **Racional**:
  - Garantiza congruencia entre lo extraído por el agente IA y la ficha de apertura hospitalaria.
  - Genera automáticamente un código único de seguimiento (`EP-YYYYMMDD-XXXX`).

### 3. Vinculación en `documentos_triaje` y Repositorio PostgreSQL

- **Decisión**:
  - Propagar `resultado.metadata["episodio_id"] = str(episodio_id)` y `resultado.metadata["codigo_episodio"] = codigo_episodio`.
  - Actualizar `PostgresStorageRepository.guardar_resultado(...)` para que persista `episodio_id` en la tabla `documentos_triaje` (columna ya creada en la migración `o8p808522kl4`).
  - Mantener soporte tanto en el flujo real con `asyncpg` como en el almacén en memoria para pruebas unitarias (`_mock_store`).
- **Racional**:
  - Garantiza consistencia relacional y permite que la vista `v_episodios_detalle` y las consultas de coordinación puedan enlazar los documentos al episodio clínico.

### 4. Trazabilidad Inmutable del Evento

- **Decisión**: Invocar `AuditRepository.registrar_evento_trazabilidad(...)` con el evento `DOCUMENTO_ASOCIADO_A_EPISODIO`.
- **Racional**:
  - Cumple estrictamente con el Principio V de la Constitución de MediFlow (Trazabilidad Médica Inmutable y Auditoría E2E).
  - Almacena en `metadata` del evento si el episodio fue creado automáticamente o si se asoció a uno preexistente.

### 5. Resiliencia y Manejo de Errores

- **Decisión**: La orquestación de episodios dentro de `TriageService` estará contenida en un bloque de control de excepciones que:
  - Registre detalladamente cualquier error con `logger.error("triage_service.episodio.error", ...)`.
  - No interrumpa ni lance una excepción que aborte el procesamiento del documento si el documento y sus extracciones de IA son válidos.
  - Marque en `resultado.metadata["episodio_error"] = str(exc)` para trazabilidad operativa.
- **Racional**:
  - Disponibilidad clínica (*High Availability*): en una guardia médica de urgencias, si la vinculación relacional secundaria sufre un timeout o bloqueo temporal, el médico debe poder recibir el informe de triaje y la alerta de prioridad de inmediato.
