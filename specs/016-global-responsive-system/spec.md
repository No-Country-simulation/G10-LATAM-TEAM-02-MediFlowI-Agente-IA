# Feature Specification: Sistema Global de Diseño Adaptable y Responsive (MediFlow Web)

**Feature Branch**: `016-global-responsive-system`  
**Created**: 2026-10-20  
**Status**: Draft  
**Input**: User description: "crea un spec global para el responsive todo el sistema que actual se esan rompiendo ciertos diseños"  

---

## Resumen Ejecutivo y Alcance

MediFlow es un sistema hospitalario de triaje médico y procesamiento documental por Inteligencia Artificial que opera en múltiples terminales de salud: pantallas de escritorio en estaciones de enfermería y salas de guardia (1920px / 1440px / 1280px), computadoras portátiles médicas (1024px), tablets clínicas para rondas médicas (768px a 834px) y dispositivos móviles de guardia (360px a 480px).

Actualmente, varias vistas clínicas presentan anomalías visuales en resoluciones intermedias y móviles:
1. **Layout y Navegación**: La barra lateral (`Sidebar`) superpone contenido o genera desbordamientos horizontales cuando el ancho de pantalla disminuye de 1024px.
2. **Tablas Clínicas de Alta Densidad**: Tablas con múltiples columnas (Documentos, Pacientes, Usuarios y Auditoría) se desbordan o truncan información crítica de pacientes sin contenedores con scroll horizontal táctil ni tarjetas adaptativas.
3. **Parrillas Bento y Paneles KPI**: Las métricas de triaje y contadores operativos pierden su proporción en pantallas pequeñas, provocando solapamiento de textos o tarjetas desalineadas.
4. **Visor Documental y Consola de Triaje**: La vista dividida (archivo original vs. datos estructurados por IA) colapsa en tablets y móviles impidiendo la visualización simultánea o alternada fluida.
5. **Formularios y Modales de Captura**: Los modales de registro de paciente, filtros y acciones flotantes se recortan verticalmente sin scroll interno en pantallas táctiles compactas.

Esta especificación establece los requisitos funcionales, criterios de aceptación independientes y directrices de usabilidad para garantizar un diseño 100% responsive, coherente y accesible en todo el ecosistema web de MediFlow.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegación Principal y Shell Adaptable (Prioridad: P1)

Como médico de guardia o enfermero que utiliza una tablet clínica o laptop en movilidad, necesito que el menú de navegación, la barra superior y el área de contenido principal se adapten automáticamente al tamaño de pantalla sin ocultar información ni generar scroll horizontal no deseado, para poder navegar eficientemente por los módulos del sistema.

**Why this priority**: Es la base estructural de toda la aplicación. Si el layout global colapsa o empuja los componentes fuera de la pantalla, ninguna otra vista puede utilizarse adecuadamente.

**Independent Test**: Cambiar el viewport del navegador a anchos de 375px (smartphone), 768px (tablet) y 1024px+ (desktop); verificar que el Sidebar se oculte en modo off-canvas/drawer con botón de hamburguesa accesible en móvil/tablet y se expanda permanentemente en escritorio.

**Acceptance Scenarios**:
1. **Given** un usuario que accede desde una tablet o smartphone (< 1024px), **When** se carga la aplicación, **Then** el menú lateral se encuentra replegado por defecto y se muestra un botón visible en la cabecera para abrirlo en formato drawer con backdrop interactivo.
2. **Given** el menú lateral abierto en dispositivo móvil, **When** el usuario selecciona una opción de navegación o presiona el botón de cierre/backdrop, **Then** la navegación se realiza y el menú se repliega automáticamente sin bloquear la pantalla.
3. **Given** una estación de trabajo de escritorio (≥ 1024px), **When** el usuario visualiza el sistema, **Then** la barra lateral se fija de manera persistente a la izquierda con el contenido clínico ocupando el espacio restante de forma fluida.

---

### User Story 2 - Tablas Clínicas y Controles de Paginación en Vistas Compactas (Prioridad: P1)

