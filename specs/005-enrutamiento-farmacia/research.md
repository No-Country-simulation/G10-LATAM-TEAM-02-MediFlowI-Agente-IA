# Phase 0: Outline & Research

## Decision 1: Identificación de Recetas y Medicamentos Controlados
- **Decision**: El nodo `routing.py` dependerá del campo `tipo_documento` (ej. `"Receta_Medica"`), de la evaluación del string `diagnostico` (buscando "farmacoterapia" sin "descompensación aguda"), y de una bandera en la metadata `state.metadata.get("medicamentos_controlados", False)` para determinar la obligatoriedad de la auditoría humana (HITL).
- **Rationale**: Mantiene el nodo de enrutamiento como una función pura de decisión basada en reglas clínicas claras, evaluando la severidad en base a la combinación del tipo de documento y el diagnóstico textual.
- **Alternatives considered**: Parsear `state.datos_extraidos.hallazgos_clave` usando expresiones regulares exhaustivas, pero se prefiere usar la combinación directa del diagnóstico y metadata para mayor robustez clínica.

## Decision 2: Resolución de Precedencia Clínica (Urgencias vs Farmacia)
- **Decision**: El nivel de prioridad `"Urgente"` (Emergencia Médica) tomará precedencia absoluta sobre el enrutamiento a `"Farmacia_Hospitalaria"`.
- **Rationale**: En un contexto hospitalario real (y bajo las reglas clínicas de MediFlow), una alerta de urgencia requiere atención inmediata del médico de guardia, independientemente de si el documento también contiene una prescripción farmacológica.
- **Alternatives considered**: Derivar a ambas colas (imposible con el estado actual ya que `destino_principal` es único) o derivar a Farmacia primero (peligroso para la vida del paciente).

## Decision 3: Interacción con el Detector de Discrepancias (Issue #29)
- **Decision**: Si el estado tiene la bandera de conflicto de identidad (`state.metadata.get("discrepancia_identidad_detectada")`), el documento debe ir a `"Cola_Revision_Ambigua"`, incluso si es una receta médica controlada.
- **Rationale**: La seguridad del paciente exige que primero se resuelva a quién pertenece el documento antes de despachar medicamentos.
- **Alternatives considered**: Despachar a Farmacia y que el farmacéutico resuelva la identidad. Descartado porque la resolución de identidad es responsabilidad de auditoría general, no de la farmacia.

## Decision 4: Actualización del Status Global del Grafo
- **Decision**: Si el documento es enrutado a Farmacia por un medicamento de control especial, la variable `requiere_auditoria_humana` será `True`, lo cual a nivel del nodo seteará `status_final = "pendiente_auditoria"`.
- **Rationale**: Mantiene consistencia con cómo el sistema UI lee los estados pendientes de los pacientes.
- **Alternatives considered**: Crear un nuevo status `"pendiente_farmacia"`. Descartado por ser innecesario y requerir cambios masivos en el frontend y en la tabla de PostgreSQL.
