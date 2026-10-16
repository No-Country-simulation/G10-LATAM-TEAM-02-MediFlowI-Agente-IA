# Implementation Plan: Extracción Estructurada de Medicamentos Prescritos y Enrutamiento a Farmacia Hospitalaria

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/011-prescription-medication-extraction/spec.md`

## Summary

Implementar la extracción clínica estructurada de medicamentos prescritos (principio activo/marca, dosis, frecuencia y vía de administración) mediante modelos tipados con Pydantic v2 en el estado del agente LangGraph (`AgentState`), enriquecer el prompt del nodo de extracción (`node_extraction`), incorporar deserialización y deduplicación defensiva, e integrar el enrutamiento inteligente en `node_routing` hacia `Farmacia_Hospitalaria` con detección automática de fármacos controlados para salvaguarda de auditoría médica humana (HITL), dando cumplimiento al 100% del Requisito R3.

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: Pydantic v2 (`BaseModel`, `Field`), LangGraph, FastAPI, Structlog  
**Storage**: PostgreSQL 17 (`mediflow_dev` en `documentos_triaje.resultado_json`, `episodios_clinicos`, `trazabilidad_eventos`)  
**Testing**: Pytest (100% tests en verde, rollback transaccional o mocks en tests)  
**Target Platform**: Linux Server / Docker Container hospitalario  
**Project Type**: AI Agentic Pipeline & REST API  
**Performance Goals**: Tiempo de extracción e inferencia < 3.0s por documento; 0ms overhead adicional para documentos sin recetas  
**Constraints**: 
- Cero regresiones en los 26 tests preexistentes del backend.
- Tipado estricto con Pydantic v2 (prohibido `Any` no documentado o diccionarios planos para entidades clínicas).
- Tolerancia a valores nulos en dosis, frecuencia y vía si el texto original no los especifica.
- Precedencia médica absoluta: `Cola_Emergencia_Medica` sobre `Farmacia_Hospitalaria` si existe riesgo vital agudo.
**Scale/Scope**: Soporte para polifarmacia extensa (hasta 20 medicamentos por receta sin truncamiento).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio Constitucional | Estado | Justificación y Cumplimiento |
|---|---|---|
| **I. Test-First y Puerta en Verde** | ✅ PASS | Se diseñan pruebas unitarias y de integración primero en `test_agent_cases.py` y `test_destinos_triaje_unit.py`. 0 regresiones toleradas. |
| **II. Consulta Obligatoria ante Dudas** | ✅ PASS | El alcance técnico y clínico está delimitado exhaustivamente por el Requisito R3 y la Tarea 2.7 del plan de trabajo. |
| **III. PostgreSQL Fuente de Verdad** | ✅ PASS | Los medicamentos extraídos se persisten dentro de `resultado_json` en la tabla `documentos_triaje` sin mutar la BD durante las pruebas. |
| **IV. RBAC Hospitalario** | ✅ PASS | Cuando un fármaco controlado requiere auditoría humana, la resolución HITL queda restringida a coordinadores y administradores. |
| **V. Trazabilidad Inmutable** | ✅ PASS | La derivación a `Farmacia_Hospitalaria` y la presencia de medicamentos quedan registradas en el evento de auditoría. |
| **VI. Tipado Estricto Pydantic v2** | ✅ PASS | `MedicamentoPrescritoState` modelado con validación de tipos estricta y sincronizado con OpenAPI en `specs/components/schemas.yaml`. |

## Project Structure

### Documentation (this feature)

```text
specs/011-prescription-medication-extraction/
├── spec.md              # Especificación funcional validada
├── plan.md              # Este plan de implementación técnica
├── research.md          # Decisiones de modelado, prompt y enrutamiento
├── data-model.md        # Definición de MedicamentoPrescritoState y relaciones
├── quickstart.md        # Guía paso a paso para validación y testing
├── checklists/
│   └── requirements.md  # Checklist de calidad de especificación
└── contracts/
    └── openapi.contract.yaml # Extensión de contrato OpenAPI 3.1
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── agent/
│   │   ├── state.py                 # Modelo MedicamentoPrescritoState y ampliación de DatosExtraidosState
│   │   ├── nodes/
│   │   │   ├── extraction.py        # _EXTRACTION_PROMPT, _parsear_respuesta y _consolidar_datos
│   │   │   └── routing.py           # Enrutamiento a Farmacia_Hospitalaria y detección de controlados
│   │   └── clinical_catalog.py      # Catálogo y normalización
│   ├── services/
│   │   └── triage_service.py        # Serialización y persistencia
│   └── _generated/
│       └── models.py                # Modelos OpenAPI autogenerados
├── tests/
│   ├── test_agent_cases.py          # Pruebas unitarias de extracción de medicamentos
│   ├── test_destinos_triaje_unit.py # Pruebas de enrutamiento a Farmacia_Hospitalaria
│   └── test_openapi_contract.py     # Verificación de contrato OpenAPI
specs/
└── components/
    └── schemas.yaml                 # Schema OpenAPI para MedicamentoPrescrito y DatosExtraidos
```

**Structure Decision**: Monorepo modular estándar con backend en Python/FastAPI/LangGraph, sincronizado contra especificaciones OpenAPI en `specs/` y suites de prueba en `backend/tests/`.

## Complexity Tracking

> **No violations of constitutional principles detected.** El diseño utiliza los patrones existentes del agente LangGraph sin añadir dependencias externas, tablas innecesarias ni capas redundantes.
