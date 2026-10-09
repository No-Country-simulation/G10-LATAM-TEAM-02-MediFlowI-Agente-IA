# Implementation Plan: Enrutamiento a Farmacia

**Branch**: `dev-henry-suarez` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-enrutamiento-farmacia/spec.md`

## Summary

Actualizar la lógica condicional en `_calcular_destino` (dentro de `routing.py`) para identificar recetas médicas e inyectarlas automáticamente hacia la cola de `Farmacia_Hospitalaria`, forzando intervención humana (HITL) obligatoria si se detectan medicamentos de control especial, cumpliendo con la Regla de Oro de MediFlow.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: LangGraph, Pydantic, pytest

**Storage**: N/A (Solo actualización en memoria en la capa del Agente)

**Testing**: `pytest` (Unit Testing para la función `_calcular_destino`)

**Target Platform**: Backend (FastAPI / LangGraph)

**Project Type**: AI Agent Node

**Constraints**: Respetar el flujo actual sin generar regresiones en otras colas (Urgencias, Ambiguas, Rutina).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **Regla de Oro #3 (0 Regresiones):** Asegurado mediante TDD. Se debe actualizar y correr `test_destinos_triaje_unit.py`.
- [x] **Regla de Oro #1 (PostgreSQL):** N/A para esta funcionalidad puramente lógica de ruteo.

## Project Structure

### Documentation (this feature)

```text
specs/005-enrutamiento-farmacia/
├── plan.md              # Este archivo
├── research.md          # Decisiones de inyección de metadata
├── data-model.md        # Definición implícita de metadata
├── quickstart.md        # Comandos de prueba con pytest
├── contracts/
│   └── routing-contract.md # Firma modificada para _calcular_destino
└── tasks.md             # (Pendiente - Fase 2)
```

### Source Code (repository root)

```text
backend/
├── app/
│   └── agent/
│       └── nodes/
│           └── routing.py        # Modificación de _calcular_destino
└── tests/
    └── test_destinos_triaje_unit.py # Pruebas unitarias
```

**Structure Decision**: La modificación impacta exclusivamente en un nodo LangGraph (`routing.py`) y en su suite de pruebas respectiva, manteniendo la arquitectura aislada y acoplada a la especificación de diseño de agentes.

## Complexity Tracking

N/A - La solución propuesta no incrementa la complejidad arquitectónica, sólo añade ramificaciones lógicas al enrutador existente.
