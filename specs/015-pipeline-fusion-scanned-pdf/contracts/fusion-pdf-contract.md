# Contrato de Interfaz Interna: Pipeline Fusion para PDFs Escaneados

**Feature**: `015-pipeline-fusion-scanned-pdf`  
**Referencia**: Tarea 2.9 ([IA-09])  
**Date**: 2026-10-20  

---

## 1. Contrato del Umbral de Decisión en Ingesta (`ingestion.py`)

### Entrada
- `state.tipo_archivo`: `"PDF"`
- `state.documento_base64`: `str` (Base64 del PDF)
- `fusion_context`: `ContextoTriaje | None`

### Lógica de Evaluación
```python
pdf_bytes = base64.b64decode(state.documento_base64)
texto_digital = _extraer_texto_pdf_pymupdf(pdf_bytes)

if texto_digital and len(texto_digital.strip()) >= 50:
    # Ruta Digital Inmediata
    metodo = "TEXT_EXTRACTION"
    texto = texto_digital.strip()
    invocar_vision = False
else:
    # Ruta Escaneada / Pipeline Fusion
    metodo = "MULTIMODAL_VISION"
    invocar_vision = True
```

### Garantías de Salida
1. **`documento_base64`**: Debe ser estrictamente `None` en el retorno.
2. **`metodo_extraccion`**:
   - `"TEXT_EXTRACTION"`: si el PDF tenía ≥ 50 caracteres vectoriales.
   - `"MULTIMODAL_VISION"`: si fue procesado por el pase único de Gemini Vision.
   - `"FALLBACK_AUDIT"`: si la llamada a visión o rasterizado falló.
3. **`ContextoTriaje.fusion_resultado`**: Poblado con `ResultadoFusionVision` si la fusión fue exitosa para permitir cortocircuito en `extraction` y `classification`.

---

## 2. Contrato de Optimización y Rasterizado en Memoria

### Parámetros de Rasterizado
- **Matriz de Escala**: `fitz.Matrix(1.5, 1.5)` (equivalente a 108-120 DPI).
- **Formato Intermedio**: JPEG en `io.BytesIO`.
- **Límite de Páginas**: 1 página principal (máximo 3 páginas clínicas en caso de multipágina).

### Parámetros de `image_optimizer.py`
- **Dimensión Máxima**: 1280 píxeles en el lado más largo (sin ampliar imágenes menores).
- **Calidad de Compresión**: JPEG calidad 80 con optimización progresiva.
- **Presupuesto Máximo de Red**: Estrictamente menor a **350,000 bytes** (350 KB) en formato Base64 con prefijo MIME.

---

## 3. SLA y Rendimiento Clínico
- **PDF Digital**: Latencia de ingesta `< 50 ms`.
- **PDF Escaneado**: Latencia de pase único multimodal `< 7.0 s` (p95 < 8.0 s).
