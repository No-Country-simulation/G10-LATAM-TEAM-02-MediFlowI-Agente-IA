# Seguridad y trazabilidad del triaje — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Proteger los flujos clínicos con sesiones Bearer y registrar de manera íntegra qué usuario carga, audita y cambia el estado de un documento.

**Architecture:** Esta primera entrega centraliza la autenticación de usuario en FastAPI y mantiene la API Key solamente para integraciones. Una migración Alembic añade las relaciones, estados e historial; el repositorio persiste transiciones funcionales de manera transaccional y React envía el token de sesión real.

**Tech Stack:** FastAPI, Pydantic, asyncpg, Alembic, PostgreSQL 17, React 19, TypeScript/Vite, pytest.

**Spec:** `Docs/superpowers/specs/2026-09-25-integridad-seguridad-triaje-design.md`

## Global Constraints

- PostgreSQL es la fuente única de verdad y los tests no mutan `mediflow_dev`.
- Solo una persona puede cambiar `modo_almacenamiento`; ningún proceso debe cambiarlo automáticamente a OCI.
- Toda tabla o columna nueva/alterada requiere comentario PostgreSQL explícito.
- Todo contrato modificado actualiza OpenAPI y sus tipos TypeScript.
- Cada comportamiento inicia con una prueba fallida; al cierre se ejecutan `pytest`, `npm run build` y `alembic upgrade head` sobre una base aislada.

## Review Focus

- Un Bearer expirado devuelve 401 aun si llega una API Key válida; tarea 1.
- Un operador no puede crear una auditoría HITL; tarea 2.
- Una identidad histórica no mapeable bloquea la migración sin inventar un usuario; tarea 3.
- Rechazar termina en `rechazado`, no en `error`; tarea 4.
- Si falla historia/auditoría, la transacción revierte el cambio de estado; tarea 5.

---

### Task 1: Sesión Bearer reutilizable y login real

**Files:**
- Modify: `backend/app/core/security.py`, `backend/app/api/v1/auth.py`, `backend/tests/test_auth_api.py`
- Modify: `frontend/src/context/AuthContext.jsx`, `frontend/src/api/auth.api.ts`

**Interfaces:**
- Produces: `require_current_user(authorization: str | None) -> dict` que devuelve la sesión válida o HTTP 401.

- [ ] **Step 1: Write the failing test**

```python
def test_require_current_user_rechaza_bearer_invalido(client):
    response = client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer invalido'})
    assert response.status_code == 401
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_auth_api.py -q`
Expected: FAIL because there is no reusable dependency.

- [ ] **Step 3: Implement `require_current_user` and real frontend login**

Use the dependency in `/auth/me`. Make `AuthContext` call the backend login API, persist `{access_token, user}`, verify it on restore and clear it after a 401.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_auth_api.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add backend/app/core/security.py backend/app/api/v1/auth.py backend/tests/test_auth_api.py frontend/src/context/AuthContext.jsx frontend/src/api/auth.api.ts && git commit -m "feat: centralize bearer session authentication"`

### Task 2: Autorización Bearer de rutas interactivas

**Files:**
- Modify: `backend/app/api/v1/triage.py`, `backend/app/api/v1/documents.py`, `backend/app/api/v1/settings.py`, `backend/app/api/v1/patients.py`
- Modify: `backend/tests/test_triage_api.py`, `backend/tests/test_documents_api.py`, `backend/tests/test_settings_api.py`, `backend/tests/conftest.py`
- Modify: `frontend/src/api/triage.api.ts`, `frontend/src/api/patients.api.ts`, `specs/openapi.yaml`, `specs/components/schemas.yaml`

**Interfaces:**
- Consumes: `require_current_user` from task 1.
- Produces: `require_roles(*roles)` and a `DecisionAuditoriaRequest` without `auditor_id`.

- [ ] **Step 1: Write the failing tests**

```python
def test_operador_no_puede_auditar(client, operador_bearer_headers):
    response = client.patch('/api/v1/documents/DOC-1', json={'decision': 'aprobar'}, headers=operador_bearer_headers)
    assert response.status_code == 403
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest backend/tests/test_triage_api.py backend/tests/test_documents_api.py backend/tests/test_settings_api.py -q`
Expected: FAIL because routes still use API Key and accept `auditor_id`.

- [ ] **Step 3: Implement roles, route protection, and Bearer clients**

Require Bearer for patient, triage and document routes; allow HITL only for `AUDITOR`/`ADMINISTRADOR`, and settings only for `ADMINISTRADOR`. Derive auditor UUID from the session. Remove `VITE_API_KEY` from frontend API helpers and attach the stored Bearer token.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest backend/tests/test_triage_api.py backend/tests/test_documents_api.py backend/tests/test_settings_api.py -q; python infrastructure/scripts/validate_spec.py`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add backend/app/api/v1 frontend/src/api specs backend/tests && git commit -m "feat: protect clinical UI routes with bearer auth"`

### Task 3: Migración de estados, relaciones e historial

**Files:**
- Create: `backend/alembic/versions/<revision>_add_document_traceability.py`
- Modify: `Docs/BASE_DE_DATOS.md`, `backend/tests/test_migrations.py`

**Interfaces:**
- Produces: `historial_documento`, las FKs de usuario y estados `recibido`, `procesando`, `procesado`, `pendiente_auditoria`, `rechazado`, `no_soportado`, `error`.

- [ ] **Step 1: Write the failing migration test**

```python
def test_traceability_schema_has_user_fks_and_history(connection):
    assert column_type(connection, 'auditorias_hitl', 'auditor_id') == 'uuid'
    assert foreign_key_targets(connection, 'historial_documento') == {'documentos_triaje', 'usuarios'}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_migrations.py -q`
Expected: FAIL because migration and test fixture do not exist.

- [ ] **Step 3: Implement reversible migration and schema test fixture**

Expand the enum without dropping data, add comments, indexes and FKs, map only deterministic legacy auditor identities and fail on unmappable data. Keep `cola_procesamiento` as a table.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_migrations.py -q; alembic -c backend/alembic.ini upgrade head`
Expected: PASS using a test-only database URL.

