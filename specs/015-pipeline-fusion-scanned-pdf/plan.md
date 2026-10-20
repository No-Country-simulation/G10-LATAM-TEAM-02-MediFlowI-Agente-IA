# Implementation Plan: Pipeline Fusion para PDFs Escaneados e Híbridos (Tarea 2.9 / IA-09)

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)  
**Referencia de Plan de Trabajo**: Tarea 2.9 ([PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md](../../plan%20de%20trabajo/PLAN_DE_TRABAJO_BACKEND_LANGGRAPH.md#L306-L335))  
**Issue de GitHub**: [IA-09] #69 / PR #77  

---

## Summary

Consolidar al 100% el rendimiento y cobertura de la **Tarea 2.9 (IA-09)** extendiendo el algoritmo de **Pipeline Fusion** hacia documentos PDF escaneados e híbridos mediante discriminación inteligente:
1. **Regla 1 (PDF Digital / ≥ 50 caracteres)**: Extracción directa vectorial con PyMuPDF en ~0.01s con método `TEXT_EXTRACTION`, ahorrando llamadas de visión, garantizando 100% de fidelidad y cero alucinaciones.
2. **Regla 2 (PDF Escaneado / < 50 caracteres)**: Detección automática de contenido visual, rasterización en memoria con PyMuPDF a JPEG optimizado (< 350 KB vía `image_optimizer.py`), e invocación del pase único de Gemini Vision vía `fusion.py`, completando el triaje en un solo viaje de red con latencia < 7s (p95 < 8s).
3. **Saneamiento de Memoria**: Liberación inmediata de `documento_base64 = None` al terminar `node_ingestion` en ambos flujos.

---

## Technical Context

**Language/Version**: Python 3.12+ (Entorno activo: Python 3.13 en Linux)  
**Primary Dependencies**: FastAPI 0.115+, LangGraph 0.2+, LangChain, PyMuPDF 1.25+ (`fitz`), Pillow 11+ (`PIL`), `ChatGoogleGenerativeAI` (Gemini 1.5 Flash), Pydantic v2  
**Storage**: PostgreSQL `mediflow_dev` (persistencia canónica de metadatos clínicos y trazabilidad); almacenamiento local de archivos originales en `backend/storage/recibidos/` preservado por `TriageService`  
**Testing**: Pytest 9.1+ (`pytest backend/tests/test_pipeline_fusion.py backend/tests/test_pipeline_fusion_benchmark.py -v`)  
**Target Platform**: Servidor Linux / Contenedor Docker hospitalario  
**Project Type**: Agente Autónomo de Triaje de Urgencias y Farmacia Hospitalaria (FastAPI / LangGraph)  
**Performance Goals**:
- PDF Digital (≥ 50 caracteres): Ingesta en `< 50 ms`.
- PDF Escaneado (< 50 caracteres): Pipeline Fusion completo en `< 7.0 s` (p95 < 8.0 s).
- Payload Base64 por página rasterizada: Estrictamente `< 350,000 bytes` (< 350 KB).  
**Constraints**:
- Cumplimiento estricto de la Constitución MediFlow v1.2.0: Cero regresiones, 100% de pruebas en verde en `pytest` sin mutación de la base de datos de desarrollo.
- Procesamiento 100% en memoria mediante buffers `io.BytesIO`, prohibiendo archivos temporales en disco.
- Mantenimiento estricto de los 5 nodos estándar de LangGraph (`ingestion` ➔ `extraction` ➔ `classification` ➔ `confidence` ➔ `routing`).

---

## Constitution Check

*GATE: Conformidad estricta con las directrices de MediFlow.*

| Principio Constitucional | Evaluación de Conformidad | Estado |
|---|---|:---:|
| **I. Test-First y Puerta de Calidad Estricta** | Todas las pruebas unitarias y de benchmark (`test_pipeline_fusion.py`, `test_pipeline_fusion_benchmark.py`) deben pasar al 100% en verde antes de dar por completado. | ✅ PASA |
| **II. Consulta Obligatoria ante Dudas** | La regla de corte por umbral de 50 caracteres y la decisión de no crear tarea 2.10 fueron confirmadas explícitamente con el usuario. | ✅ PASA |
| **III. PostgreSQL como Fuente de Verdad** | Toda la clasificación, códigos CIE-10 y decisiones de enrutamiento se persisten en `mediflow_dev`. | ✅ PASA |
| **IV. Agente IA y Arquitectura de 5 Nodos** | Se preserva la topología canónica de LangGraph; la optimización ocurre dentro del nodo `ingestion` y se comunica mediante `ContextoTriaje` desacoplado. | ✅ PASA |
| **V. Trazabilidad y Seguridad Hospitalaria** | Los archivos físicos se preservan inalterados por `TriageService`; el saneamiento de `documento_base64 = None` en el estado evita fuga de binarios en memoria. | ✅ PASA |

---

## Project Structure

### Documentation (this feature)

```text
specs/015-pipeline-fusion-scanned-pdf/
├── spec.md              # Especificación funcional y criterios de aceptación
├── plan.md              # Este archivo (Plan de arquitectura e implementación)
├── research.md          # Fase 0: Decisiones técnicas y justificación de umbrales
├── data-model.md        # Fase 1: Diagrama de flujo y ciclo de estados
├── quickstart.md        # Fase 1: Guía de validación y comandos de prueba
├── checklists/
│   └── requirements.md  # Checklist de calidad de requerimientos
└── contracts/
    └── fusion-pdf-contract.md # Contrato de interfaz interna y SLA
```

### Source Code Impacted

```text
backend/
├── app/
│   ├── agent/
│   │   ├── fusion.py            # Módulo de fusión multimodal (reutilizado)
│   │   ├── graph.py             # Grafo LangGraph singleton (reutilizado)
│   │   └── nodes/
│   │       ├── ingestion.py     # Integración del umbral >= 50 chars y activación de fusión para PDFs
│   │       ├── extraction.py    # Cortocircuito reactivo para reutilizar datos de fusión
│   │       └── classification.py # Cortocircuito reactivo para normalización de prioridad
│   └── services/
│       ├── image_optimizer.py   # Compresión Pillow < 350 KB (reutilizado)
│       └── llm_service.py       # Cliente Gemini Vision con timeout=30 y max_retries=2
└── tests/
    ├── test_pipeline_fusion.py  # Suite de pruebas unitarias de fusión
    └── test_pipeline_fusion_benchmark.py # Suite de benchmark de latencia
```

---

## Complexity Tracking

> **Sin violaciones constitucionales ni complejidades no justificadas.**

| Item | Evaluación |
|---|---|
| Reutilización vs Módulo Nuevo | Se reutiliza `fusion.py` y `image_optimizer.py` en lugar de duplicar lógica para PDFs, manteniendo el código limpio y robusto. |
| Umbral de 50 caracteres | Basado en el estándar de informes clínicos digitales donde anamnesis y diagnóstico superan ampliamente este umbral, aislando membretes y escaneos reales. |
