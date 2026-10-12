# Feature Specification: Calibrador de Score de Confianza Multimodal y Retención HITL

**Feature Branch**: `006-confidence-score` (desarrollado en rama de trabajo `dev-henry-suarez`)

**Created**: 2026-10-12

**Status**: Completed (100% Tests Passed)

**Input**: User description: "Calibrar cálculo de score de confianza multimodal en confidence.py para retener casos con confianza menor a 0.75"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Calibración Granular y Ponderación del Score Multimodal (Priority: P1)

Como evaluador clínico de triaje del sistema hospitalario, quiero que el agente de IA pondere cuantitativamente la legibilidad del texto/OCR, la claridad de las imágenes adjuntas y la completitud de las variables clínicas esenciales para calcular un score de confianza unificado, normalizado estrictamente entre 0.0 y 1.0.

**Why this priority**: Es la base del criterio clínico del agente. Un cálculo simplista o sesgado puede clasificar erróneamente un documento ilegible o incompleto como de alta certeza, poniendo en riesgo la seguridad asistencial del paciente.

**Independent Test**: Procesar documentos con distintos grados de calidad (texto nítido vs escaneos degradados, datos clínicos completos vs registros sin signos vitales o sin diagnóstico) y verificar que el score final refleje con precisión matemática y granularidad el valor calculado entre 0.0 y 1.0.

**Acceptance Scenarios**:

1. **Given** un documento con texto legible de alta extensión, datos de paciente confirmados, signos vitales y diagnóstico explícito con código CIE-10, **When** se evalúa la confianza en el nodo de calibración, **Then** el score de confianza resultante es alto (≥ 0.85) y refleja una ponderación positiva en cada dimensión evaluada.
2. **Given** un documento escaneado con texto muy breve o degradado (< 20 caracteres) y sin signos vitales o hallazgos clínicos claros, **When** se procesa la confianza, **Then** el score de confianza es penalizado adecuadamente y se mantiene estrictamente dentro del rango acotado [0.0, 1.0].

---

### User Story 2 - Retención Obligatoria por Umbral de Confianza HITL (< 0.75) (Priority: P1)

Como Coordinador Médico responsable de la seguridad hospitalaria, quiero que cualquier caso cuyo score de confianza global sea inferior al umbral clínico estricto de 0.75 sea retenido de forma obligatoria (*Human-in-the-Loop*), marcando `requiere_auditoria_humana = True`, suspendiendo el estado del flujo en `pendiente_auditoria` y desviando la solicitud hacia la `Cola_Auditoria_Humana`.

**Why this priority**: Garantiza la Regla de Oro y la Constitución de MediFlow. Ninguna derivación médica automatizada debe ejecutarse sin supervisión humana si la IA no alcanza un nivel de certeza clínica calificada (≥ 0.75).

**Independent Test**: Enviar documentos que produzcan un score calibrado de 0.74 o menor, verificando empíricamente que el sistema marque la auditoría como obligatoria y enrute a la cola de auditoría médica sin desviarse a colas ordinarias de rutina o farmacia.

**Acceptance Scenarios**:

1. **Given** un expediente o informe clínico cuyo score de confianza final es 0.74, **When** se evalúa la política de enrutamiento y auditoría, **Then** el sistema asigna `requiere_auditoria_humana = True`, define el estado final como `pendiente_auditoria` y fija el destino principal en `Cola_Auditoria_Humana`.
2. **Given** un expediente clínico de rutina con score de confianza final de 0.76 (≥ 0.75) y sin banderas de urgencia ni discrepancias de identidad, **When** se determina el enrutamiento, **Then** se permite el flujo automático regular sin exigir auditoría humana obligatoria por umbral de confianza.

---

### User Story 3 - Trazabilidad y Desglose Explicable de Factores de Confianza (Priority: P2)

Como Auditor Médico y Supervisor de Calidad de IA, quiero consultar en los metadatos del documento el desglose de los factores ponderados (calidad de texto, completitud clínica, legibilidad de imagen) para comprender de forma transparente e inmutable por qué un caso fue retenido o aprobado automáticamente.

**Why this priority**: Cumple con el Principio V de la Constitución de MediFlow (Trazabilidad Médica Inmutable y Explicabilidad). Facilita el análisis retrospectivo del Coordinador Médico durante la auditoría.

