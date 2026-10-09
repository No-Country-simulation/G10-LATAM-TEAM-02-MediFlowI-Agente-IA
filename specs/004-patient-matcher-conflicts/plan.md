# Implementation Plan: Nodo de Resolución de Identidad y Conflictos DNI/HC en Pipeline

**Branch**: `dev-wilmer-gulcochia` | **Date**: 2026-10-05 | **Spec**: [specs/004-patient-matcher-conflicts/spec.md](./spec.md)

**Input**: Feature specification from `specs/004-patient-matcher-conflicts/spec.md` (Tarea `[IA-02]`, Issue `#29`)

---

## Summary

Integrar en el pipeline del agente de triaje (`backend/app/agent/`) la resolución de identidad clínica basada estrictamente en identificadores oficiales (DNI e Historia Clínica) utilizando `patient_repository.resolver_paciente_por_identificadores(dni, hc)`. Cuando los identificadores extraídos de un documento clínico pertenezcan a pacientes distintos en la base de datos PostgreSQL, el agente interceptará el conflicto, marcará `discrepancia_identidad_detectada = True` en `state.metadata`, forzará el enrutamiento a `Cola_Revision_Ambigua` y establecerá `requiere_auditoria_humana = True` con `status = "pendiente_auditoria"` para garantizar la seguridad clínica del paciente mediante intervención HITL (*Human-in-the-Loop*).

---

## Technical Context

**Language/Version**: Python 3.13 / FastAPI  
**Primary Dependencies**: `langgraph` (orquestación del pipeline), `pydantic` (modelado de estado `AgentState`), `structlog` (logs estructurados)  
**Storage**: PostgreSQL 17 (`mediflow_dev`) — Tabla `pacientes` consultada asíncronamente vía `patient_repository`  
**Testing**: `pytest`, `pytest-asyncio`, `unittest.mock` (simulación de repositorio y LLM en pruebas unitarias/pipeline)  
**Target Platform**: Linux / Docker  
**Project Type**: AI Pipeline / Agent Decision Logic / Clinical Safety Layer  
**Performance Goals**: Resolución de identidad y cotejo < 15ms por documento procesado  
**Constraints**: No mutar la base de datos de desarrollo durante pruebas unitarias; 100% pruebas en verde sin regresiones; prohibido adivinar identidad por nombres/apellidos si los identificadores discrepan  
**Scale/Scope**: Módulo central de seguridad del agente de triaje para prevención de eventos adversos por identificación cruzada  

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance Assessment | Status |
|---|---|---|
| **I. Test-First y Puerta de Calidad Estricta en Verde** | Suite unitaria `test_patient_matcher.py` y casos de pipeline en `test_agent_cases.py` con 100% de aserciones en verde. | ✅ PASS |
| **II. Consulta Obligatoria ("Si no sabe, pregunte")** | El modelo delega discrepancias a `Cola_Revision_Ambigua` para resolución médica humana, sin suposiciones de IA. | ✅ PASS |
| **III. PostgreSQL Fuente Única de Verdad** | Cotejo directo contra la tabla `pacientes` mediante `patient_repository.resolver_paciente_por_identificadores`. | ✅ PASS |
| **IV. Seguridad y RBAC** | Interceptación de datos clínicos cruzados impidiendo asociación errónea a expedientes de terceros. | ✅ PASS |
| **V. Trazabilidad Médica** | Inyección de metadata explícita (`discrepancia_identidad_detectada`, `motivo_ambiguedad`, `dni_detectado`, `hc_detectada`). | ✅ PASS |

---

## Project Structure

### Documentation (this feature)

```text
specs/004-patient-matcher-conflicts/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical research & decisions (Phase 0)
├── data-model.md        # Entities, schema & state flow (Phase 1)
├── quickstart.md        # Validation & verification guide (Phase 1)
├── contracts/           # Component & pipeline interface contracts (Phase 1)
│   └── patient-matcher-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Actionable task list (Phase 2 - /speckit-tasks)
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── agent/
│   │   ├── patient_matcher.py     # [NUEVO] Módulo de resolución y verificación de identidad
│   │   ├── nodes/
│   │   │   ├── extraction.py      # Invocación de matching post-extracción y seteo de metadata
│   │   │   └── routing.py         # Interceptación de conflicto → Cola_Revision_Ambigua
│   │   └── state.py               # Tipado y esquemas de metadata/enrutamiento
│   └── repositories/
│       └── patient_repository.py  # Función resolver_paciente_por_identificadores ya existente
└── tests/
    ├── test_patient_matcher.py    # [NUEVO] Pruebas unitarias de matching y resolución de conflictos
    └── test_agent_cases.py        # Casos de integración del pipeline completo de triaje
```

---

## Structure Decision

Se encapsula la lógica de resolución en `backend/app/agent/patient_matcher.py` para mantener modularidad y permitir su uso tanto en el nodo `extraction.py` como de forma aislada en pruebas unitarias y servicios de triaje. El nodo `routing.py` consulta la presencia de discrepancia en `state.metadata` y prioriza la derivación a `Cola_Revision_Ambigua` con retención humana obligatoria.

---

## Complexity Tracking

*No violations to project constitution detected.*
