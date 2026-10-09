# Quickstart Guide: Endpoints REST de Coordinación y Auditoría Médica (HITL)

**Feature**: `specs/006-coordination-audit-api`
**Date**: 2026-10-09

## 1. Requisitos Previos

- PostgreSQL activo con la base de datos `mediflow_dev` o pruebas con mocks de base de datos aislados.
- Dependencias de backend instaladas (`pytest`, `httpx`, `asyncpg`, `fastapi`, `pydantic`).

## 2. Escenarios de Prueba y Validación

### A. Ejecutar la Suite de Pruebas Automatizadas

```bash
pytest backend/tests/test_coordination_api.py -v
```

### B. Validar Protección RBAC (Seguridad)

- **Acceso Permitido**: Peticiones con token de usuario rol `COORDINADOR` o `ADMINISTRADOR` reciben HTTP 200.
- **Acceso Denegado**: Peticiones con token de usuario rol `OPERADOR` o `MEDICO` reciben HTTP 403 Forbidden.
- **Sin Autenticación**: Peticiones sin token reciben HTTP 401 Unauthorized.

### C. Validar Flujo End-to-End de Resolución Médica

1. Obtener lista de pendientes:
   ```bash
   curl -X GET http://localhost:8000/api/v1/coordination/pending \
     -H "Authorization: Bearer <TOKEN_COORDINADOR>"
   ```
2. Resolver un caso con dictamen clínico:
   ```bash
   curl -X POST http://localhost:8000/api/v1/coordination/resolve/DOC-2026-0001 \
     -H "Authorization: Bearer <TOKEN_COORDINADOR>" \
     -H "Content-Type: application/json" \
     -d '{
       "decision": "aprobar",
       "justificacion_clinica": "Se valida concordancia diagnóstica y cuadro clínico estabilizado."
     }'
   ```
3. Verificar historial de auditoría:
   ```bash
   curl -X GET http://localhost:8000/api/v1/coordination/audit/DOC-2026-0001 \
     -H "Authorization: Bearer <TOKEN_COORDINADOR>"
   ```
