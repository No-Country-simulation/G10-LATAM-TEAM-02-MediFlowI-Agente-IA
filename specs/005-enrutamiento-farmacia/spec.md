# Feature Specification: Enrutamiento a Farmacia Hospitalaria

**Feature Branch**: `005-enrutamiento-farmacia` (desarrollado en rama de trabajo `dev-henry-suarez`)

**Created**: 2026-10-09

**Status**: Completed (100% Tests Passed)

**Input**: User description: "Actualizar nodo de enrutamiento en routing.py para derivar recetas y farmacoterapia hacia Farmacia_Hospitalaria"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enrutamiento automático de recetas (Priority: P1)

El sistema (agente LangGraph) debe procesar documentos identificados como "receta médica" o cuyo diagnóstico sugiera "farmacoterapia exclusiva sin descompensación aguda", asignándolos de manera predeterminada a la bandeja de `Farmacia_Hospitalaria`.

**Why this priority**: Asegura que las prescripciones médicas lleguen correctamente al área de dispensación farmacológica, agilizando la atención del paciente.

**Independent Test**: Puede probarse enviando un documento clasificado como receta médica normal y verificando que el destino final en `decision_enrutamiento` sea `Farmacia_Hospitalaria` y no requiera auditoría.

**Acceptance Scenarios**:

1. **Given** un documento procesado, **When** su clasificación indica "receta médica" sin medicamentos controlados, **Then** el destino de enrutamiento es `Farmacia_Hospitalaria` y `requiere_auditoria_humana` es `False`.

---

### User Story 2 - Retención de medicamentos controlados (Priority: P1)

Si la receta o solicitud incluye medicamentos de control especial o estupefacientes, el enrutamiento debe requerir obligatoriamente una revisión humana (HITL) para garantizar cumplimiento legal y seguridad.

**Why this priority**: Es una regla clínica y legal estricta. Dispensar medicamentos controlados sin revisión médica/coordinación puede llevar a graves sanciones y riesgos al paciente.

**Independent Test**: Puede probarse simulando la extracción de un medicamento controlado (ej. morfina, clonazepam) y verificando que el nodo de enrutamiento exija auditoría humana.

**Acceptance Scenarios**:

1. **Given** un documento procesado, **When** su clasificación o datos extraídos indican la presencia de medicamentos de control especial, **Then** el destino de enrutamiento se establece o mantiene en `Farmacia_Hospitalaria` (o el adecuado) y obligatoriamente `requiere_auditoria_humana` se establece en `True`.

### Edge Cases

- ¿Qué sucede si la receta es ilegible o ambigua respecto a si contiene un medicamento controlado? El sistema por seguridad debe enviarlo a `Cola_Revision_Ambigua` con auditoría forzada.
- ¿Qué pasa si un documento es una interconsulta urgente y a la vez contiene una receta médica? Prevalencia clínica: la urgencia médica debe priorizarse sobre la dispensación farmacológica normal.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El nodo de enrutamiento MUST asignar el destino `Farmacia_Hospitalaria` a todo documento clasificado como receta médica o cuyo diagnóstico indique farmacoterapia exclusiva sin descompensación aguda.
- **FR-002**: El nodo de enrutamiento MUST detectar la bandera o señal de "medicamentos controlados" (desde la extracción o clasificación) y establecer `requiere_auditoria_humana = True` en la decisión final.
- **FR-003**: La justificación de enrutamiento MUST indicar explícitamente si se derivó a Farmacia y si fue retenido por presencia de medicamentos de control especial.

### Key Entities *(include if feature involves data)*

- **DecisionEnrutamientoState**: Entidad que almacena el destino final (`Farmacia_Hospitalaria`), el flag de auditoría y la justificación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las recetas médicas sin medicamentos controlados son derivadas automáticamente a Farmacia sin requerir intervención humana.
- **SC-002**: El 100% de las recetas que incluyen medicamentos controlados son marcadas para auditoría médica (HITL).
- **SC-003**: Ningún documento legítimo de receta termina en colas erróneas (ej. Admisión o Archivo_Fisico).

## Assumptions

- Se asume que el nodo previo de extracción o clasificación ya es capaz de identificar e inyectar en el estado (`AgentState`) la información necesaria para saber si un documento es "receta médica" y si tiene "medicamentos controlados".
- Se asume que el destino `Farmacia_Hospitalaria` ya forma parte del catálogo de destinos permitidos del hospital.
