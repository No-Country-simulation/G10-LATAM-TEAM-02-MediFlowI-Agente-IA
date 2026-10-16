# Feature Specification: Extracción Estructurada de Medicamentos Prescritos y Enrutamiento a Farmacia Hospitalaria

**Feature Branch**: `dev-wilmer-gulcochia`

**Created**: 2026-10-15

**Status**: Draft

**Input**: User description: "Extracción estructurada de medicamentos prescritos dosis frecuencia y vía de administración en recetas médicas con Pydantic y enrutamiento a Farmacia_Hospitalaria (Requisito R3)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extracción de Pauta Farmacológica Completa en Recetas Médicas (Priority: P1)

Como personal del servicio de Farmacia Hospitalaria y médico auditor, quiero que el sistema identifique y extraiga con precisión el listado de todos los medicamentos prescritos en una receta médica, detallando el nombre del fármaco, dosis, frecuencia y vía de administración, para agilizar la dispensación segura y evitar errores de medicación.

**Why this priority**: Representa el núcleo del Requisito R3. La correcta identificación de medicamentos y su dosificación es crítica para la seguridad del paciente y para el flujo operativo hospitalario.

**Independent Test**: Puede probarse de forma aislada procesando documentos tipo receta médica con prescripciones explícitas (ejemplo: *"Paracetamol 500 mg cada 8 horas vía oral"* y *"Amoxicilina 875 mg cada 12 horas vía oral"*), verificando que se obtenga una lista estructurada con cada fármaco desagregado en sus componentes clínicos y el documento sea derivado a `Farmacia_Hospitalaria`.

**Acceptance Scenarios**:

1. **Given** un documento clínico digitalizado correspondiente a una receta médica ambulatoria con dos o más fármacos prescritos con pauta completa, **When** el agente procesa el documento, **Then** el sistema extrae un listado estructurado donde cada elemento contiene el nombre del medicamento, dosis, frecuencia y vía de administración normalizados, y enruta el caso a `Farmacia_Hospitalaria`.
2. **Given** una receta con prescripción de antibióticos o analgésicos que incluye dosis e intervalo horario pero omite la vía explícita, **When** el sistema analiza la indicación, **Then** extrae fielmente el medicamento, dosis y frecuencia, dejando la vía como no especificada sin abortar el procesamiento ni generar datos inventados.

---

### User Story 2 - Tolerancia a Prescripciones con Datos Parciales o Abreviaturas Clínicas (Priority: P2)

Como personal de farmacia y admisión clínica, quiero que el sistema sea capaz de registrar prescripciones médicas que presenten datos complementarios parciales (por ejemplo, medicación sin vía indicada o abreviaturas estándar como "c/8h", "VO", "EV", "PRN"), preservando la fidelidad textual del documento original.

**Why this priority**: En la práctica clínica real, muchas recetas manuscritas o emitidas en consultorio omiten la vía (asumiendo vía oral) o usan abreviaturas médicas estándar. El sistema no debe fallar ni descartar el fármaco.

**Independent Test**: Puede probarse enviando recetas con abreviaturas posológicas típicas ("Ibuprofeno 400mg c/8h VO", "Metformina 850mg 1 vez al día") y confirmando que los atributos se capturen correctamente en sus respectivos campos.

**Acceptance Scenarios**:

1. **Given** una indicación médica con abreviaturas de frecuencia ("c/12h", "1 comp/día"), **When** el sistema procesa el texto, **Then** almacena la frecuencia preservando el significado clínico sin corromper el nombre del fármaco ni la dosis.
2. **Given** una prescripción donde solo figura el nombre del fármaco y la dosis sin intervalo horario especificado, **When** el agente extrae los datos, **Then** registra el medicamento y su dosis con frecuencia nula o no especificada, manteniendo la integridad del registro clínico.

---

### User Story 3 - Discriminación de Documentos sin Prescripciones Farmacológicas (Priority: P3)

Como coordinador médico y equipo de triaje, quiero que los documentos que no constituyan recetas ni contengan prescripciones activas (por ejemplo: informes de laboratorio, estudios radiológicos o notas de evolución sin medicamentos) mantengan la lista de medicamentos vacía y sean derivados a sus colas asistenciales habituales (como `Cola_Rutina` o `Cola_Emergencia_Medica`), sin ser desviados erróneamente a Farmacia.

**Why this priority**: Evita la saturación del servicio de Farmacia Hospitalaria con documentos diagnósticos que no requieren dispensación de fármacos.

**Independent Test**: Puede probarse procesando un informe ecográfico o de laboratorio sin medicamentos prescritos, verificando que la lista de medicamentos resulte vacía (`[]`) y el enrutamiento respete la cola clínica correspondiente (ej. `Cola_Rutina`).

**Acceptance Scenarios**:

1. **Given** un informe de radiografía de tórax con diagnóstico pero sin indicaciones farmacológicas, **When** el agente realiza la extracción y enrutamiento, **Then** la colección de medicamentos permanece vacía y el destino se asigna según la prioridad clínica general (no `Farmacia_Hospitalaria`).
2. **Given** una nota de evolución médica de urgencia que menciona un antecedente farmacológico pasado pero no prescribe nueva medicación, **When** el sistema extrae la información, **Then** no confunde los antecedentes con prescripciones activas y enruta acorde a la gravedad del cuadro clínico.

---

### Edge Cases

