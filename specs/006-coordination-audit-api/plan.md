# Implementation Plan: Endpoints REST de Coordinación y Auditoría Médica (HITL)

**Branch**: `006-coordination-audit-api` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-coordination-audit-api/spec.md`

## Summary

Implementar los endpoints REST especializados en `/api/v1/coordination` para permitir que los médicos coordinadores y administradores supervisen la bandeja de triajes pendientes de auditoría humana (*Human-in-the-Loop*), registren resoluciones médicas inmutables (`aprobar`, `reclasificar`, `rechazar`) con justificación clínica, y consulten el historial de eventos de auditoría y trazabilidad médica respaldados en PostgreSQL.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, Pydantic v2, asyncpg, structlog
**Storage**: PostgreSQL 17 (`auditorias_coordinacion`, `trazabilidad_eventos`, `documentos_triaje`, `episodios_clinicos`)
**Testing**: pytest (`test_coordination_api.py`), HTTPX TestClient
**Target Platform**: Linux / Docker Server
**Project Type**: Backend REST Web Service
**Performance Goals**: < 500ms tiempo de respuesta en consulta de bandeja de pendientes
**Constraints**: 
- RBAC estricto (`require_roles("COORDINADOR", "ADMINISTRADOR")`) con rechazo 403 a roles no autorizados.
- Persistencia inmutable a través de `AuditRepository`.
- 100% pruebas en verde sin mutar la base de datos `mediflow_dev`.
- Sincronización con especificación OpenAPI.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Test-First y Puerta de Calidad Estricta en Verde**: Se crearán pruebas unitarias e integración en `test_coordination_api.py` asegurando 100% tests en verde.
- [x] **II. Consulta Obligatoria ante Dudas**: Requerimientos alineados directamente con el Plan de Trabajo Oficial y aprobados por el usuario.
- [x] **III. PostgreSQL como Fuente Única de Verdad Clínica**: Los dictámenes y eventos se persisten obligatoriamente en PostgreSQL vía `AuditRepository`.
- [x] **IV. Seguridad y Control de Acceso por Roles (RBAC Hospitalario)**: Rutas protegidas con `Depends(require_roles("COORDINADOR", "ADMINISTRADOR"))`.
- [x] **V. Trazabilidad Médica Inmutable**: Toda resolución genera un evento inmutable en `trazabilidad_eventos`.

## Project Structure

### Documentation (this feature)

```text
specs/006-coordination-audit-api/
├── spec.md              # Especificación funcional
├── plan.md              # Este archivo (Plan técnico de arquitectura)
├── research.md          # Hallazgos técnicos y decisiones de diseño
├── data-model.md        # Esquemas Pydantic v2 y modelo relacional
├── quickstart.md        # Guía de validación y pruebas
├── contracts/           # Contratos OpenAPI
│   └── coordination-api.yaml
└── checklists/
    └── requirements.md  # Checklist de calidad de requisitos
```

### Source Code (repository layout)

```text
backend/
├── app/
│   ├── api/v1/
│   │   ├── coordination.py      # Nuevo router de coordinación y auditoría HITL
│   │   └── ...
│   ├── schemas/
│   │   ├── coordination.py      # Nuevos esquemas Pydantic v2 para coordinación
│   │   └── ...
│   ├── repositories/
│   │   ├── audit_repository.py  # Métodos de persistencia de auditoría y trazabilidad
│   │   └── ...
│   └── main.py                  # Inclusión de coordination.router en FastAPI
└── tests/
    └── test_coordination_api.py # Suite de pruebas de seguridad y endpoints
```

**Structure Decision**: Se creará el módulo de endpoints en `backend/app/api/v1/coordination.py`, esquemas Pydantic v2 en `backend/app/schemas/coordination.py` y se enriquecerá `AuditRepository` con métodos auxiliares de consulta de pendientes e historial si es necesario, registrando el router en `main.py`.

## Complexity Tracking

> **No violations identified**: La arquitectura se apega completamente a los patrones existentes de repositorios, esquemas y routers de MediFlow.
