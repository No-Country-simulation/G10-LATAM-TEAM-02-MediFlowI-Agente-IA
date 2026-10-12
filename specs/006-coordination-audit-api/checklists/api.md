# API Quality Checklist: Endpoints REST de Coordinación y Auditoría Médica (HITL)

**Purpose**: Unit tests for API requirements quality, security policies, and schema completeness.
**Created**: 2026-10-09
**Feature**: [spec.md](../spec.md)

## Requirement Completeness

- [x] CHK001 - Are HTTP status codes explicitly documented for all error scenarios (401, 403, 404, 422, 503)? [Completeness, Spec §FR-006, §FR-007]
- [x] CHK002 - Are query parameter bounds and validation constraints defined for `/pending` (limit, offset, minutos_espera)? [Completeness, Spec §FR-002]
- [x] CHK003 - Are the allowed enum values for the clinical decision attribute explicitly defined (`aprobar`, `reclasificar`, `rechazar`)? [Completeness, Spec §FR-004]
- [x] CHK004 - Are audit traceability event payloads and metadata structure specified? [Completeness, Spec §FR-005]

## Requirement Clarity

- [x] CHK005 - Is the minimum clinical justification length quantified with specific bounds (>= 5 chars)? [Clarity, Spec §FR-004]
- [x] CHK006 - Is the behavior for non-existent `documento_id` unambiguously specified as 404 Not Found? [Clarity, Spec §Edge Cases]
- [x] CHK007 - Is the database unavailability error response structured without exposing internal SQL traces? [Clarity, Spec §Edge Cases]

## Security & RBAC Coverage

- [x] CHK008 - Are role-based access control rules defined for all endpoints under `/api/v1/coordination`? [Security, Spec §FR-001, §FR-006]
- [x] CHK009 - Is token verification behavior defined for missing or expired sessions? [Security, Spec §FR-007]
- [x] CHK010 - Is SQL injection prevention mandated via asyncpg positional parameter binding? [Security, Constitution §III]

## Consistency & Data Integrity

- [x] CHK011 - Do Pydantic response schemas align exactly with the OpenAPI v3 contract in `openapi.yaml`? [Consistency, Spec §FR-008]
- [x] CHK012 - Are patient and episode UUID representations consistently serialized as strings in JSON responses? [Consistency, Data Model]
- [x] CHK013 - Does clinical resolution update the triaje operational status while preserving immutable audit logs? [Consistency, Spec §US2]
