# Implementation Plan: Normalización y Deserialización Robusta de Respuestas LLM Multiformato

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-llm-response-normalization/spec.md`

## Summary

Resolver la incompatibilidad de tipos generada cuando los modelos multimodales (como Google Gemini en `langchain_google_genai`, usando el modelo activo `gemini-3.5-flash-lite`) entregan el contenido de respuesta (`AIMessage.content`) como una lista de bloques o fragmentos en lugar de un string primitivo, y normalizar campos numéricos como `edad`:
1. **Capa de Servicio (`LLMService.completar`)**: Unificar la deserialización de `respuesta.content` garantizando que siempre retorne una cadena de texto consolidada (`str`), iterando de forma segura sobre listas de fragmentos o diccionarios (`{"type": "text", "text": "..."}`).
2. **Nodos de Extracción y Clasificación (`extraction.py` y `classification.py`)**: Implementar normalización defensiva en `_parsear_respuesta` para sanitizar la entrada, eliminando bloques Markdown (```json ... ```) con tolerancia a caracteres de control previos y posteriores, previniendo excepciones `'list' object has no attribute 'strip'`.
3. **Validación Defensiva de Estado (`state.py`)**: Implementar `@field_validator("edad", mode="before")` en `PacienteState` para parsear automáticamente cadenas con sufijos textuales (ej: `"19 años"`) a entero.
4. **Pruebas Automatizadas TDD**: Desarrollar pruebas unitarias en `tests/test_llm_service.py` y pruebas de integración en `tests/test_agent_cases.py` con respuestas multiformato simuladas, garantizando cero regresiones en la suite completa de `pytest`.

## Technical Context

**Language/Version**: Python 3.12+ / Python 3.13
**Primary Dependencies**: LangGraph, langchain-google-genai, langchain-openai, langchain-core, Pydantic v2, structlog
**Storage**: PostgreSQL 17 (`mediflow_dev`, tablas `documentos_triaje`, `episodios_clinicos`)
**Testing**: pytest (`pytest-asyncio`), HTTPX TestClient
**Target Platform**: Linux / Docker Server
**Project Type**: Backend AI Agent & Clinical Triage Pipeline
**Performance Goals**: < 10ms de procesamiento de normalización de respuestas por solicitud
**Constraints**:
- Cumplimiento incondicional de la Regla de Oro y la Constitución de MediFlow.
- Cero alteraciones en las firmas públicas de la API REST (`/api/v1/triage`).
- Mantenimiento estricto de la estructura de 5 nodos de LangGraph.
- 100% de pruebas unitarias y E2E pasando en verde sin mutar `mediflow_dev`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Test-First y Puerta de Calidad Estricta en Verde**: Se implementarán tests que reproduzcan la respuesta en lista de Gemini antes de desplegar, verificando 100% en verde con `pytest`.
- [x] **II. Consulta Obligatoria ante Dudas**: El alcance se circunscribe a la normalización de payloads del LLM, diagnosticada y aprobada por el usuario.
- [x] **III. PostgreSQL como Fuente Única de Verdad Clínica**: Los metadatos clínicos extraídos se persisten en `documentos_triaje` con diagnóstico y CIE-10 validados.
- [x] **IV. Seguridad y Control de Acceso por Roles**: No altera las restricciones RBAC existentes.
- [x] **V. Trazabilidad Médica Inmutable**: Garantiza que los errores de parsing no bloqueen la auditoría ni generen clasificaciones anómalas.

## Project Structure

### Documentation (this feature)

```text
specs/008-llm-response-normalization/
├── spec.md              # Especificación funcional
├── plan.md              # Este archivo (Plan técnico de arquitectura)
├── research.md          # Investigación de patrones de deserialización en LangChain
├── data-model.md        # Entidades, flujos de datos y tipos de contenido
├── quickstart.md        # Comandos de ejecución y pruebas de validación
├── contracts/           # Contratos de interfaz de servicio
│   └── llm-normalization-contract.yaml
└── checklists/
    └── requirements.md  # Checklist de calidad de requisitos
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── agent/
│   │   ├── state.py           # Validador defensivo de edad en PacienteState
│   │   └── nodes/
│   │       ├── extraction.py      # Sanitización defensiva en _parsear_respuesta
│   │       └── classification.py  # Sanitización defensiva en _parsear_respuesta
│   └── services/
│       └── llm_service.py         # Normalización robusta en LLMService.completar()
└── tests/
    ├── test_llm_service.py        # Pruebas unitarias de respuestas multiformato
    └── test_agent_cases.py        # Cobertura de extracción/clasificación end-to-end
```

## Complexity Tracking

> Ninguna violación a la constitución detectada. Diseño desacoplado y puramente defensivo.
