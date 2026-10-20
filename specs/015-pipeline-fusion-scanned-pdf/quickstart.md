# Guía de Validación Rápida: Pipeline Fusion para PDFs Escaneados (Quickstart)

**Feature**: `015-pipeline-fusion-scanned-pdf`  
**Referencia**: Tarea 2.9 ([IA-09])  
**Date**: 2026-10-20  

---

## 1. Prerrequisitos

- Entorno virtual de backend activo (`backend/.venv`).
- Dependencias instaladas: `PyMuPDF (fitz)`, `Pillow`, `langgraph`, `fastapi`.
- Variable de entorno `GOOGLE_API_KEY` (opcional para pruebas unitarias con mocks; requerida para benchmark en vivo).

---

## 2. Validación Automatizada con Pytest

Ejecutar la suite completa de pruebas de fusión e ingesta:

```bash
# Desde la raíz del repositorio
backend/.venv/bin/pytest backend/tests/test_pipeline_fusion.py backend/tests/test_pipeline_fusion_benchmark.py -v
```

### Resultados Esperados:
- **`test_un_viaje_y_reuso_sin_omitir_cie10_ni_cinco_nodos`**: PASSED (verifica cortocircuito en 1 viaje de red).
- **`test_compresion_adaptativa_mide_base64_no_solo_jpeg`**: PASSED (verifica presupuesto < 350 KB).
- **`test_pdf_digital_omite_vision_y_extrae_en_milisegundos`**: PASSED (verifica umbral >= 50 caracteres).
- **`test_pdf_escaneado_activa_pipeline_fusion`**: PASSED (verifica activación de pase único para < 50 caracteres).
- **`test_servicio_conserva_original_aunque_el_estado_libere_base64`**: PASSED (verifica saneamiento de memoria `documento_base64 = None`).

---

## 3. Validación Manual del Benchmark de Latencia

Para medir el rendimiento de 20 muestras clínicas sintéticas:

```bash
backend/.venv/bin/python infrastructure/scripts/benchmark_pipeline_fusion.py --dry-run
```

- Métrica de Aprobación: `cumple_p95_menor_8s == True` con latencias percentil 95 inferiores a 8,000 ms.