Como coordinador médico o auditor que consulta listas de triaje, pacientes o documentos desde un dispositivo móvil o tablet, necesito que las tablas de datos no se desborden de la pantalla y permitan un desplazamiento fluido o una representación compacta en tarjetas, con controles de paginación y acciones accesibles con toques de dedos.

**Why this priority**: Las listas de documentos, pacientes y usuarios son la herramienta de trabajo diario. Si los datos se cortan o los botones de acción quedan inaccesibles, se impide la auditoría clínica y el triaje.

**Independent Test**: Acceder a las vistas `/documentos`, `/pacientes` y `/usuarios` en un viewport de 390px; verificar que las tablas permitan scroll horizontal suave con encabezados claros o colapsen a tarjetas legibles, y que los botones "Ver", "Revisar" e "Ingestar" mantengan un tamaño táctil mínimo de 44x44px.

**Acceptance Scenarios**:
1. **Given** un listado de más de 10 documentos con columnas de ID, paciente, fecha, prioridad y acciones, **When** se visualiza en un ancho inferior a 768px, **Then** el contenedor de la tabla conserva scroll horizontal contenido (`overflow-x-auto`) sin desbordar el ancho de la página ni romper el layout exterior.
2. **Given** la barra de paginación al pie de una tabla clínica, **When** se visualiza en móvil, **Then** los elementos de paginación se reorganizan en múltiples filas limpias (resumen de conteo arriba, botones Anterior/Siguiente abajo) sin superponerse ni ocultar texto.
3. **Given** los botones de acción rápida por fila, **When** se tocan en pantalla táctil, **Then** responden de inmediato y cuentan con espaciado suficiente para evitar pulsaciones erróneas.

---

### User Story 3 - Parrillas KPI y Métricas del Dashboard Adaptables (Prioridad: P2)

Como director o jefe de guardia que consulta el Dashboard operativo desde cualquier resolución, necesito que las tarjetas de indicadores (Total procesados, urgentes, auditorías requeridas y tiempo promedio) se distribuyan armónicamente en 1, 2 o 4 columnas según el ancho disponible.

**Why this priority**: El Dashboard es el punto de partida visual; una mala distribución degrada la experiencia de supervisión ejecutiva y dificulta la detección rápida de alertas críticas.

**Independent Test**: Redimensionar el Dashboard desde 360px hasta 1920px comprobando la reorganización de 1 columna (móvil) a 2 columnas (tablets) y 4 columnas (pantallas anchas), sin solapamiento numérico ni de etiquetas.

**Acceptance Scenarios**:
1. **Given** un dispositivo con ancho menor a 576px, **When** carga el Dashboard, **Then** las tarjetas KPI se muestran en una sola columna vertical con ancho completo.
2. **Given** una pantalla intermedia entre 576px y 992px, **When** carga el Dashboard, **Then** las tarjetas se acomodan en una cuadrícula de 2 columnas equidistantes.
3. **Given** monitores o laptops (≥ 992px), **When** carga el Dashboard, **Then** las tarjetas se alinean horizontalmente en 4 columnas respetando el diseño Bento clínico.

---

### User Story 4 - Visor Documental y Comparador Clínico Dividido (Prioridad: P2)

Como médico que revisa el detalle de un documento y el resultado del triaje en una tablet o laptop con pantalla reducida, necesito poder alternar fluidamente entre la vista del documento original (PDF/imagen) y la ficha de datos clínicos extraídos por la IA mediante pestañas o modo apilado.

**Why this priority**: La auditoría y revisión de diagnósticos requiere contrastar el documento original con la estructuración del LLM; en pantallas compactas ambas secciones no caben en paralelo horizontal sin volverse ilegibles.

**Independent Test**: Abrir `/documentos/:id` o `/auditoria/:id` en 768px y 414px; verificar que el layout divido horizontal pase a un modo vertical apilado o con pestañas de alternancia rápida ("Documento Original" / "Ficha Clínica IA").

