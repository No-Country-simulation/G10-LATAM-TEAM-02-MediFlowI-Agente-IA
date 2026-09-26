# Integridad documental clínica Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminar truncamiento de clasificación, asociar pacientes con seguridad y registrar cada fase del triaje.

**Architecture:** La clasificación consolidará bloques de texto; el repositorio resolverá DNI/HC sin inferencias por nombre. El repositorio PostgreSQL guardará eventos técnicos mínimos y la UI consumirá el catálogo tipado compartido.

**Tech Stack:** FastAPI, Pydantic, LangGraph, asyncpg/Alembic, React/Vite/TypeScript.

**Spec:** `Docs/superpowers/specs/2026-09-25-triaje-integridad-documental-design.md`

## Global Constraints

- PostgreSQL `mediflow_dev` es la fuente de verdad; todo esquema nuevo usa Alembic y `COMMENT ON`.
- Las pruebas no modifican `mediflow_dev`.
- No cambiar automáticamente LOCAL/OCI.
- Verificar `pytest`, `npm run build` y `alembic upgrade head`.

## Review Focus

- Hallazgo urgente en el último bloque debe prevalecer; prueba en Task 1.
- DNI/HC contradictorios no deben asociar; prueba en Task 2.
- Evento no debe guardar texto clínico; prueba en Task 3.
- Un tipo fuera del catálogo debe normalizarse a `Otro`; prueba en Task 4.

### Task 1: Clasificación por bloques

**Files:** `backend/app/agent/nodes/classification.py`, `backend/tests/test_agent_cases.py`.

- [ ] Escribir `test_consolidar_clasificaciones_prioriza_urgente_en_bloque_final`.
- [ ] Ejecutar la prueba y confirmar RED.
- [ ] Implementar `consolidar_clasificaciones(bloques: list[ClasificacionState]) -> ClasificacionState`; reutilizar bloques de extracción y eliminar `texto[:3000]`.
- [ ] Ejecutar pruebas del agente y confirmar verde.
- [ ] Commit `feat: classify complete documents in chunks`.

### Task 2: Resolución segura DNI/HC

**Files:** `backend/app/repositories/patient_repository.py`, `backend/app/repositories/postgres_storage.py`, `backend/tests/test_patients_api.py`.

- [ ] Escribir pruebas de coincidencia única y conflicto DNI/HC.
- [ ] Implementar `resolver_paciente_por_identificadores(dni: str | None, historia_clinica: str | None) -> dict` con estados `asociado`, `sin_coincidencia`, `conflicto`.
- [ ] Asociar sólo el estado `asociado`; devolver `conflicto` sin escritura de FK.
- [ ] Ejecutar pruebas y confirmar verde.
- [ ] Commit `feat: resolve document patient by dni and hc`.

### Task 3: Historial granular

**Files:** `backend/app/repositories/postgres_storage.py`, `backend/tests/test_documents_api.py`.

- [ ] Escribir prueba de lista de eventos técnicos sin texto clínico.
- [ ] Implementar eventos OCR, extracción, clasificación, enrutamiento y resultado de asociación en modo PostgreSQL y mock.
- [ ] Ejecutar pruebas de documentos y confirmar verde.
- [ ] Commit `feat: record granular document workflow events`.

### Task 4: Catálogo clínico tipado

**Files:** `backend/app/agent/nodes/classification.py`, `frontend/src/api/triage.api.ts`, `frontend/src/pages/TriageConsoleView.tsx`, pruebas de agente.

- [ ] Escribir prueba para tipo no reconocido normalizado a `Otro`.
- [ ] Definir catálogo compartido en backend y ampliar prompt; normalizar respuesta del LLM.
- [ ] Exponer unión TypeScript y mostrar etiquetas del catálogo en UI.
- [ ] Ejecutar `pytest` y `npm run build`.
- [ ] Commit `feat: expand typed clinical document catalog`.

## Self-review

- Los cuatro requisitos de la especificación tienen una tarea propietaria.
- Task 2 produce el resultado de asociación que Task 3 registra.
- No se requiere una tabla adicional; la FK `paciente_id` e `historial_documento` ya existen.
