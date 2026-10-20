# Feature Specification: Visor interactivo y robusto de documentos PDF clínicos con skeleton loader y zoom

**Feature Branch**: `dev-wilmer-gulcochia` (Rama de desarrollo activa)  
**Referencia de Plan de Trabajo**: Tarea 5.2 (`plan de trabajo/PLAN_DE_TRABAJO_FRONTEND_REACT.md`)  
**Issue de GitHub**: [FE-14] #71 (Visor Interactivo de PDFs: Skeleton Loader, Pantalla Completa y Descarga)  
**Created**: 2026-10-18  
**Updated**: 2026-10-20 (Alineación E2E con streaming backend, barra de herramientas en 2 niveles y criterios de aceptación frontend)  
**Status**: Completed / Implemented in `dev-wilmer-gulcochia`  

**Input**: User description & Issue [FE-14]: "Como Médico Especialista, quiero visualizar documentos clínicos en PDF con un visor interactivo que incluya indicador de carga (skeleton loader), controles de zoom, modo pantalla completa y descarga directa del archivo original. Criterios de aceptación: Skeleton loader fluido mientras se completa la descarga del documento para mostrarse en pantalla; Botón de alternancia a pantalla completa (Full Screen API); Botón de descarga directa del PDF original; Comportamiento responsivo en dispositivos de escritorio y tablets clínicas."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualización Fluida con Indicador de Carga Animado (Priority: P1) 🎯 MVP

Como profesional de la salud o evaluador médico en el sistema hospitalario, quiero visualizar un indicador de carga animado (skeleton loader) mientras se descarga y prepara el documento PDF clínico, para tener retroalimentación visual inmediata y saber con certeza que el documento está en proceso de despliegue en lugar de observar una pantalla vacía o congelada.

**Why this priority**: En un entorno hospitalario de alta demanda, la retroalimentación visual inmediata durante la carga de expedientes y recetas es crítica para evitar la percepción de fallo del sistema y reducir la frustración del personal médico.

**Independent Test**: Se puede verificar de forma independiente abriendo cualquier documento clínico PDF en el visor (`/documentos/:id` o `/auditoria/:id`) y observando que el esqueleto de carga animado (`role="status"`, animación `animate-pulse`) se presenta instantáneamente y permanece visible hasta que el contenido del documento esté completamente renderizado.

**Acceptance Scenarios**:

1. **Given** un documento clínico PDF seleccionado para su revisión, **When** el usuario solicita visualizar el archivo y la descarga o renderizado está en curso, **Then** el sistema presenta un esqueleto de carga animado fluido con Tailwind CSS que ocupa el área de visualización sin parpadeos.
2. **Given** el visor mostrando el skeleton loader animado, **When** el documento PDF completa su carga exitosamente mediante el evento `onLoad`, **Then** el esqueleto de carga se oculta suavemente y se muestra el documento interactivo listo para su inspección médica.

---

### User Story 2 - Control de Ampliación y Alternancia a Pantalla Completa (Priority: P2)

Como médico o coordinador clínico, quiero ajustar el nivel de zoom (acercar, alejar y reiniciar) y alternar a pantalla completa mediante una barra de herramientas accesible, para inspeccionar con precisión firmas, sellos, dosis farmacológicas y notas manuscritas presentes en documentos clínicos complejos.

**Why this priority**: Los documentos clínicos escaneados con frecuencia presentan tipografías pequeñas o anotaciones marginales que requieren ampliación selectiva y un área de visualización máxima sin distracciones para emitir un juicio clínico seguro.

**Independent Test**: Se puede probar abriendo un documento PDF y accionando los botones de la barra de herramientas para acercar (+25%), alejar (-25%), restablecer al 100% y activar/desactivar la vista a pantalla completa, comprobando que la vista responde inmediatamente sin desbordar los límites del visor.

**Acceptance Scenarios**:

1. **Given** un documento PDF visible en el visor, **When** el usuario presiona el botón de acercar zoom (+), **Then** el contenido aumenta su escala visual de manera progresiva hasta un límite máximo seguro (250%).
2. **Given** un documento con zoom aplicado, **When** el usuario presiona el botón de restablecer zoom o alejar (-), **Then** la escala se reduce progresivamente (mínimo 50%) o vuelve al 100% de su visualización estándar al presionar el indicador central.
3. **Given** el visor en su tamaño integrado habitual, **When** el usuario presiona el botón de pantalla completa, **Then** el visor se expande para ocupar la totalidad del monitor mediante la Full Screen API nativa del navegador (con fallback CSS de ventana completa `fixed inset-0 z-50`), actualizando el ícono y tooltip para permitir volver al modo regular.

---

### User Story 3 - Descarga Directa y Manejo Resiliente de Fallos (Priority: P3)

Como personal administrativo o clínico, quiero disponer de un botón de descarga directa del archivo original y contar con una alternativa de contingencia si el visor embebido no puede renderizar el PDF, para garantizar la continuidad asistencial sin interrupciones operativas.

**Why this priority**: La disponibilidad ininterrumpida de los documentos médicos es vital; si un navegador bloquea complementos o un archivo presenta advertencias de compatibilidad embebida, el profesional médico debe poder obtener el documento original de manera inmediata.

**Independent Test**: Se puede probar haciendo clic en el botón de descarga para obtener el archivo original en el almacenamiento local con su nombre canónico, y simulando un fallo de carga embebida para comprobar la presencia del mensaje informativo y el enlace de descarga directa.

**Acceptance Scenarios**:

1. **Given** un documento clínico disponible, **When** el usuario hace clic en el botón de descarga de la barra de herramientas, **Then** el navegador inicia la descarga directa del archivo original (PDF o imagen) preservando su nombre de archivo clínico.
2. **Given** una situación donde el visor embebido experimenta un error de carga o restricción de visualización por políticas de seguridad del navegador, **When** el renderizado falla o expira el tiempo de espera, **Then** el sistema presenta un estado de error claro con un encabezado descriptivo accesible y un panel de contingencia que ofrece botones directos para descargar y abrir el archivo en una pestaña externa.

---

### Edge Cases

- **Conexiones hospitalarias lentas o documentos de gran volumen**: El skeleton loader debe permanecer visible y animado durante tiempos de respuesta prolongados sin bloquear la interfaz general.
- **Transición entre documentos sucesivos**: Si el usuario cambia de documento clínico mientras otro estaba cargando o ampliado, el visor debe reiniciar sus niveles de zoom a su valor base (100%), restablecer el skeleton loader y limpiar posibles estados de error previos.
- **Restricciones de seguridad del navegador para visores embebidos**: En entornos hospitalarios con políticas estrictas de seguridad (sandbox o bloqueo de plugins) que impidan la visualización embebida de PDFs, debe activarse el mecanismo de contingencia sin romper el layout.
- **Redimensionamiento de pantalla y rotación de tabletas**: Al cambiar entre orientación vertical y horizontal o redimensionar la ventana (desde 768px hasta resoluciones 4K), la barra de herramientas y el documento deben adaptarse fluidamente sin desbordamientos horizontales ni colisión de botones.
- **Disponibilidad física del archivo binario**: Si el archivo físico original no existe en el sistema de almacenamiento (LOCAL o OCI), el backend debe responder HTTP 404 estructurado y el frontend desplegar la alerta clínica sin que la aplicación se congele.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar un esqueleto de carga animado (skeleton loader) con Tailwind CSS (`role="status"`, `animate-pulse`) en el contenedor principal mientras el documento PDF se encuentra descargando y preparando para visualización.
- **FR-002**: El sistema DEBE ocultar el skeleton loader y presentar el documento en pantalla una vez que el visor embebido (`<object>` o `<iframe>`) confirme la disponibilidad del recurso mediante el evento `onLoad`.
- **FR-003**: El sistema DEBE incluir una barra de herramientas superior accesible y organizada (`role="toolbar"`) que concentre las acciones de navegación y visualización clínica.
- **FR-004**: La barra de herramientas DEBE proporcionar controles de zoom interactivos: botón para acercar (+25%), botón para alejar (-25%) y selector/botón de restablecimiento a escala original (100%), delimitados entre 50% y 250%.
- **FR-005**: La barra de herramientas DEBE incluir un botón de alternancia a pantalla completa que active y desactive el modo de pantalla completa mediante la API del navegador (Full Screen API) con fallback fluido a clase CSS `fixed inset-0 z-50`.
- **FR-006**: La barra de herramientas DEBE incorporar un botón para la descarga directa del archivo PDF o imagen original con preservación del nombre del archivo clínico.
- **FR-007**: El sistema DEBE detectar condiciones de error en la carga del documento embebido y mostrar un panel de contingencia explicativo (`role="alert"`) con opciones directas para descargar o abrir el archivo original en una pestaña independiente (`target="_blank"`).
- **FR-008**: La interfaz del visor DEBE ser completamente responsiva, garantizando usabilidad ergonómica tanto en monitores de escritorio clínicos como en tabletas médicas en orientación vertical y horizontal (desde 768px de ancho).
- **FR-009**: Al cambiar el identificador o URL del documento recibido en las propiedades, el sistema DEBE restablecer el zoom a 100%, reiniciar el indicador de carga y limpiar estados de error previos.
- **FR-010**: El backend DEBE proveer un endpoint de streaming binario `GET /api/v1/documents/{documento_id}/file` con cabeceras `Content-Disposition: inline` y `Content-Type` adecuado para servir los archivos originales PDF, PNG, JPG y WebP persistidos en almacenamiento.
- **FR-011**: El cliente API `documentsApi.ts` DEBE proyectar la URL de streaming en el campo `url_archivo` para todos los documentos consultados en el sistema de triaje y auditoría.