- **Polifarmacia extensiva**: Recetas con más de 5 medicamentos simultáneos. El sistema debe extraer la totalidad de los ítems en una lista sin truncamiento.
- **Medicamentos controlados o estupefacientes**: Prescripciones que contengan psicotrópicos, opiáceos o estupefacientes (ej. morfina, fentanilo, clonazepam). Deben enrutarse a `Farmacia_Hospitalaria` activando la bandera de auditoría humana obligatoria por normativa de control de sustancias.
- **Recetas de emergencia vital**: Documentos donde se indica medicación pero el paciente presenta un cuadro de riesgo vital inminente (ej. Shock anafiláctico con indicación de adrenalina). La prioridad de emergencia hospitalaria (`Cola_Emergencia_Medica`) debe prevalecer sobre el enrutamiento de rutina de farmacia.
- **Texto ilegible o receta borrosa**: Si el OCR o la visión extraen caracteres ininteligibles que impiden determinar el fármaco con certeza (confianza < 0.75), el caso debe derivarse a `Cola_Auditoria_Humana` para revisión por el Coordinador Médico antes de dispensar.
- **Doble denominación (marca vs. genérico)**: Indicaciones tipo "Paracetamol (Panadol) 500 mg". El sistema debe capturar el nombre principal comprensible sin duplicar el registro como dos medicamentos distintos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE identificar y extraer estructuradamente cada medicamento prescrito presente en el documento clínico.
- **FR-002**: Para cada medicamento detectado, el sistema DEBE capturar los siguientes cuatro atributos clínicos:
  - Nombre del medicamento (fármaco genérico o comercial prescrito).
  - Dosis (cantidad y unidad de medida, ej. "500 mg", "1 g", "10 ml").
  - Frecuencia (pauta temporal de administración, ej. "cada 8 horas", "una vez al día", "SOS").
  - Vía de administración (ej. "oral", "intravenosa", "subcutánea", "tópica", "inhalatoria").
- **FR-003**: El campo "nombre del medicamento" DEBE ser obligatorio para cada entrada válida de la lista; los campos de dosis, frecuencia y vía de administración DEBEN ser opcionales (permitir valor nulo si no se mencionan explícitamente en el texto original).
- **FR-004**: El sistema DEBE garantizar que la colección de medicamentos se inicialice como una lista vacía por defecto cuando el documento procesado no contenga prescripciones terapéuticas.
- **FR-005**: El sistema DEBE enrutar automáticamente los documentos categorizados como receta médica o con prescripciones farmacológicas activas hacia el destino `Farmacia_Hospitalaria`, siempre que no exista una condición de emergencia médica aguda que exija derivación inmediata a `Cola_Emergencia_Medica`.
- **FR-006**: Si una prescripción contiene medicamentos sujetos a control especial (estupefacientes o psicofármacos) o si la confianza del análisis es inferior al umbral hospitalario (score < 0.75), el sistema DEBE marcar la necesidad de intervención humana (`requiere_auditoria_humana = True`).
- **FR-007**: Queda estrictamente PROHIBIDO inventar, asumir o inferir medicamentos, dosis o vías de administración que no se encuentren respaldados en el contenido del documento médico original.

---

### Key Entities *(include if feature involves data)*

- **Medicamento Prescrito (Prescribed Medication Entity)**:
  - Representa una indicación farmacoterapéutica individual emitida por un profesional médico para el tratamiento de un paciente.
  - Atributos clave:
    - `medicamento`: Nombre del principio activo o especialidad farmacéutica prescrita (cadena de texto no vacía).
    - `dosis`: Cantidad administrada por toma junto con su unidad de medida posológica (cadena de texto o nulo).
    - `frecuencia`: Intervalo horario, pauta temporal o periodicidad de la toma (cadena de texto o nulo).
    - `via_administracion`: Ruta de administración anatómica recomendada (cadena de texto o nulo).
- **Receta Médica / Prescripción Clínica**:
  - Documento asistencial que agrupa una o más entidades de medicamento prescrito, asociado a un paciente, profesional prescriptor y episodio clínico.
  - Relación: Un documento clínico de triaje puede contener 0, 1 o múltiples medicamentos prescritos.
- **Destino Asistencial `Farmacia_Hospitalaria`**:
  - Cola operativa del servicio de farmacia donde se reciben las solicitudes de validación de receta, verificación de interacciones y dispensación de fármacos.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los documentos tipo receta médica que presenten indicaciones farmacológicas explícitas generan un listado estructurado de medicamentos sin pérdida del nombre del fármaco ni de su dosis.
- **SC-002**: El sistema alcanza una precisión superior al 95% en la asignación correcta de destino a `Farmacia_Hospitalaria` para recetas médicas y prescripciones ambulatorias no emergentes.
- **SC-003**: En el 100% de los casos con medicamentos sujetos a fiscalización o recetas con texto ambiguo/dudoso (confianza < 0.75), el sistema activa la salvaguarda de auditoría médica humana antes de la dispensación.
- **SC-004**: Los documentos clínicos de diagnóstico o evolución sin indicaciones farmacológicas registran un arreglo vacío de medicamentos en el 100% de los casos evaluados, evitando derivaciones erróneas a Farmacia.

---

## Assumptions

- **A-001**: Las recetas médicas pueden presentarse en formatos digitales estructurados, PDFs con texto vectorial o escaneos/fotografías que ya hayan atravesado la fase de ingesta y extracción de texto/visión del agente.
- **A-002**: La nomenclatura de medicamentos en español es la primaria en el contexto del hospital (LATAM), admitiendo tanto denominaciones comunes internacionales (DCI / genéricos) como marcas comerciales registradas en la región.
- **A-003**: Cuando un documento combina un diagnóstico de extrema urgencia con indicación terapéutica inmediata (ej. paro cardíaco, politraumatismo), la derivación a `Cola_Emergencia_Medica` tiene precedencia asistencial sobre la gestión de farmacia ambulatoria.
- **A-004**: Los modelos de extracción no realizan juicio terapéutico sobre la idoneidad clínica de la dosis prescrita por el médico; su función es registrar fielmente lo formulado en el documento.