- [ ] **Step 5: Commit**

Run: `git add backend/alembic/versions backend/tests/test_migrations.py Docs/BASE_DE_DATOS.md && git commit -m "feat: add document traceability schema"`

### Task 4: Transiciones HITL y almacenamiento PostgreSQL

**Files:**
- Modify: `backend/app/api/v1/documents.py`, `backend/app/repositories/postgres_storage.py`, `backend/app/agent/state.py`, `backend/tests/test_documents_api.py`

**Interfaces:**
- Consumes: UUID de usuario actual y la migración de tarea 3.
- Produces: `registrar_auditoria(..., auditor_id: UUID, ...) -> bool` con aprobar/reclasificar → `procesado`, rechazar → `rechazado`.

- [ ] **Step 1: Write the failing test**

```python
def test_rechazar_documento_lo_deja_en_rechazado(client, auditor_bearer_headers):
    response = client.patch('/api/v1/documents/DOC-PENDIENTE', json={'decision': 'rechazar'}, headers=auditor_bearer_headers)
    assert response.json()['status'] == 'rechazado'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_documents_api.py -q`
Expected: FAIL because a rechazo hoy asigna `error`.

- [ ] **Step 3: Implement the canonical HITL transitions**

Write audit records and update PostgreSQL in one transaction; return the authenticated auditor identity. Consult the database before physical storage and do not create a write fallback that bypasses PostgreSQL.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_documents_api.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

Run: `git add backend/app/api/v1/documents.py backend/app/repositories/postgres_storage.py backend/app/agent/state.py backend/tests/test_documents_api.py && git commit -m "fix: preserve HITL audit outcomes"`

### Task 5: Eventos funcionales y verificación integrada

**Files:**
- Modify: `backend/app/repositories/postgres_storage.py`, `backend/app/services/triage_service.py`, `backend/tests/test_documents_api.py`, `backend/tests/test_triage_api.py`
- Modify: `Docs/ESPECIFICACION_TECNICA_COMPLETA.md`, `Docs/BASE_DE_DATOS.md`, `specs/openapi.yaml`, `specs/components/schemas.yaml`

**Interfaces:**
- Produces: `registrar_historial(conn, documento_id: str, evento: str, ...) -> None`.

- [ ] **Step 1: Write the failing test**

```python
async def test_auditoria_rechazada_crea_evento_y_estado(connection):
    await repository.registrar_auditoria('DOC-1', 'rechazar', auditor_id, 'sin sustento')
    assert await events_for(connection, 'DOC-1') == ['AUDITORIA_RECHAZADA']
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_documents_api.py backend/tests/test_triage_api.py -q`
Expected: FAIL because there are no history writes.

- [ ] **Step 3: Implement `registrar_historial` and contract documentation**

Emit reception, processing, audit-pending and each HITL-decision event with old/new state and actor. Align OpenAPI and technical/database documentation with the shipped contract.

- [ ] **Step 4: Run integration verification**

Run: `pytest; npm --prefix frontend run build; alembic -c backend/alembic.ini upgrade head`
Expected: tests pass, Vite produces zero TypeScript errors and Alembic reaches head using isolated test configuration.

- [ ] **Step 5: Commit**

Run: `git add Docs specs backend frontend && git commit -m "feat: record functional document history"`

## Deferred plans

- OCR fallback, text chunking and automatic patient association are a separate processing plan.
- Ambiguity/priority normalization, document catalog and `.jsx`→`.tsx` migration are a separate compatibility plan.
