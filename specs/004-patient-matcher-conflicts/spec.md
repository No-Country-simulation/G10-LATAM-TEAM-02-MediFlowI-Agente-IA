# Feature Specification: Nodo de Resolución de Identidad y Conflictos DNI/HC en Pipeline

**Feature Branch**: `004-patient-matcher-conflicts` (desarrollado en rama de trabajo `dev-wilmer-gulcochia`)  
**Created**: 2026-10-05  
**Status**: Draft  
**Input**: Añadir verificación de coincidencia de DNI y HC en el pipeline del agente para derivar conflictos a Cola_Revision_Ambigua  

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verificación de Coincidencia de Identificadores Clínicos (Priority: P1)

Como agente autónomo de triaje de MediFlow, quiero cotejar el DNI y la Historia Clínica extraídos del documento clínico contra la base de datos de pacientes mediante `resolver_paciente_por_identificadores(dni, hc)` para determinar si el documento pertenece con certeza a un paciente único, si es un paciente nuevo o si existe un conflicto de identidad.

**Why this priority**: En un entorno hospitalario, la asignación errónea de un estudio o receta a un paciente equivocado es un evento adverso grave. La IA nunca debe asumir o adivinar la identidad basándose solo en nombres si los identificadores oficiales discrepan.

**Independent Test**: Invocar la función de matching con combinaciones de DNI y HC válidas/inválidas y verificar que retorne los estados exactos: `asociado`, `sin_coincidencia` o `conflicto`.

**Acceptance Scenarios**:
1. **Given** un documento con DNI `12345678` y HC `HC-100` que pertenecen al mismo paciente en base de datos, **When** se evalúa la coincidencia, **Then** el estado resultante es `asociado` y el paciente queda identificado sin errores.
2. **Given** un documento con DNI `12345678` (Paciente A) y HC `HC-200` (Paciente B), **When** se evalúa la coincidencia, **Then** el sistema detecta `conflicto` de identidad y rechaza la asociación automática.
3. **Given** un documento con DNI o HC que no existen en la base de datos, **When** se evalúa, **Then** el estado es `sin_coincidencia` permitiendo la posterior creación en admisión.

---

### User Story 2 - Enrutamiento Automático a Cola de Revisión Ambigua por Conflicto (Priority: P2)

Como coordinador médico hospitalario (HITL), quiero que todo documento clínico con conflicto de identidad DNI/HC sea retenido automáticamente, derivado a la `Cola_Revision_Ambigua` y marcado con `requiere_auditoria_humana = True` para que un humano valide físicamente la identidad antes de anexar el estudio a la Historia Clínica Electrónica.

**Why this priority**: Garantiza la seguridad del paciente reteniendo en la cola de ambigüedad cualquier estudio con datos cruzados o discrepantes.

**Independent Test**: Ejecutar el pipeline completo del agente con un estado de conflicto de identidad y validar que `decision_enrutamiento.destino_principal == 'Cola_Revision_Ambigua'` y `decision_enrutamiento.requiere_auditoria_humana is True`.

**Acceptance Scenarios**:
1. **Given** un flujo de triaje donde se detectó `estado == "conflicto"`, **When** el agente llega al nodo de enrutamiento (`routing`), **Then** fuerza el destino a `Cola_Revision_Ambigua` sin importar que la prioridad clínica sea `Urgente` o `Rutina`.
2. **Given** un enrutamiento por conflicto de identidad, **When** se genera la justificación, **Then** incluye `"Discrepancia detectada entre DNI y HC: requiere revisión de ambigüedad"`.

---

### User Story 3 - Notificación y Registro de Metadata de Conflicto (Priority: P3)

Como auditor de calidad y sistema de monitoreo, quiero que la metadata del `AgentState` registre explícitamente el flag `"discrepancia_identidad_detectada": True` y los identificadores en conflicto para facilitar la auditoría rápida en la interfaz de Coordinación Médica.

**Why this priority**: Proporciona el contexto exacto al médico coordinador para que no tenga que buscar manualmente cuál fue el dato que falló.

**Independent Test**: Verificar que `state.metadata` contenga los datos del conflicto (`dni_extraido`, `hc_extraida`, `tipo_conflicto`).

**Acceptance Scenarios**:
1. **Given** un caso con conflicto DNI/HC, **When** finaliza el procesamiento, **Then** `state.metadata` contiene `discrepancia_identidad_detectada = True` y `motivo_ambiguedad = "conflicto_identidad_dni_hc"`.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El pipeline del agente DEBE integrar un módulo/función de resolución de identidad de pacientes (`patient_matcher.py` o dentro de `extraction.py`).
- **FR-002**: La resolución DEBE utilizar `patient_repository.resolver_paciente_por_identificadores(dni, hc)`.
- **FR-003**: Si el DNI extraído corresponde al Paciente A y la HC extraída corresponde al Paciente B, el sistema DEBE clasificar el resultado con `estado = "conflicto"`.
- **FR-004**: Ante un estado de `conflicto`, el pipeline DEBE asignar `requiere_auditoria_humana = True` en `AgentState`.
- **FR-005**: El nodo `routing.py` DEBE sobreescribir cualquier enrutamiento ordinario cuando exista conflicto de identidad, asignando como `destino_principal` a **`Cola_Revision_Ambigua`**.
- **FR-006**: El nodo `routing.py` DEBE incorporar en `justificacion_enrutamiento` el motivo de la discrepancia de identidad.
- **FR-007**: El sistema DEBE inyectar en `state.metadata` la clave `"discrepancia_identidad_detectada": True`.
- **FR-008**: Si solo viene DNI o solo viene HC y coincide con un único paciente, el sistema DEBE asociar exitosamente al paciente (`estado = "asociado"`).
- **FR-009**: La resolución NUNCA debe asumir coincidencia basada únicamente en similitud de nombres y apellidos si los documentos de identidad oficiales discrepan.

---

## Success Criteria

1. **Seguridad Clínica (Cero Falsas Asociaciones)**: 100% de los documentos con DNI y HC cruzados son detectados e interceptados antes de llegar a la Historia Clínica Electrónica.
2. **Derivación Precisa a HITL**: 100% de los conflictos son enrutados a `Cola_Revision_Ambigua` con retención humana activada (`requiere_auditoria_humana = True`).
3. **Cobertura de Pruebas**: 100% de pruebas unitarias y de pipeline pasando en verde en `backend/tests/test_patient_matcher.py` y `backend/tests/test_agent_cases.py`.

---

## Edge Cases

- **Documento sin DNI ni HC**: `resolver_paciente_por_identificadores(None, None)` retorna `sin_coincidencia` sin lanzar excepción ni marcar conflicto.
- **DNI con formato sucio o espacios**: La extracción debe limpiar espacios antes de consultar el repositorio (`strip()`).
- **DNI coincidente pero HC nula**: Asocia correctamente al paciente si el DNI existe en el sistema.
- **Fallo de conexión en `patient_repository`**: Si la base de datos no está disponible, el matcher maneja la excepción de forma controlada sin tumbar el pipeline.