**Acceptance Scenarios**:
1. **Given** la pantalla de detalle de documento en desktop (≥ 1200px), **When** se visualiza el expediente, **Then** el visor documental y el panel de metadatos se muestran en dos paneles paralelos lado a lado.
2. **Given** la pantalla de detalle de documento en tablet o móvil (< 1200px), **When** se visualiza el expediente, **Then** la interfaz adopta una disposición apilada verticalmente o presenta un selector de vista (pestañas) manteniendo el zoom y controles del visor 100% operativos.

---

### User Story 5 - Modales, Formularios y Banners de Alerta Táctiles (Prioridad: P3)

Como operador de admisión que registra nuevos pacientes o carga documentos clínicos desde una tablet, necesito que los modales y formularios se adapten a la altura y ancho de la pantalla, manteniendo visibles los botones de acción ("Guardar", "Cancelar") sin que el teclado virtual los tape.

**Why this priority**: Garantiza que las tareas transaccionales (ingreso de datos de pacientes, edición de usuarios, confirmación de auditorías) puedan completarse sin frustración técnica en dispositivos táctiles.

**Independent Test**: Abrir el modal de "Registrar Paciente" en un viewport móvil con teclado emulado; validar que el modal ocupe el 95% del ancho, tenga scroll vertical independiente en el cuerpo y conserve el pie con los botones siempre accesible.

**Acceptance Scenarios**:
1. **Given** cualquier modal del sistema (Registro de Paciente, Edición, Confirmación de Auditoría), **When** se abre en un dispositivo con resolución menor a 768px, **Then** el ancho se ajusta automáticamente al 95-100% del viewport con bordes seguros y scroll interno en el cuerpo del formulario.
2. **Given** una alerta flotante de emergencia (`EmergencyAlertToast`), **When** se emite en un móvil, **Then** se ancla en la parte superior o inferior central ocupando un ancho controlado con botón de cierre táctil accesible sin invadir elementos clave de navegación.

---

### Casos Límite y Consideraciones Especiales (Edge Cases)

