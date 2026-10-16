# Feature Specification: Ingesta Híbrida Multimodal de Imágenes y Documentos Escaneados

**Feature Branch**: `009-multimodal-vision-ocr`

**Created**: 2026-10-12

**Status**: Draft

**Input**: User description: "Ingesta híbrida multimodal de imágenes y documentos escaneados con Gemini Vision y fallback local a Tesseract OCR"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Procesamiento Clínico Automatizado de Imágenes Médicas y Fotografías (Priority: P1)

Como personal de admisión hospitalaria o médico de triaje,
quiero cargar fotografías directas o capturas de recetas, volantes médicos e informes de interconsulta (en formatos PNG, JPEG o WebP),
para que el sistema interprete visualmente el contenido del documento, extraiga los datos del paciente y el diagnóstico, y clasifique la urgencia clínica sin requerir transcripción manual.

**Why this priority**:
Actualmente el sistema procesa con éxito documentos PDF con texto embebido, pero en la práctica médica real (urgencias, ambulancias, consultorios periféricos) una gran parte de los ingresos clínicos llega como fotos de recetas, capturas de pantalla de chats médicos o documentos impresos fotografiados. Habilitar la comprensión visual directa es el núcleo para desbloquear la operatividad clínica en tiempo real.

**Independent Test**:
Puede probarse cargando una imagen nítida (JPG/PNG) de una orden de atención o receta médica a través del endpoint o interfaz de triaje. El sistema debe completar la extracción de datos clínicos (paciente, diagnóstico, CIE-10) con alta confianza y derivar el caso a su cola correspondiente sin intervención humana.

**Acceptance Scenarios**:
1. **Given** un archivo de imagen válido (JPEG, PNG o WebP) que contiene una orden médica legible, **When** el usuario lo sube al canal de triaje, **Then** el motor de visión multimodal procesa visualmente el documento, extrae los datos clínicos del paciente, asigna la prioridad clínica y registra el estado como `procesado`.
2. **Given** una imagen con orientación no estándar o tipografía diversa, **When** se procesa en la etapa de ingesta, **Then** el modelo de visión interpreta adecuadamente la estructura del documento y normaliza el contenido textual para las etapas subsiguientes.

---

### User Story 2 - Ingesta de Documentos PDF Escaneados sin Capa de Texto (Priority: P2)

Como coordinador médico o enfermero de triaje,
quiero subir archivos PDF correspondientes a documentos físicos escaneados (donde no existe texto seleccionable embebido),
para que el sistema detecte automáticamente la ausencia de texto vectorial, procese las páginas como imágenes de alta resolución mediante el motor multimodal y obtenga los datos clínicos de manera transparente.

**Why this priority**:
Muchos hospitales y centros de salud digitalizan historias clínicas en escáneres multifuncionales que generan PDFs que son esencialmente imágenes encapsuladas. Si el extractor de texto plano falla o devuelve texto vacío, el flujo no debe detenerse ni descartar el archivo.

**Independent Test**:
Puede probarse subiendo un PDF generado exclusivamente a partir de escaneos (sin texto seleccionable). El sistema debe detectar la condición de escaneo, aplicar el procesamiento visual multimodal a las páginas y retornar los datos estructurados con el mismo nivel de detalle que un PDF digital.

**Acceptance Scenarios**:
1. **Given** un PDF escaneado donde la extracción de texto estándar obtiene una cadena vacía o residual inferior al umbral mínimo, **When** el agente ejecuta la fase de ingesta, **Then** el sistema transforma las páginas en representaciones visuales y las envía al motor de visión multimodal, recuperando el contenido clínico completo.
2. **Given** un PDF multipágina escaneado, **When** se realiza la ingesta visual, **Then** el sistema procesa las páginas relevantes, consolida el texto obtenido y lo transfiere al nodo de extracción estructurada.

---

### User Story 3 - Resiliencia Hospitalaria mediante Mecanismo de Respaldo Local (Priority: P3)

Como administrador hospitalario o personal de sistemas,
quiero que ante contingencias externas (indisponibilidad temporal del servicio en la nube, agotamiento de cuota de API de visión o caída de conectividad de salida),
el sistema active automáticamente un motor de reconocimiento óptico de caracteres (OCR) local que intente recuperar el texto del documento para continuar el procesamiento o derivar a auditoría humana con diagnóstico claro.

**Why this priority**:
En un entorno clínico hospitalario 24/7, la dependencia absoluta de un único servicio externo de visión puede crear cuellos de botella ante interrupciones de red. Disponer de un mecanismo de respaldo por degradación elegante asegura continuidad operativa.

**Independent Test**:
Puede probarse simulando la falla o desconexión del servicio de visión primaria al cargar una imagen. El sistema debe capturar el error, activar de inmediato el motor OCR local de contingencia, extraer el texto legible y, en caso de que ambos fallen, derivar el caso a `pendiente_auditoria` con un mensaje explicativo detallado sin lanzar excepciones no controladas.

**Acceptance Scenarios**:
1. **Given** una imagen cargada y el servicio de visión en la nube no disponible o con cuota agotada, **When** falla la llamada principal de visión, **Then** el sistema conmuta automáticamente al motor OCR local, extrae el texto disponible y prosigue con la canalización de triaje.
2. **Given** una imagen ilegible o degradada donde tanto el motor multimodal como el OCR de respaldo no logran extraer información suficiente, **When** concluye la fase de ingesta, **Then** el sistema marca el documento como `pendiente_auditoria` (HITL) con causa `"Fallo en reconocimiento visual y OCR local"` y preserva la integridad del registro en la base de datos.

