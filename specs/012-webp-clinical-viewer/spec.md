# Feature Specification: Soporte Integral para Carga y Visualización de Imágenes WebP en Visor Clínico

**Feature Branch**: `012-webp-clinical-viewer`

**Created**: 2026-10-17

**Status**: Draft

**Input**: User description: "Se necesita un soporte integral para carga y visualización de imágenes WebP en visor clínico. Es decir, se requiere que:
- En frontend/src/components/documents/DocumentUploader.tsx, incluir image/webp y extensión .webp en los tipos aceptados.
- En frontend/src/components/documents/DocumentViewer.tsx, asegurar que la etiqueta <img> renderice URLs de tipo WebP.
- Añadir manejo de error si el navegador no soporta el formato o el archivo está corrupto.
- Crear prueba unitaria en src/tests/components/documents/DocumentViewer.test.tsx.

Los criterios de aceptación son los siguientes:
- Uploader permite seleccionar y arrastrar archivos .webp.
- Visor renderiza imágenes WebP con zoom y adaptación de contenedor.
- Mensaje descriptivo si el archivo no puede decodificarse.
- Pruebas unitarias de carga y renderizado aprobadas."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Carga y Selección de Documentos Médicos en Formato WebP (Priority: P1)

Como personal administrativo o médico en admisión hospitalaria, deseo poder seleccionar o arrastrar archivos con formato WebP (`.webp`, MIME `image/webp`) en el componente de carga de documentos clínicos (`DocumentUploader.tsx`), para que el sistema acepte imágenes diagnósticas comprimidas eficientemente sin rechazos de formato.

**Why this priority**: Es el punto de entrada crítico de la funcionalidad; sin la admisión del tipo de archivo y extensión `.webp` en la zona de drop y en el selector del sistema de archivos, los usuarios no pueden ingresar este tipo de imágenes a MediFlow.

**Independent Test**:
- Arrastrar un archivo `estudio_clinico.webp` hacia la zona de carga (dropzone) de `DocumentUploader`.
- Seleccionar mediante el diálogo del explorador de archivos un archivo `.webp`.
- Comprobar que el archivo es aceptado sin mostrar alertas de error de formato y que su información básica (nombre, peso) se visualiza correctamente en la vista previa previa al procesamiento.

**Acceptance Scenarios**:

1. **Given** un usuario situado en la vista de carga de documentos clínicos, **When** arrastra un archivo con extensión `.webp` (MIME `image/webp`) dentro del dropzone, **Then** el uploader valida exitosamente el formato y prepara el archivo para su envío.
2. **Given** un usuario interactuando con el selector de archivos nativo del uploader, **When** abre el diálogo de selección, **Then** los archivos con extensión `.webp` y tipo MIME `image/webp` están habilitados en los filtros de selección.
3. **Given** un usuario intentando subir un archivo WebP que supera los 10 MB, **When** se evalúa el archivo, **Then** el uploader rechaza el archivo indicando que excede el límite permitido de 10 MB.

---

### User Story 2 - Visualización y Renderizado Clínico de Imágenes WebP con Adaptación y Zoom (Priority: P1)

Como médico o auditor clínico, deseo visualizar documentos e imágenes médicas en formato WebP dentro del visor integrado (`DocumentViewer.tsx`), con ajuste automático al contenedor y controles ergonómicos de zoom y pantalla completa, para analizar diagnósticos y detalles anatómicos con alta fidelidad.

**Why this priority**: El personal de salud requiere examinar con precisión las prescripciones, placas o recetas en formato WebP directamente en la interfaz clínica sin requerir aplicaciones externas.

**Independent Test**:
- Cargar un documento con URL a una imagen WebP en `DocumentViewer`.
- Verificar que la etiqueta de imagen renderiza la URL de forma fluida adaptándose al contenedor.
- Probar las acciones de pantalla completa / expansión y controles de adaptación visual (zoom in/out / reset o escalado proporcional).

**Acceptance Scenarios**:

1. **Given** un documento con extensión `.webp` o URL a imagen WebP, **When** se abre en `DocumentViewer`, **Then** la imagen se renderiza en el contenedor visual con la etiqueta correspondiente y ajuste proporcional (`objectFit: contain`).
2. **Given** un documento WebP desplegado en el visor, **When** el usuario activa el modo de pantalla completa o ajusta la vista, **Then** el contenedor adapta su escala manteniendo la relación de aspecto sin distorsionar la imagen clínica.

---

### User Story 3 - Manejo Resiliente de Errores ante Archivos Corruptos o Fallo de Decodificación (Priority: P2)

Como usuario clínico, si cargo o intento visualizar una imagen WebP dañada, corrupta o cuyo formato no pueda ser decodificado por el navegador, deseo recibir un mensaje claro, amigable y explicativo en lugar de una pantalla en blanco o un icono de imagen rota, con opciones para reintentar o abrir externamente.

**Why this priority**: En un entorno hospitalario crítico, un fallo silencioso o confuso genera desconfianza y retrasos en la atención; un mensaje explícito permite al usuario solicitar un reenvío del documento.

**Independent Test**:
- Proveer a `DocumentViewer` una URL con un archivo `.webp` intencionalmente corrupto o inválido.
- Disparar el evento de fallo de carga (`onError`).
- Verificar que se muestra un estado visual de error descriptivo ("No fue posible decodificar o cargar la imagen clínica...") con icono de alerta y opción de abrir en pestaña independiente.

**Acceptance Scenarios**:

