# Research & Technical Decisions: Pipeline Fusion para PDFs Escaneados e Híbridos

**Feature**: `015-pipeline-fusion-scanned-pdf`  
**Referencia**: Tarea 2.9 ([IA-09]) / Issue #69 / PR #77  
**Date**: 2026-10-20  

---

## 1. Decisiones de Arquitectura e Ingesta

### Decisión 1: Umbral de Discriminación Inteligente (Texto Digital vs. Visión Multimodal)
- **Decisión**: Utilizar la extracción directa vectorial con `PyMuPDF` (`fitz`) e inspeccionar la longitud del texto resultante:
  - **`len(texto_digital.strip()) >= 50`**: Se cataloga como documento digital (o híbrido con texto rico). Se adopta dicho texto en milisegundos (`0.01s`) con método `TEXT_EXTRACTION`, omitiendo cualquier rasterizado o consumo de visión.
  - **`len(texto_digital.strip()) < 50`**: Se cataloga como PDF escaneado (o híbrido con solo membrete/título). Se activa automáticamente la ruta de **Pipeline Fusion** en memoria.
- **Justificación**:
  - Un informe médico digital o receta electrónica tiene entre 100 y 3,000 caracteres de texto seleccionable. Extraerlo directamente garantiza 100% de precisión en dosis, fármacos, DNI y CIE-10 en < 50 ms.
  - Si un PDF solo contiene un membrete (ej. `"Hospital Central - Urgencias"` = 28 caracteres) y el resto es una receta fotografiada, el umbral de 50 caracteres detecta inmediatamente que la semántica clínica real reside en la imagen incrustada.
- **Alternativas Evaluadas y Descartadas**:
  - *Enviar siempre el PDF completo a Visión Multimodal*: Descartado por consumo excesivo de tokens y latencia innecesaria de 5-7 segundos cuando el texto digital ya está disponible de forma limpia en 0.01 segundos.
  - *Usar Tesseract OCR local para PDFs escaneados*: Descartado por lentitud (> 25 segundos por documento) y alto índice de error en caligrafía médica y firmas.

---

### Decisión 2: Rasterización 100% en Memoria mediante PyMuPDF
- **Decisión**: Extraer las páginas del PDF escaneado directamente a imágenes en memoria (`io.BytesIO`) empleando `fitz.open(stream=pdf_bytes, filetype="pdf")` con matriz de escala `fitz.Matrix(1.5, 1.5)` (equivalente a 108-120 DPI).
- **Justificación**:
  - Cero escrituras en el sistema de archivos (cumplimiento de seguridad y rendimiento hospitalario).
  - Escala 1.5 provee nitidez óptima para sellos y manuscritos clínicos sin sobrepasar la memoria RAM.
  - Se procesa la primera página clínica (o hasta 3 páginas clave) garantizando que el archivo comprimido no supere los 350 KB.
- **Alternativas Evaluadas y Descartadas**:
  - *Usar librería `pdf2image` con binario `pdftoppm` (Poppler)*: Descartado para evitar dependencias nativas del sistema operativo en contenedores Docker y simplificar la portabilidad.
  - *Rasterizado a 300 DPI*: Descartado porque generaba imágenes de más de 4 MB que excedían el límite estricto de Gemini Vision y ralentizaban la red.

---

### Decisión 3: Reutilización de `image_optimizer.py` y `fusion.py`
- **Decisión**: Conectar la imagen rasterizada en memoria directamente al servicio [image_optimizer.py](file:///home/wigsdev/GitHub/mediflow/backend/app/services/image_optimizer.py) (auto-orientación EXIF, normalización RGB y compresión JPEG 80) y al orquestador [fusion.py](file:///home/wigsdev/GitHub/mediflow/backend/app/agent/fusion.py) con `ContextoTriaje`.
- **Justificación**:
  - Reutiliza al 100% la inversión técnica del PR #77 (`6a3f3e9`).
  - Permite que los nodos posteriores (`extraction.py` y `classification.py`) apliquen el mismo cortocircuito reactivo que ya funciona con imágenes JPEG/PNG/WebP, completando el triaje en un solo viaje de red.
- **Alternativas Evaluadas y Descartadas**:
  - *Crear un prompt o módulo de fusión independiente para PDFs*: Descartado por violar el principio DRY y generar deuda técnica innecesaria.

---

### Decisión 4: Manejo Resiliente de Fallos sin Bucles Redundantes
- **Decisión**: Si la llamada a Gemini Vision falla o devuelve un JSON no interpretable para un PDF escaneado, el sistema marca `metodo_extraccion = "FALLBACK_AUDIT"` y deriva directamente a `pendiente_auditoria` (HITL).
- **Justificación**:
  - Ante una imagen médica ilegible en un PDF, reintentar con OCR tradicional tarda 30 segundos adicionales y casi invariablemente produce texto ininteligible que termina de todas formas en auditoría humana. Fallar rápido hacia HITL protege la experiencia del usuario y no satura la API.
