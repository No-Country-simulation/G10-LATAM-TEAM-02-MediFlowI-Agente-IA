# Implementation Plan: Visualización Estructurada de Medicamentos Prescritos, Vías de Administración y Robustez del Visor Clínico

**Branch**: `014-prescription-medication-viewer` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/014-prescription-medication-viewer/spec.md`

---

## Summary

Esta funcionalidad implementa la visualización estructurada y enriquecida de medicamentos prescritos (farmacoterapia) en la interfaz clínica de MediFlow, incorporando el nombre del fármaco, dosis, frecuencia y vías de administración (oral, intravenosa, intramuscular, etc.) mediante badges estilizados con Tailwind CSS. Asimismo, desacopla semánticamente los encabezados de alerta del cuerpo descriptivo en el visor clínico (`DocumentViewer.tsx`), garantizando plena accesibilidad, consistencia en pruebas automatizadas y soporte integral para la toma de decisiones médicas en la ficha de detalle (`/documentos/:id`), consola de triaje (`/triaje`) y bandeja de auditoría HITL (`/auditoria/:id`).

---

## Technical Context

**Language/Version**: TypeScript 5.x / React 18+ (Frontend), Python 3.12+ (Backend)  
**Primary Dependencies**: React 18, Vite, Tailwind CSS, Lucide React / React Icons, FastAPI, Pydantic v2  
**Storage**: PostgreSQL 17 (`mediflow_dev`, campo `documentos_triaje.metadata.medicamentos` proyectado en `datos_extraidos.medicamentos`)  
**Testing**: Vitest + React Testing Library (Frontend, 13 suites, 94 tests), Pytest (Backend, 49 tests en suite de documentos y fusión)  
**Target Platform**: Navegadores modernos (Desktop clínico, tablets de triaje y móviles médicos)  
**Project Type**: Web Application (Frontend SPA React + Backend FastAPI REST API)  
**Performance Goals**: Renderizado de tabla y visor en < 200ms; tiempo de respuesta de API < 150ms  
**Constraints**: 100% pruebas en verde, tipado estricto sin `any`, responsive con Tailwind CSS, accesibilidad semántica en alertas  
**Scale/Scope**: 5 componentes/vistas de frontend afectados (`types/documents.ts`, `documentsApi.ts`, `ExtractedData.tsx`, `AuditDetail.tsx`, `TriageConsoleView.tsx`, `DocumentViewer.tsx`), 2 módulos backend (`postgres_storage.py`, `documents.py`)

---

## Constitution Check

*GATE: Evaluado contra `.specify/memory/constitution.md`*

| Principio Constitucional | Estado | Justificación / Evidencia |
|---|:---:|---|
| **I. Test-First y Calidad Estricta en Verde** | ✅ PASA | `vitest run` pasa con 94/94 tests; `pytest` pasa con 49/49 tests relevantes; `npm run build` con 0 errores TypeScript. Base de datos `mediflow_dev` intacta. |
| **II. Consulta Obligatoria ante Dudas** | ✅ PASA | Requerimientos de UI y desacoplamiento semántico derivados explícitamente del plan de trabajo frontend y spec aprobada. |
| **III. PostgreSQL como Fuente Única de Verdad** | ✅ PASA | Persistencia en `documentos_triaje` vía UPSERT; metadatos JSONB accesibles y normalizados sin requerir DDL destructivo previo a la BD unificada. |
| **IV. Seguridad y Control de Acceso (RBAC)** | ✅ PASA | Visualización en auditoría restringida a roles autorizados (`COORDINADOR`/`ADMINISTRADOR`). |
| **V. Trazabilidad Médica Inmutable** | ✅ PASA | Preservación de todos los metadatos de extracción del pipeline IA. |
| **VI. Tailwind CSS y Responsividad Obligatoria** | ✅ PASA | Maquetado 100% responsivo con clases de Tailwind CSS y badges adaptativos. |

---

## Project Structure

### Documentation (this feature)

```text
specs/014-prescription-medication-viewer/
├── spec.md                     # Especificación funcional aprobada
├── plan.md                     # Este archivo (Plan de implementación técnica)
├── research.md                 # Fase 0: Decisiones técnicas y trade-offs
├── data-model.md               # Fase 1: Entidades, diagramas ER y ciclo de vida
├── quickstart.md               # Fase 1: Guía de validación y comandos ejecutables
├── contracts/
│   └── medication-contract.json # Fase 1: Esquema JSON del contrato de datos
└── checklists/
    └── requirements.md         # Verificación de calidad de la especificación
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/v1/
│   │   └── documents.py        # Proyección de metadata.medicamentos a datos_extraidos
│   └── repositories/
│       └── postgres_storage.py # Persistencia de medicamentos en metadata durante UPSERT
└── tests/
    ├── test_documents_api.py   # Pruebas de serialización de documentos
    └── test_pipeline_fusion.py # Pruebas del pipeline multimodal

frontend/
├── src/
│   ├── api/
│   │   └── documentsApi.ts     # Normalización defensiva de medicamentos y vías
│   ├── components/
│   │   ├── documents/
│   │   │   └── DocumentViewer.tsx # Desacoplamiento semántico en alerta de contingencia
│   │   └── triage/
│   │       └── ExtractedData.tsx  # Tabla clínica de farmacoterapia y badges
│   ├── pages/
│   │   ├── AuditDetail.tsx        # Sección de medicamentos en auditoría HITL
│   │   └── TriageConsoleView.tsx  # Sección de medicamentos en consola de triaje
│   └── types/
│       └── documents.ts        # Interfaz TypeScript Medication y ClinicalDocument extendida
└── tests/
    └── components/
        └── documents/
            └── DocumentViewer.test.tsx # Pruebas del visor clínico
```

**Structure Decision**: Arquitectura desacoplada Web Application estándar (Frontend React + Backend FastAPI). Cada capa consume contratos tipados y sincronizados.

---

## Complexity Tracking

> **Sin violaciones constitucionales que justificar**. Todo el diseño se apoya en los patrones ya establecidos en la base de código.
