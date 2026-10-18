# Feature Specification: Visor interactivo y robusto de documentos PDF clínicos con skeleton loader y zoom

**Feature Branch**: `013-clinical-pdf-viewer`

**Created**: 2026-10-18

**Status**: Draft

**Input**: User description: "Visor interactivo y robusto de documentos PDF clinicos con skeleton loader y zoom. De manera general se necesita: Actualizar frontend/src/components/documents/DocumentViewer.tsx; Incorporar esqueleto de carga animado mientras el iframe o elemento <object> carga el PDF; Añadir barra de herramientas con botones de: Modo Pantalla Completa, Zoom In/Out y Descargar Archivo; Manejar estado de error con enlace de contingencia para descarga directa. Criterios de aceptación: Skeleton loader fluido mientras se completa la descarga del documento para mostrarse en pantalla; Botón de alternancia a pantalla completa (Full Screen API); Botón de descarga directa del PDF original; Comportamiento responsivo en dispositivos de escritorio y tablets clínicas."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización Fluida con Indicador de Carga Animado (Priority: P1)

Como profesional de la salud o evaluador médico en el sistema hospitalario, quiero visualizar un indicador de carga animado (skeleton loader) mientras se descarga y prepara el documento PDF clínico, para tener retroalimentación visual inmediata y saber con certeza que el documento está en proceso de despliegue en lugar de observar una pantalla vacía o congelada.

**Why this priority**: En un entorno hospitalario de alta demanda, la retroalimentación visual inmediata durante la carga de expedientes y recetas es crítica para evitar la percepción de fallo del sistema y reducir la frustración del personal médico.

**Independent Test**: Se puede verificar de forma independiente abriendo cualquier documento clínico PDF en el visor y observando que el esqueleto de carga animado se presenta instantáneamente y permanece visible de forma suave hasta que el contenido del documento esté completamente disponible para su lectura.

**Acceptance Scenarios**:

1. **Given** un documento clínico PDF seleccionado para su revisión, **When** el usuario solicita visualizar el archivo y la descarga o renderizado está en curso, **Then** el sistema presenta un esqueleto de carga animado fluido que ocupa el área de visualización sin parpadeos.
2. **Given** el visor mostrando el skeleton loader animado, **When** el documento PDF completa su carga exitosamente, **Then** el esqueleto de carga se oculta de forma fluida y se muestra el documento interactivo listo para su inspección médica.

---

### User Story 2 - Control de Ampliación y Alternancia a Pantalla Completa (Priority: P2)

Como médico o coordinador clínico, quiero ajustar el nivel de zoom (acercar, alejar y reiniciar) y alternar a pantalla completa mediante una barra de herramientas accesible, para inspeccionar con precisión firmas, sellos, dosis farmacológicas y notas manuscritas presentes en documentos clínicos complejos.

**Why this priority**: Los documentos clínicos escaneados con frecuencia presentan tipografías pequeñas o anotaciones marginales que requieren ampliación selectiva y un área de visualización máxima sin distracciones para emitir un juicio clínico seguro.

**Independent Test**: Se puede probar abriendo un documento PDF y accionando los botones de la barra de herramientas para acercar, alejar, restablecer al 100% y activar/desactivar la vista a pantalla completa, comprobando que la vista responde inmediatamente sin desbordar los límites del visor.

**Acceptance Scenarios**:

1. **Given** un documento PDF visible en el visor, **When** el usuario presiona el botón de acercar zoom, **Then** el contenido aumenta su escala visual de manera progresiva hasta un límite máximo seguro.
2. **Given** un documento con zoom aplicado, **When** el usuario presiona el botón de restablecer zoom o alejar, **Then** la escala se reduce o vuelve al 100% de su visualización estándar.
3. **Given** el visor en su tamaño integrado habitual, **When** el usuario presiona el botón de pantalla completa, **Then** el visor se expande para ocupar la totalidad del monitor o pantalla del dispositivo mediante la API nativa de pantalla completa, actualizando el ícono del botón para permitir volver al modo regular.

---

### User Story 3 - Descarga Directa y Manejo Resiliente de Fallos (Priority: P3)

Como personal administrativo o clínico, quiero disponer de un botón de descarga directa del archivo original y contar con una alternativa de contingencia si el visor embebido no puede renderizar el PDF, para garantizar la continuidad asistencial sin interrupciones operativas.

**Why this priority**: La disponibilidad ininterrumpida de los documentos médicos es vital; si un navegador bloquea complementos o un archivo presenta advertencias de compatibilidad embebida, el profesional médico debe poder obtener el documento original de manera inmediata.

**Independent Test**: Se puede probar haciendo clic en el botón de descarga para obtener el archivo original en el almacenamiento local, y simulando un fallo de carga embebida para comprobar la presencia del mensaje informativo y el enlace de descarga directa.

**Acceptance Scenarios**:

1. **Given** un documento clínico disponible, **When** el usuario hace clic en el botón de descarga de la barra de herramientas, **Then** el navegador inicia la descarga directa del archivo PDF original con su nombre correspondiente.
2. **Given** una situación donde el visor embebido experimenta un error de carga o restricción de visualización, **When** el renderizado falla, **Then** el sistema presenta un estado de error claro y no bloqueante con un botón o enlace de contingencia que permite descargar y abrir el archivo original directamente.

---

### Edge Cases

- **Conexiones hospitalarias lentas o documentos de gran volumen**: El skeleton loader debe permanecer visible y animado durante tiempos de respuesta prolongados sin bloquear la interfaz general.
- **Transición entre documentos sucesivos**: Si el usuario cambia de documento clínico mientras otro estaba cargando o ampliado, el visor debe reiniciar sus niveles de zoom a su valor base (100%), restablecer el skeleton loader y limpiar posibles estados de error previos.
- **Restricciones de seguridad del navegador para visores embebidos**: En entornos hospitalarios con políticas estrictas de seguridad (sandbox) que impidan la visualización embebida de PDFs, debe activarse el mecanismo de contingencia sin romper el layout.
- **Redimensionamiento de pantalla y rotación de tabletas**: Al cambiar entre orientación vertical y horizontal o redimensionar la ventana, la barra de herramientas y el documento deben adaptarse fluidamente sin ocultar los controles de acción.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar un esqueleto de carga animado (skeleton loader) en el contenedor principal mientras el documento PDF se encuentra descargando y preparando para visualización.
- **FR-002**: El sistema DEBE ocultar el skeleton loader y presentar el documento en pantalla una vez que el visor embebido confirme la disponibilidad del recurso.
- **FR-003**: El sistema DEBE incluir una barra de herramientas superior accesible y organizada que concentre las acciones de navegación y visualización clínica.
- **FR-004**: La barra de herramientas DEBE proporcionar controles de zoom interactivos: botón para acercar (zoom in), botón para alejar (zoom out) y selector/botón de restablecimiento a escala original (100%).
- **FR-005**: La barra de herramientas DEBE incluir un botón de alternancia a pantalla completa que active y desactive el modo de pantalla completa mediante la API del navegador (Full Screen API).
- **FR-006**: La barra de herramientas DEBE incorporar un botón para la descarga directa del archivo PDF original con preservación del nombre del archivo clínico.
- **FR-007**: El sistema DEBE detectar condiciones de error en la carga del documento embebido y mostrar un panel de contingencia explicativo con opción directa para descargar o abrir el archivo original en una pestaña independiente.
- **FR-008**: La interfaz del visor DEBE ser completamente responsiva, garantizando usabilidad ergonómica tanto en monitores de escritorio clínicos como en tabletas médicas en orientación vertical y horizontal.
- **FR-009**: Al cambiar el identificador o URL del documento recibido en las propiedades, el sistema DEBE restablecer el zoom a 100%, reiniciar el indicador de carga y limpiar estados de error previos.

### Key Entities

- **Documento Clínico**: Representa el expediente o archivo PDF sometido a visualización, caracterizado por su nombre descriptivo de archivo, su identificador único y su URL segura de origen.
- **Estado del Visor Clínico**: Conjunto reactivo de variables que controlan la experiencia de usuario, incluyendo el estado de carga (`cargando`, `listo`, `error`), el factor de ampliación (zoom), el estado de pantalla completa (`activo`, `inactivo`) y el mensaje de contingencia en caso de fallo.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de visualización de documentos presentan retroalimentación visual inmediata mediante el skeleton loader en menos de 100 ms tras la selección del archivo.
- **SC-002**: Los profesionales médicos pueden alternar al modo de pantalla completa y salir de él con una sola interacción (1 clic o toque táctil).
- **SC-003**: Los usuarios disponen de controles de zoom con respuesta visual inmediata (menor a 150 ms) para ampliar hasta al menos un 200% y restablecer a la vista estándar del 100%.
- **SC-004**: En escenarios de fallo de renderizado embebido, el 100% de los usuarios reciben una opción de contingencia de descarga directa accesible en menos de 1 segundo tras suscitarse el error.
- **SC-005**: La interfaz del visor y su barra de herramientas mantienen total legibilidad y operatividad en resoluciones desde tabletas (768px de ancho) hasta estaciones clínicas de alta definición (1080p y 4K), sin desbordamientos horizontales ni colisión de botones.

## Assumptions

- Los archivos PDF clínicos se encuentran alojados en rutas accesibles y autorizadas del sistema MediFlow.
- Los navegadores web de las estaciones clínicas soportan la API nativa de pantalla completa (`requestFullscreen` / `exitFullscreen`) o un mecanismo de fallback a pantalla completa de ventana.
- El visor conserva compatibilidad con la visualización de imágenes clínicas (JPG, PNG, WebP) además de los documentos PDF, manteniendo una experiencia unificada en el componente.
- Los estilos y maquetación respetan la directiva de diseño con Tailwind CSS y los lineamientos de accesibilidad hospitalaria sin sobrecarga de elementos decorativos innecesarios.

