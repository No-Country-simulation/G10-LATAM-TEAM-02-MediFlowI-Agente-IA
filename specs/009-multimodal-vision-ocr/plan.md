# Implementation Plan: Ingesta Híbrida Multimodal con Gemini Vision y OCR Local

**Branch**: `009-multimodal-vision-ocr` | **Date**: 2026-10-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/009-multimodal-vision-ocr/spec.md`

## Summary

Implementar un flujo de ingesta de documentos de alta precisión y resiliencia que admita imágenes clínicas (PNG, JPEG, WebP) y PDFs escaneados (sin texto vectorial embebido). La estrategia técnica emplea **Google Gemini Vision** (`ChatGoogleGenerativeAI`) a través de un nuevo método `completar_multimodal` en `LLMService` como motor primario, rasterización de páginas en memoria con `PyMuPDF` (`fitz`), un mecanismo de respaldo automático hacia OCR local (`pytesseract`), y captura defensiva de errores que deriva a auditoría médica (*Human-in-the-Loop*) sin colapsar el sistema si ambos motores son incapaces de transcribir el documento.

## Technical Context

**Language/Version**: Python 3.12+ (Backend)  
**Primary Dependencies**: `langchain-google-genai`, `PyMuPDF` (`fitz`), `Pillow`, `pytesseract`, `structlog`, `FastAPI`  
**Storage**: PostgreSQL (`mediflow_dev`) para metadatos y trazabilidad, almacenamiento físico local/OCI  
**Testing**: `pytest` con fixtures aislados (sin mutar base de datos de desarrollo)  
**Target Platform**: Linux / Docker  
**Project Type**: Servicio web de triaje hospitalario y orquestación con agentes autónomos (LangGraph)  
**Performance Goals**: Procesamiento multimodal < 4s por documento; fallback a OCR < 2s; latencia de ingesta controlada  
**Constraints**: Entornos donde Tesseract no esté instalado a nivel de sistema deben degradar limpiamente a HITL sin generar errores 500  
**Scale/Scope**: Procesamiento de órdenes médicas, recetas manuscritas y PDFs escaneados  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Principio I (Test-First & Cero Regresiones)**: Nuevos tests unitarios y de integración para ingesta multimodal y fallback antes de cerrar la tarea; 100% pruebas en verde.
- [x] **Principio II (Consulta Obligatoria)**: El alcance fue acordado con el usuario y las ambigüedades técnicas fueron resueltas en `research.md`.
- [x] **Principio III (PostgreSQL como Fuente Única de Verdad)**: Los metadatos de ingesta y estados se preservan en `documentos_triaje` y tablas de trazabilidad sin mutaciones no autorizadas.
- [x] **Principio IV & V (RBAC y Trazabilidad Médica Inmutable)**: Toda derivación a `pendiente_auditoria` por fallos visuales genera su registro correspondiente en auditoría.
- [x] **Regla de Oro**: Ninguna prueba muta `mediflow_dev`, el modo de almacenamiento se mantiene 100% manual.

## Project Structure

### Documentation (this feature)

```text
specs/009-multimodal-vision-ocr/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── vision-ocr-contract.yaml
├── checklists/
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code Impact

```text
backend/
├── app/
│   ├── services/
│   │   └── llm_service.py       # Nuevo método completar_multimodal() y soporte de imágenes
│   ├── agent/
│   │   ├── nodes/
│   │   │   └── ingestion.py     # Lógica híbrida: PyMuPDF -> Gemini Vision -> Tesseract OCR -> Fallback HITL
│   │   └── state.py             # Metadatos de método de extracción
│   └── api/v1/
│       └── triage.py            # Reconocimiento de tipos MIME (soporte WebP y detección de escaneos)
└── tests/
    └── test_ingestion_multimodal.py  # Tests unitarios y de integración para imágenes y escaneos
```

**Structure Decision**: El proyecto sigue la estructura unificada modular del backend existente de MediFlow, desacoplando el servicio LLM del nodo de ingesta de LangGraph.

## Complexity Tracking

*No hay violaciones constitucionales que justificar.*
