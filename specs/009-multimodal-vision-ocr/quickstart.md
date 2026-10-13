# Quickstart: Validación de Ingesta Híbrida Multimodal y OCR

**Feature**: `009-multimodal-vision-ocr`  
**Date**: 2026-10-12  

---

## Prerrequisitos

1. Servidor de desarrollo backend activo en el puerto 8000:
   ```fish
   cd /home/wigsdev/GitHub/mediflow/backend
   .venv/bin/uvicorn app.main:app --reload --port 8000
   ```
2. Token JWT de autenticación válido:
   ```fish
   set TOKEN (curl -s -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@mediflow.com","password":"admin"}' | jq -r .access_token)
   ```

---

## Escenario 1: Ingesta de Imagen Fotográfica Legible (PNG / JPEG)

Prueba de ingesta con una imagen médica o receta fotográfica:

```fish
curl -s -X POST http://localhost:8000/api/v1/triage/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "documento_id=DOC-TEST-IMG-001" \
  -F "canal_origen=Consulta_Externa" \
  -F "archivo=@casos_clinicos_prueba/receta_urgencias_medica_1791707870248.jpg;type=image/jpeg" \
  | jq '{documento_id, status, error_mensaje, datos_extraidos, clasificacion, decision_enrutamiento}'
```

**Resultado Esperado**:
- `status`: `"procesado"` (o `"pendiente_auditoria"` si la confianza es < 0.80 por legibilidad).
- `error_mensaje`: `null` (sin caídas por ausencia de Tesseract).
- `datos_extraidos.paciente`: Campos extraídos correctamente por Gemini Vision.

---

## Escenario 2: Ingesta de PDF Escaneado (Sin Texto Embebido)

Prueba de detección de PDF escaneado con rasterización en memoria y lectura multimodal:

```fish
curl -s -X POST http://localhost:8000/api/v1/triage/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "documento_id=DOC-TEST-SCAN-001" \
  -F "canal_origen=Admision" \
  -F "archivo=@casos_clinicos_prueba/caso_escaneado_simulado.pdf;type=application/pdf" \
  | jq '{documento_id, status, error_mensaje, datos_extraidos}'
```

**Resultado Esperado**:
- El sistema detecta ausencia de texto embebido en PyMuPDF (`< 50 caracteres`).
- Renderiza las páginas con `fitz` y las envía al motor de visión multimodal.
- `status`: `"procesado"`.

---

## Escenario 3: Ejecución de la Suite de Pruebas Automatizadas

```fish
# Pruebas unitarias de visión y OCR
cd /home/wigsdev/GitHub/mediflow/backend
.venv/bin/pytest tests/test_ingestion_multimodal.py -v

# Verificación de cero regresiones en todo el backend
.venv/bin/pytest -q
```