- **Cambio dinámico de orientación (Landscape vs. Portrait)**: Si un médico gira una tablet de vertical a horizontal durante la revisión de un documento, el layout debe recalculare sin perder el estado del formulario, la página actual de la tabla ni la sesión activa.
- **Teclado virtual en pantalla**: En dispositivos móviles, la apertura del teclado virtual reduce drásticamente la altura visible del viewport (`vh`). Los modales y campos de formulario deben contar con `overflow-y-auto` y no depender de alturas fijas en píxeles.
- **Títulos y cadenas de texto extremadamente largas**: Nombres de archivos complejos, nombres completos de pacientes o diagnósticos CIE-10 extensos deben contar con reglas de truncamiento inteligente (`truncate`, `text-ellipsis`) con tooltip accesible para no empujar botones fuera de pantalla.
- **Pantallas de ultra alta densidad (Retina / 4K)**: El diseño debe mantenerse centrado con un ancho máximo contenido (`max-w-7xl` o contenedor clínico) sin estirarse desmesuradamente en monitores panorámicos.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE implementar un sistema de rejilla y puntos de interrupción estándar (Mobile: `< 640px`, Tablet: `640px - 1023px`, Desktop: `1024px - 1439px`, Wide: `≥ 1440px`).
- **FR-002**: La navegación principal (`Sidebar`) DEBE colapsar automáticamente a un menú deslizante (off-canvas/drawer) en viewports inferiores a 1024px, con activador de tipo hamburguesa accesible en la cabecera.
- **FR-003**: Todo contenedor de tabla con más de 4 columnas DEBE contar con encapsulamiento en un contenedor con desplazamiento horizontal (`overflow-x-auto`) y bordes visuales que indiquen continuidad de contenido.
- **FR-004**: Los controles de paginación DEBEN ser responsivos: en pantallas móviles (`< 640px`) deben apilarse verticalmente (información de registros arriba, controles de avance/retroceso centrados abajo).
- **FR-005**: Las tarjetas de resumen (KPIs) en Dashboard y Pacientes DEBEN reorganizarse mediante flex/grid responsive (1 columna en `< 576px`, 2 columnas en `576px - 991px`, 4 columnas en `≥ 992px`).
- **FR-006**: Las vistas divididas (Split View) en `/documentos/:id` y `/auditoria/:id` DEBEN reorganizarse a diseño vertical apilado o con pestañas de selección cuando el ancho de pantalla sea menor a 1200px.
- **FR-007**: Los modales de interacción clínica DEBEN tener una altura máxima relativa (`max-h-[90vh]`) con scroll interno en el cuerpo y botones fijos en la cabecera y pie.
- **FR-008**: Los elementos interactivos táctiles (botones, checkboxes, interruptores, selectores) DEBEN tener un área de contacto mínima recomendada de 40x40 píxeles para evitar pulsaciones erróneas en pantallas táctiles.
- **FR-009**: Las notificaciones de guardia en tiempo real (`EmergencyAlertToast`) DEBEN adaptarse al ancho de pantalla en móviles, evitando cubrir la barra de navegación o los botones principales de acción.
- **FR-010**: Ninguna vista del sistema DEBE generar una barra de desplazamiento horizontal en el elemento raíz (`body` o `html`), garantizando un viewport bloqueado en el eje X (`overflow-x-hidden`).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: **0 Desbordamientos Horizontales Involuntarios**: El 100% de las pantallas del sistema renderizan sin barra de scroll horizontal en la ventana principal en anchos de 360px, 390px, 768px, 1024px, 1366px y 1920px.
- **SC-002**: **Tiempo de Tarea en Dispositivos Táctiles**: Los usuarios en tablets clínicas completan las tareas clave de triaje (buscar paciente, ver documento, revisar auditoría) en tiempos equivalentes (margen menor al 10%) respecto a estaciones de escritorio.
- **SC-003**: **Accesibilidad Táctil**: El 100% de los botones y controles interactivos en vistas móviles cuentan con al menos 40px de área de impacto y espaciado mínimo de 8px entre controles contiguos.
- **SC-004**: **Puntuación de Usabilidad Móvil**: Auditorías de Lighthouse o herramientas de usabilidad móvil superan los 90 puntos en rendimiento de diseño y legibilidad en vistas principales (Login, Dashboard, Documentos, Pacientes).

---

## Key Entities & Layout Tokens

- **Breakpoints Estandarizados**:
  - `xs`: `< 480px` (Móviles estándar)
  - `sm`: `≥ 640px` (Móviles grandes y phablets)
  - `md`: `≥ 768px` (Tablets retrato)
  - `lg`: `≥ 1024px` (Tablets apaisadas y laptops compactas)
  - `xl`: `≥ 1280px` (Escritorios estándar)
  - `2xl`: `≥ 1536px` (Estaciones de trabajo clínicas de alta resolución)
- **Componentes Afectados**:
  - `MainLayout` / `Sidebar` / `Header`
  - `DocumentTable` / Paginación
  - `Dashboard` (Bento Grid)
  - `DocumentViewer` / `ExtractedData` / `AuditDetail`
  - `PatientsManagementView` / `UsersManagementView`
  - `EmergencyAlertToast` / Modales de captura

---

## Assumptions & Boundaries

- **Tailwind CSS como Motor de Estilizado**: Se aprovechan las clases utilitarias responsivas de Tailwind CSS (`sm:`, `md:`, `lg:`, `xl:`) y las variables de diseño médico ya definidas en la aplicación.
- **Soporte Navegadores Modernos**: Se garantiza compatibilidad completa en las versiones recientes de Google Chrome, Safari Mobile (iOS 15+), Firefox y Microsoft Edge.
- **No Requiere App Nativa**: El sistema se mantiene como una Single Page Application (SPA) web responsive accesible directamente desde el navegador, sin necesidad de compilar paquetes nativos iOS/Android en esta fase.
