# Feature Specification: Visualización Estructurada de Medicamentos Prescritos, Vías de Administración y Robustez del Visor Clínico

**Feature Branch**: `014-prescription-medication-viewer`  
**Created**: 2026-10-20  
**Status**: Ready for Planning  
**Input**: User description: "Visualizacion estructurada de medicamentos prescritos vias de administracion y robustez del visor clinico"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización Estructurada de Prescripciones Médicas en la Ficha de Detalle (Priority: P1)

Como médico especialista o farmacéutico hospitalario, deseo ver en la ficha de detalle clínico de un documento (`/documentos/:id`) la lista completa de medicamentos prescritos, detallando el nombre del fármaco, posología/dosis, frecuencia y vía de administración (oral, intravenosa, intramuscular, tópica, etc.), para verificar la idoneidad farmacológica y fundamentar el enrutamiento hospitalario.

**Why this priority**:
La prescripción médica es el núcleo terapéutico del acto médico. Disponer de los medicamentos extraídos con su vía de administración previene errores de medicación y permite corroborar derivaciones hacia Farmacia Hospitalaria o áreas críticas sin forzar la lectura manual del documento crudo.

**Independent Test**:
Puede probarse accediendo a la ficha de detalle de un documento con prescripción médica (receta física o digital). La interfaz debe renderizar la tabla de medicamentos con sus columnas (*Medicamento*, *Dosis*, *Frecuencia*, *Vía*), mostrando insignias distintivas para la vía de administración y preservando la visualización existente del paciente, diagnóstico y código CIE-10.

**Acceptance Scenarios**:

1. **Given** un documento clínico procesado que contiene prescripciones médicas, **When** el usuario consulta su ficha de detalle (`/documentos/:id`), **Then** se despliega una tabla clínica con ícono de farmacoterapia conteniendo cada medicamento extraído, dosis, frecuencia y una insignia visual representativa para la vía de administración.
2. **Given** un documento clínico que no contiene prescripciones (ej. informe de laboratorio o volante administrativo), **When** el usuario visualiza los datos extraídos, **Then** la sección de medicamentos se omite de forma defensiva para no sobrecargar el espacio visual con tablas vacías.
3. **Given** un medicamento cuya vía de administración no fue consignada explícitamente en el texto original, **When** se renderiza la fila correspondiente, **Then** el campo de vía muestra un estado neutro o no aplicable sin quebrar el layout de la tabla.

---

### User Story 2 - Visualización en Tiempo Real de Fármacos en Consola de Triaje y Auditoría Médica (Priority: P2)

Como operador de triaje o médico auditor, deseo que tanto en la consola interactiva de triaje (`/triaje`) como en la bandeja de resolución de auditoría manual (*Human-in-the-Loop*, `/auditoria/:id`), los medicamentos prescritos detectados por el sistema se visualicen de forma inmediata, para validar decisiones antes de despachar o rectificar casos clínicos.

**Why this priority**:
La consola de triaje y la bandeja de auditoría son los entornos operacionales donde se evalúa el comportamiento del flujo clínico. El médico auditor necesita verificar de inmediato los medicamentos para confirmar si un fármaco controlado o de alto riesgo justifica la retención en auditoría o el despacho prioritario.

**Independent Test**:
Puede probarse cargando un caso clínico con prescripción en la consola de triaje o abriendo un documento retenido en la vista de auditoría. Ambos módulos deben mostrar la tabla de fármacos detectados con sus atributos antes de tomar la decisión médica.

**Acceptance Scenarios**:

1. **Given** un caso clínico seleccionado o ingresado en la consola de triaje (`/triaje`), **When** se ejecuta el análisis del agente, **Then** el panel de datos extraídos incluye la tabla estructurada de medicamentos prescritos junto al diagnóstico y score de confianza.
2. **Given** un documento derivado a revisión médica manual en `/auditoria/:id`, **When** el auditor médico accede al formulario de resolución, **Then** visualiza la lista de medicamentos prescritos identificados para respaldar su decisión de confirmar, rechazar o rectificar el destino a Farmacia Hospitalaria o al servicio correspondiente.

---

### User Story 3 - Robustez Semántica y Accesibilidad en Panel de Contingencia del Visor Clínico (Priority: P3)

Como usuario clínico que opera el visor de documentos, cuando un documento o imagen no puede decodificarse o cargarse, deseo que el panel de contingencia clínica presente un encabezado de alerta semántico y un texto explicativo diferenciado, para comprender de inmediato el fallo sin ambigüedades y acceder rápidamente a las opciones de descarga directa o apertura en pestaña independiente.

**Why this priority**:
En situaciones de error de visualización, la ambigüedad en los textos o la duplicidad de mensajes en títulos y descripciones dificulta la accesibilidad para lectores de pantalla y herramientas de pruebas automatizadas. Desacoplar el título del mensaje explicativo asegura claridad clínica y robustez según los estándares del proyecto.