**Independent Test**: Consultar el estado y metadatos resultantes tras el cálculo de confianza y validar que se incluya un diccionario detallado con las penalizaciones y bonificaciones aplicadas.

**Acceptance Scenarios**:

1. **Given** un documento procesado por el nodo de confianza, **When** finaliza la calibración, **Then** el resultado contiene en los metadatos clínicos el desglose explícito de los factores (calidad de extracción, completitud de signos/diagnóstico, penalizaciones por errores) junto al score numérico final redondeado a 3 decimales.

---

### Edge Cases

- **Texto completamente vacío o ilegible**: Si la extracción falla o el texto es inferior al umbral mínimo, el score debe penalizarse hacia el límite inferior y garantizar retención HITL inmediata con justificación clínica explícita.
- **Score en el límite exacto del umbral (0.750)**: Un score exactamente igual a 0.750 cumple el umbral mínimo (score ≥ 0.75) y no es retenido por confianza baja, a menos que existan otras condiciones de seguridad (urgencia ambigua, medicamentos controlados o conflicto de identidad).
- **Presencia de factores atípicos o contradictorios**: Si el documento contiene diagnóstico pero carece de paciente o signos vitales, las bonificaciones y penalizaciones deben balancearse sin desbordar los límites [0.0, 1.0].

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE calcular el score de confianza final combinando la calidad del texto extraído, la coherencia diagnóstica y la completitud de entidades clínicas (datos demográficos, signos vitales y código CIE-10).
- **FR-002**: El score de confianza calculado DEBE estar acotado numéricamente de forma estricta entre `0.0` y `1.0`, redondeado a tres decimales.
- **FR-003**: El sistema DEBE comparar el score final contra el umbral de corte estricto `0.75`. Si `score < 0.75`, DEBE marcar de forma mandatoria `requiere_auditoria_humana = True`.
- **FR-004**: Ante un caso con `score < 0.75`, el enrutamiento DEBE dirigir la atención hacia `Cola_Auditoria_Humana` y suspender el procesamiento autónomo en estado `pendiente_auditoria`, notificando la necesidad de revisión médica.
- **FR-005**: Las reglas de seguridad de precedencia crítica (discrepancias de identidad DNI/HC según Issue #29 y emergencias médicas graves de nivel Urgente) DEBEN mantener su precedencia clínica sobre la cola de auditoría estándar.
- **FR-006**: El nodo de calibración DEBE adjuntar en los metadatos del estado la trazabilidad detallada de los factores de cálculo de confianza para auditoría médica.

### Key Entities

- **MetricasConfianza**: Representa el desglose multidimensional de señales evaluadas (calidad de texto, completitud clínica, legibilidad, penalizaciones aplicadas).
- **ClasificacionState**: Estado interno que almacena el `score_confianza_clasificacion` actualizado tras la calibración.
- **DecisionEnrutamientoState**: Entidad que refleja el destino final (`Cola_Auditoria_Humana`), el indicador `requiere_auditoria_humana` y la justificación clínica del triaje.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de los documentos con score de confianza menor a 0.75 son interceptados y asignados a la bandeja de revisión humana (`Cola_Auditoria_Humana`).
- **SC-002**: 0% de casos con score fuera del rango matemático [0.0, 1.0].
- **SC-003**: 100% de los casos procesados preservan el desglose de factores de confianza en metadatos para fines de auditoría médica hospitalaria.
- **SC-004**: Cero regresiones en la suite automatizada de pruebas del backend (`pytest backend/`) manteniendo 100% de tests en verde conforme a la Regla de Oro.

---

## Assumptions

- El modelo de datos `AgentState` ya contiene en `datos_extraidos` las estructuras de diagnóstico, signos vitales, hallazgos y paciente obtenidas en nodos precedentes.
- Las colas hospitalarias de destino están formalizadas bajo el catálogo unificado del sistema (`Cola_Auditoria_Humana`, `Cola_Revision_Ambigua`, `Cola_Emergencia_Medica`, `Cola_Rutina`, `Farmacia_Hospitalaria`).
- El umbral de corte de 0.75 reemplaza y actualiza formalmente la referencia previa de 0.50 en la decisión de enrutamiento por baja confianza.