1. **Given** una imagen WebP dañada o con datos corruptos, **When** el navegador intenta renderizarla y falla el renderizado, **Then** el visor oculta la imagen rota y muestra un componente de alerta clínica descriptivo informando el problema de decodificación.
2. **Given** el estado de error por imagen no decodificable, **When** el usuario consulta las opciones, **Then** se le ofrece la acción de abrir la URL original en una pestaña independiente o contactar a soporte.

---

### User Story 4 - Verificación Automatizada y Pruebas Unitarias Robustas (Priority: P2)

Como desarrollador y auditor de calidad del proyecto MediFlow, deseo disponer de pruebas unitarias exhaustivas en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` (y uploader), para garantizar el cumplimiento incondicional de la Regla de Oro y la Constitución (100% pruebas en verde con Vitest).

**Why this priority**: Salvaguarda la calidad del software hospitalario y previene regresiones en futuras versiones según el principio Test-First de MediFlow.

**Independent Test**:
- Ejecutar `vitest run src/tests/components/documents/DocumentViewer.test.tsx` en el frontend.
- Validar que todas las aserciones pasan en verde (renderizado de WebP, manejo de fallback ante error, visualización de estado vacío y botones de control).

**Acceptance Scenarios**:

1. **Given** la suite de pruebas unitarias de `DocumentViewer`, **When** se ejecutan con Vitest, **Then** se validan los casos de renderizado de imagen WebP, atributos de accesibilidad, evento `onError` y adaptación de contenedor.

---

### Edge Cases

- **Archivo corrupto o incompleto**: Si el archivo posee extensión `.webp` pero su cabecera binaria está incompleta o alterada, el evento `onError` de la imagen se activa y el visor presenta la tarjeta de error descriptiva.
- **Navegador desactualizado sin soporte para WebP**: Si el entorno del usuario no tiene decodificador WebP nativo, la carga falla elegantemente disparando la vista alternativa de error y descarga.
- **Extensión simulada**: Si un archivo no compatible es renombrado a `.webp`, el navegador fallará al renderizarlo y se atrapará en el manejador de error visual sin romper el árbol de componentes de React.
- **Imagen WebP de grandes dimensiones**: La imagen debe mantener contención estricta (`maxHeight`, `maxWidth: 100%`, `objectFit: contain`) para no desbordar el contenedor ni los márgenes de la interfaz clínica.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El componente `DocumentUploader` DEBE incluir el tipo MIME `image/webp` y la extensión `.webp` en la lista de tipos permitidos (`ALLOWED_TYPES` y expresión regular de validación).
- **FR-002**: El atributo `accept` del elemento `<input type="file">` en `DocumentUploader` DEBE incorporar `.webp` y `image/webp` para habilitar la selección nativa en los exploradores de archivos.
- **FR-003**: El texto de ayuda del uploader DEBE reflejar claramente la admisión de formatos `PDF, JPG, PNG y WebP, hasta 10 MB`.
- **FR-004**: El componente `DocumentViewer` DEBE reconocer URLs y nombres de archivo con extensión `.webp` como imágenes clínicas, renderizándolas mediante la etiqueta `<img>` con adaptación responsive al contenedor.
- **FR-005**: El componente `DocumentViewer` DEBE implementar un manejador de error (`onError`) en la etiqueta `<img>` para capturar fallos de decodificación o archivos corruptos.
- **FR-006**: En caso de fallo de carga de la imagen, el visor DEBE presentar un mensaje descriptivo y profesional que explique el fallo de decodificación o soporte y ofrezca alternativas al usuario.
- **FR-007**: El visor DEBE mantener la funcionalidad de pantalla completa / expansión y adaptación ergonómica tanto para imágenes WebP como para los formatos previamente soportados.
- **FR-008**: Se DEBE proveer una suite completa de pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` que verifique el renderizado exitoso de WebP, la activación del estado de error al fallar la carga, y la interacción de controles.

### Key Entities

- **Documento Clínico Adjunto**: Archivo original proporcionado por el usuario o sistema (PDF, JPG, PNG o WebP), caracterizado por `fileName`, `fileUrl` y tamaño en bytes.
- **Estado de Visualización**: Estado del visor que controla modo expandido (`isExpanded`), estado de error de carga (`hasError` / `errorMessage`) y tipo de contenido renderizado (PDF vs Imagen Médica).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de los intentos de selección o arrastre de archivos `.webp` válidos de menos de 10 MB son aceptados por `DocumentUploader` sin errores de validación de formato.
- **SC-002**: El 100% de los archivos WebP válidos se renderizan visualmente dentro de `DocumentViewer` ajustados al contenedor en menos de 1 segundo tras la recepción de la URL.
- **SC-003**: Ante archivos WebP corruptos o inaccesibles, el 100% de las instancias muestran un mensaje descriptivo sin producir excepciones no capturadas ni pantallas blancas.
- **SC-004**: El 100% de las pruebas unitarias en `frontend/src/tests/components/documents/DocumentViewer.test.tsx` pasan satisfactoriamente en verde (`vitest run`).

---

## Assumptions

- Se asume que el backend ya maneja el almacenamiento y entrega de blobs/archivos independientemente del formato mientras el mime-type sea estándar.
- Se asume que los navegadores modernos utilizados en el entorno clínico hospitalario soportan de forma nativa la especificación de imágenes WebP (Chrome 32+, Firefox 65+, Safari 14+, Edge 18+).
- Se asume que las pruebas unitarias se ejecutan utilizando el entorno de pruebas configurado en el proyecto (`vitest` + `@testing-library/react`).