**Independent Test**:
Puede probarse proveyendo una imagen corrupta o URL inválida al visor clínico. El visor debe capturar el evento de error y mostrar en el panel de contingencia un título de alerta claro ("Error de decodificación de imagen clínica") separado del cuerpo descriptivo ("No fue posible decodificar o cargar la imagen clínica..."), manteniendo activos los botones de descarga y apertura externa.

**Acceptance Scenarios**:

1. **Given** una imagen médica que falla al decodificarse en el navegador, **When** el visor activa el estado de contingencia, **Then** el encabezado muestra de manera concisa el título del error y el párrafo explicativo detalla la causa con opciones claras de contingencia.
2. **Given** la suite de pruebas automatizadas y de accesibilidad, **When** se evalúa la presencia del mensaje de contingencia, **Then** la consulta por texto se resuelve de manera unívoca sin ambigüedades de múltiples elementos coincidentes.

---

### Edge Cases

- **Prescripción con valores parciales o nulos**: Si un medicamento solo consigna el nombre del fármaco pero omite dosis o frecuencia, el sistema debe renderizar la fila mostrando guiones o etiquetas neutras sin interrumpir el flujo visual.
- **Múltiples medicamentos en una misma receta**: La tabla debe permitir navegación horizontal defensiva en pantallas móviles o pantallas médicas compactas sin desbordar el contenedor.
- **Vías de administración diversas**: Soportar vías orales, intravenosas, subcutáneas, inhalatorias, tópicas u oftálmicas mediante insignias visuales legibles y contrastadas.
- **Fallo total de red en visor**: Si el archivo no puede descargarse desde el servidor de almacenamiento, el panel de contingencia debe mantener el botón de descarga directa habilitado apuntando al recurso original.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El modelo de datos del cliente DEBE tipar formalmente la entidad de prescripción médica con atributos para nombre del fármaco, dosis, frecuencia y vía de administración.
- **FR-002**: La capa de comunicación del cliente DEBE deserializar dinámicamente la lista de medicamentos desde los datos extraídos del documento, tanto en consultas individuales como en listados.
- **FR-003**: El componente de datos clínicos extraídos DEBE renderizar una tabla dedicada para medicamentos prescritos con columnas de fármaco, dosis, frecuencia y vía de administración.
- **FR-004**: Cada vía de administración identificada DEBE mostrarse con una insignia visual estilizada para rápida lectura clínica.
- **FR-005**: Si un documento no contiene fármacos prescritos, la sección de medicamentos DEBE omitirse de la vista para mantener la sobriedad y ergonomía de la interfaz médica.
- **FR-006**: La consola de triaje y la vista de auditoría médica DEBEN incluir la visualización estructurada de medicamentos prescritos para soporte en la toma de decisiones.
- **FR-007**: El visor clínico de documentos DEBE estructurar el panel de contingencia con un encabezado descriptivo diferenciado del párrafo explicativo para garantizar accesibilidad semántica.
- **FR-008**: Todas las interfaces que renderizan farmacoterapia DEBEN ser 100% responsivas y garantizar ergonomía en estaciones clínicas y dispositivos móviles.

---

### Key Entities *(include if feature involves data)*

- **Medication (Entidad de Farmacoterapia)**: Representa un fármaco prescrito dentro del acto médico. Contiene el nombre del principio activo o comercial (`medicamento`), la posología cuantitativa (`dosis`), la pauta horaria o intervalo (`frecuencia`) y la forma de administración al paciente (`via_administracion`).
- **ClinicalDocument (Entidad de Documento Clínico)**: Representa el expediente clínico procesado. En su campo de datos extraídos (`datos_extraidos`), incorpora la colección de entidades `Medication` asociadas al diagnóstico principal y código CIE-10.
- **DocumentViewerState (Estado del Visor Clínico)**: Modela el ciclo de vida de renderizado del documento clínico (`loading`, `ready`, `error`), manteniendo mensajes de error diferenciados para encabezado y cuerpo descriptivo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: La tabla de medicamentos prescritos y sus vías de administración se renderiza en menos de 200 milisegundos tras la recepción de los datos del documento.
- **SC-002**: 100% de las pruebas unitarias y de integración de frontend (`vitest run`) se ejecutan y aprueban en verde sin fallos por ambigüedad de selectores ni regresiones.
- **SC-003**: Compilación de producción (`npm run build`) limpia con cero errores de TypeScript y cero advertencias no justificadas.
- **SC-004**: 100% de los elementos interactivos del visor y de las tablas de farmacoterapia son accesibles y operables tanto en pantallas de escritorio como en tablets y móviles médicos.

---

## Assumptions

- El backend de MediFlow provee la extracción de medicamentos estructurada en el payload JSON bajo `datos_extraidos.medicamentos` (conforme a IA-07 / Requisito R3).
- Las recetas pueden contener desde 1 hasta más de 10 medicamentos simultáneos.
- El usuario clínico dispone de un navegador moderno compatible con estándares HTML5 para visualización de componentes responsivos.
