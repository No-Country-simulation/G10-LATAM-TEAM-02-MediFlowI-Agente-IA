# Implementation Plan: Calibrador de Score de Confianza Multimodal y Retención HITL

**Branch**: `006-confidence-score` (desarrollado en `dev-henry-suarez`) | **Date**: 2026-10-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/006-confidence-score/spec.md`  (Tarea `[IA-04]`, Issue `#31`)

---

## Summary

Calibrar el cálculo del score de confianza en `backend/app/agent/nodes/confidence.py` mediante un vector de ponderación multidimensional (calidad de texto/OCR, completitud clínica de signos y diagnósticos, y consistencia CIE-10), delimitando el score estrictamente entre `0.0` y `1.0`. Actualizar en `backend/app/agent/nodes/routing.py` el umbral de corte clínico a `< 0.75` para desviar obligatoriamente los casos con baja confianza hacia `Cola_Auditoria_Humana` con `requiere_auditoria_humana = True` y `status = "pendiente_auditoria"`, preservando las precedencias críticas de emergencias médicas y discrepancias de identidad.

---

## Technical Context

**Language/Version**: Python 3.12+  
**Primary Dependencies**: FastAPI, LangGraph, Pydantic v2, structlog  
**Storage**: PostgreSQL (`mediflow_dev` inmutable durante pruebas)  
**Testing**: pytest, pytest-asyncio  
**Target Platform**: Linux / Windows / Contenedor Docker  
**Project Type**: Backend AI Agent Workflow (LangGraph Nodes)  
**Performance Goals**: Evaluación de nodo en < 10ms (función pura sobre estado en memoria)  
**Constraints**: 
- Score acotado estrictamente en rango [0.0, 1.0].
- 100% pruebas en verde antes de merge (Regla de Oro).
- Cero efectos secundarios en la base de datos de desarrollo activa.  
**Scale/Scope**: Módulo `confidence.py`, nodo `routing.py` y suite de tests unitarios/integración.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Test-First y Puerta de Calidad Estricta en Verde**: TDD obligatorio; suite de tests se planifica primero antes de tocar código de producción. Cero regresiones en `pytest`.
- [x] **II. Consulta Obligatoria ante Dudas**: Requerimientos del Issue #31 y umbral 0.75 claramente estipulados y alineados.
- [x] **III. PostgreSQL como Fuente Única de Verdad**: No se muta esquema físico; los estados y metadatos se integran en el ciclo de persistencia existente.
- [x] **IV. RBAC Hospitalario**: La `Cola_Auditoria_Humana` requiere aprobación de Coordinador Médico.
- [x] **V. Trazabilidad Inmutable**: Inyección de `factores_confianza` en `state.metadata` para auditoría retrospectiva.

---

## Project Structure

### Documentation (this feature)

```text
specs/006-confidence-score/
├── spec.md              # Especificación funcional de requerimientos
├── plan.md              # Este plan de implementación técnica
├── research.md          # Decisiones de ponderación y umbral HITL 0.75
├── data-model.md        # Estructura de entidades de estado y transiciones
├── quickstart.md        # Guía de verificación rápida y ejecución de tests
├── contracts/
│   └── confidence-contract.md # Contratos de entrada/salida de confidence y routing
└── checklists/
    └── requirements.md  # Checklist de validación de calidad
```

### Source Code Afectado

```text
backend/
├── app/
│   └── agent/
│       └── nodes/
│           ├── confidence.py  # Ponderación granular y registro de factores en metadata
│           └── routing.py     # Umbral de corte < 0.75 hacia Cola_Auditoria_Humana
└── tests/
    ├── test_confidence_calibration.py # Nuevas pruebas unitarias dedicadas a calibración
    └── test_destinos_triaje_unit.py   # Actualización y validación de corte a 0.75
```

**Structure Decision**: Modificación puntual y desacoplada dentro de la arquitectura LangGraph de MediFlow sin alterar las firmas de API públicas.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Ninguna | Cumple al 100% la arquitectura modular establecida en MediFlow | N/A |
