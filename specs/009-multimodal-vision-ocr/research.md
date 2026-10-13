# Research: Ingesta Híbrida Multimodal con Gemini Vision y OCR Local

**Feature**: `009-multimodal-vision-ocr`  
**Date**: 2026-10-12  
**Status**: Completed  

---

## 1. Integración de Visión Multimodal con Google Gemini

### Decisión
Utilizar la capacidad multimodal nativa de `langchain_google_genai` (`ChatGoogleGenerativeAI`) pasando bloques estructurados de tipo `image_url` con data URI en base64 (`data:{mime_type};base64,{data}`), complementado por un método `completar_multimodal()` en `LLMService`.

### Justificación
- `ChatGoogleGenerativeAI` ya está configurado e integrado en el proyecto bajo el modelo `gemini-3.5-flash-lite` (y compatible con otros modelos de la familia Gemini).
- La API de LangChain unifica el envío de imágenes vía `HumanMessage(content=[{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}}])`.
- No requiere instalar SDKs adicionales ni dependencias pesadas.
- Permite que Gemini procese directamente la imagen y entregue la transcripción completa y estructurada del documento clínico en español en una sola llamada.

### Alternativas Evaluadas
- **Google GenAI SDK nativo (`google-genai` / `google.generativeai`)**: Requeriría mantener dos clientes distintos (uno para LangGraph/LangChain y otro para visión directa). Descartado por redundancia y complejidad.
- **OpenAI Vision (`gpt-4o-mini`)**: Ya está soportado de forma idéntica en el formato `image_url` de LangChain si se conmuta a proveedor OpenAI.

---

## 2. Detección y Rasterización de PDFs Escaneados

### Decisión
Aprovechar `PyMuPDF` (`fitz`), que ya es una dependencia activa y probada en el proyecto, para:
1. Inspeccionar el volumen de texto embebido devuelto por `page.get_text()`.
2. Si el texto agregado de todo el documento es menor a 50 caracteres (umbral configurable que identifica escaneos puros), activar el flujo visual.
3. Renderizar las primeras páginas del PDF (hasta 3 páginas clínicas para evitar exceder latencias y cuotas) como pixmaps RGB de alta resolución (`fitz.Matrix(2, 2)` = ~144 DPI), exportarlas a JPEG/PNG en memoria y enviarlas a `completar_multimodal()`.

### Justificación
- `PyMuPDF` compila C internamente (MuPDF) y realiza rasterización ultra-rápida (menos de 50ms por página) sin requerir `poppler-utils` ni utilidades binarias del sistema operativo.
- Evita que un PDF escaneado pase con `texto_extraido = ""` al nodo de extracción y cause una falla innecesaria.

### Alternativas Evaluadas
- **`pdf2image`**: Requiere `pdftoppm` (paquete Linux `poppler-utils`) instalado a nivel de SO. Si el contenedor o máquina anfitriona no lo tiene, fallará con `FileNotFoundError`. Descartado en favor de `fitz`.

---

## 3. Mecanismo de Fallback y Resiliencia con OCR Local (Tesseract)

### Decisión
Implementar un bloque de contingencia de dos capas (*Failover Chain*):
1. **Capa Primaria**: Gemini Vision multimodal.
2. **Capa Secundaria (Fallback)**: Si Gemini Vision falla (red, HTTP 429, timeout o credenciales ausentes), capturar la excepción e intentar de inmediato el OCR local con `pytesseract` y `Pillow`.
3. **Capa Terciaria (Degradación Elegante / HITL)**: Si `pytesseract` tampoco está disponible en el sistema (ej. falta el binario `/usr/bin/tesseract`), capturar la excepción `FileNotFoundError` o `TesseractNotFoundError` de forma controlada, registrar en los logs y en el estado `AgentState`:
   - `texto_extraido = ""`
   - `error_mensaje = "Fallo en motor de visión multimodal y OCR local no disponible: [detalle]"`
   - El agente continúa su flujo estándar hasta el nodo `confidence`, donde la ausencia de datos clínicos genera confianza `0.0` y enruta automáticamente a la cola `pendiente_auditoria` (HITL) para revisión humana por el médico o coordinador.

### Justificación
- Cumple estrictamente con la **Regla de Oro** y el **Principio I & II** de la Constitución: cero caídas no controladas (HTTP 500), preservando la inmutabilidad de la base de datos PostgreSQL y la auditoría clínica integral.
- Permite que el sistema funcione en desarrollo tanto con Tesseract instalado como sin él, sin bloquear el despliegue del software.

---

## 4. Normalización del Estado y Trazabilidad

### Decisión
Registrar en los metadatos del documento y en los logs estructurados (`structlog`):
- `metodo_ingesta`: `TEXT_EXTRACTION` | `MULTIMODAL_VISION` | `LOCAL_OCR` | `FALLBACK_AUDIT`
- `paginas_procesadas`: número de páginas evaluadas.
- `tiempo_ingesta_ms`: latencia de la etapa.