---

### Edge Cases

- **Imágenes de muy baja resolución o borrosas**: El sistema debe detectar que la calidad es insuficiente para una extracción confiable, registrar confianza baja (< 0.70) y enrutar a auditoría médica asistida (`pendiente_auditoria`).
- **Formatos de archivo no soportados o corruptos**: Si se envía un archivo dañado o con extensión adulterada, el sistema debe responder con HTTP 400 Bad Request o capturar el fallo en ingesta sin colapsar el servicio del agente.
- **PDFs mixtos (páginas con texto digital y páginas escaneadas)**: Si la extracción digital devuelve texto significativo de ciertas páginas pero incompleto en otras, el sistema debe evaluar el contenido y complementar visualmente si el texto extraído es inferior a los requisitos mínimos.
- **Límite de tamaño o páginas**: Para documentos escaneados voluminosos, el sistema debe procesar las páginas clínicas prioritarias dentro de límites razonables de tiempo de ejecución (evitando timeouts de solicitud HTTP).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE admitir la ingesta directa de archivos de imagen en formatos estándar clínicos (`image/jpeg`, `image/png`, `image/webp`).
- **FR-002**: El sistema DEBE detectar automáticamente si un archivo PDF carece de texto digital embebido o contiene texto insuficiente (PDF escaneado/rasterizado).
- **FR-003**: El sistema DEBE emplear un motor de visión multimodal como estrategia primaria para la lectura, transcripción y comprensión de imágenes y páginas escaneadas.
- **FR-004**: El sistema DEBE implementar un mecanismo de contingencia (*fallback*) basado en motor de reconocimiento óptico de caracteres (OCR) local ante cualquier excepción, timeout o agotamiento de cuota del motor primario de visión.
- **FR-005**: El sistema DEBE normalizar el texto e información clínica extraída por cualquiera de los motores visuales para que alimente de forma transparente a los nodos de extracción estructurada, clasificación CIE-10 y enrutamiento.
- **FR-006**: Si ambos motores (visión primaria y OCR de respaldo) fallan o la calidad visual impide la extracción, el sistema DEBE registrar el incidente de forma segura, asignar estado `pendiente_auditoria` y transferir el documento a la bandeja de Human-in-the-Loop (HITL) sin interrumpir el servicio ni generar excepciones 500.
- **FR-007**: El sistema DEBE registrar en la trazabilidad del documento el método de extracción empleado (`TEXT_EXTRACTION`, `MULTIMODAL_VISION`, `LOCAL_OCR` o `FALLBACK_AUDIT`) para fines de auditoría técnica y médica.

### Key Entities *(include if feature involves data)*

- **DocumentoTriaje**: Entidad que almacena el documento procesado, su tipo MIME (`application/pdf`, `image/jpeg`, `image/png`), canal de origen, estado de procesamiento (`procesado`, `pendiente_auditoria`) y datos clínicos extraídos.
- **MetadatosIngesta**: Información del proceso de ingesta que detalla el método de extracción aplicado (`metodo_extraccion`), páginas procesadas, advertencias de resolución y estado del servicio de visión.
- **AuditoriaTriaje**: Registro inmutable de eventos que detalla cada transición de estado, errores encontrados en el reconocimiento visual y motivos de derivación asistida a coordinación médica.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El sistema debe procesar exitosamente al menos el 95% de las imágenes clínicas y recetas médicas legibles en formatos JPEG/PNG/WebP sin intervención humana inicial.
- **SC-002**: Los documentos PDF escaneados sin texto embebido deben transitar automáticamente al motor visual logrando una tasa de extracción clínica superior al 90%.
- **SC-003**: Ante fallos intencionales o caídas de conexión del motor de visión en la nube, el sistema debe activar el OCR local en menos de 2 segundos y continuar el ciclo de triaje sin registrar fallos fatales de servicio.
- **SC-004**: En el 100% de los casos de imágenes corruptas o totalmente ilegibles, el sistema debe derivar el documento a la cola de auditoría médica (`pendiente_auditoria`) en menos de 5 segundos, preservando la información del paciente y el motivo exacto del fallo.
- **SC-005**: 0 regresiones en el procesamiento de documentos PDF digitales estándar existentes con 100% de las pruebas automatizadas en verde.

## Assumptions

- La API externa de visión multimodal cuenta con soporte nativo para análisis de imágenes médicas y documentos en formato visual bajo la clave de API configurada en el sistema.
- Para la conversión de páginas de PDF escaneado a imágenes y OCR local, el entorno cuenta con librerías estándar de procesamiento de imágenes (`Pillow`, `pdf2image` o utilidades equivalentes en Python).
- Si el motor OCR local requiere binarios auxiliares no disponibles en el entorno anfitrión, el sistema debe capturar limpiamente la excepción `FileNotFoundError` o advertencia correspondiente y derivar a auditoría asistida sin provocar el colapso del proceso principal.
- Los documentos fotográficos ingresados contienen órdenes médicas, recetas o resúmenes clínicos en idioma español orientados a triaje ambulatorio o de urgencias.