---

### Key Entities

- **Documento Clínico**: Representa el expediente o archivo PDF/imagen sometido a visualización, caracterizado por su identificador único (`documento_id`), nombre original (`nombre_archivo`), tipo MIME y su URL de streaming (`url_archivo`).
- **Endpoint de Streaming Binario**: Ruta REST autenticada (`GET /api/v1/documents/{documento_id}/file`) que entrega el flujo de bytes del documento con cabeceras de visualización embebida (`inline`).
- **Estado del Visor Clínico**: Conjunto reactivo de variables que controlan la experiencia de usuario, incluyendo el estado de carga (`idle`, `loading`, `ready`, `error`), el factor de ampliación (zoom: 0.5 a 2.5), el estado de pantalla completa (`isFullscreen`), y el mensaje de contingencia en caso de fallo.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de visualización de documentos presentan retroalimentación visual inmediata mediante el skeleton loader en menos de 100 ms tras la selección del archivo.
- **SC-002**: Los profesionales médicos pueden alternar al modo de pantalla completa y salir de él con una sola interacción (1 clic o toque táctil, o tecla `Esc`).
- **SC-003**: Los usuarios disponen de controles de zoom con respuesta visual inmediata (menor a 150 ms) para ampliar hasta al menos un 200% y restablecer a la vista estándar del 100%.
- **SC-004**: En escenarios de fallo de renderizado embebido, el 100% de los usuarios reciben una opción de contingencia de descarga directa accesible en menos de 1 segundo tras suscitarse el error.
- **SC-005**: La interfaz del visor y su barra de herramientas mantienen total legibilidad y operatividad en resoluciones desde tabletas (768px de ancho) hasta estaciones clínicas de alta definición (1080p y 4K), sin desbordamientos horizontales ni colisión de botones.
- **SC-006**: La suite de pruebas de `DocumentViewer.test.tsx` ejecuta 14 pruebas unitarias con un 100% de aprobación en verde en Vitest.

---

## Assumptions & Integrations

- Los archivos físicos se almacenan bajo la convención canónica `backend/storage/recibidos/<documento_id>/original.<ext>` (o almacenamiento OCI equivalente) y son transmitidos por el endpoint `/api/v1/documents/{documento_id}/file`.
- Los navegadores web de las estaciones clínicas soportan la API nativa de pantalla completa (`requestFullscreen` / `exitFullscreen`) o un mecanismo de fallback a pantalla completa de ventana.
- El visor conserva compatibilidad dual con la visualización de documentos PDF e imágenes clínicas (JPG, PNG, WebP), manteniendo una experiencia unificada en el componente.
- Los estilos y maquetación respetan la directiva de diseño con Tailwind CSS y los lineamientos de accesibilidad hospitalaria sin sobrecarga de elementos decorativos innecesarios.
