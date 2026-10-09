"""Tests para los endpoints de Coordinación y Auditoría Médica (HITL) en /api/v1/coordination.

Verifica:
- Control de acceso RBAC estricto (COORDINADOR y ADMINISTRADOR permitidos, OPERADOR/MEDICO 403, no autenticado 401).
- Bandeja de pendientes GET /api/v1/coordination/pending con filtros.
- Resolución de triaje POST /api/v1/coordination/resolve/{documento_id} (aprobar, reclasificar, rechazar).
- Historial inmutable GET /api/v1/coordination/audit/{documento_id}.
- Manejo semántico de errores (404, 422, 503).
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.repositories.postgres_storage import DatabaseUnavailableError


@pytest.fixture
def mock_coordinador_user():
    return {
        "id": "11111111-2222-3333-4444-555555555555",
        "documento_identidad": "12345678",
        "nombres": "Dr. Carlos",
        "apellidos": "Coordinador",
        "correo": "coordinador@mediflow.pe",
        "rol": "COORDINADOR",
        "estado": "ACTIVO",
    }


@pytest.fixture
def mock_admin_user():
    return {
        "id": "22222222-2222-3333-4444-555555555555",
        "documento_identidad": "87654321",
        "nombres": "Admin",
        "apellidos": "General",
        "correo": "admin@mediflow.pe",
        "rol": "ADMINISTRADOR",
        "estado": "ACTIVO",
    }


@pytest.fixture
def mock_operador_user():
    return {
        "id": "33333333-2222-3333-4444-555555555555",
        "documento_identidad": "44445555",
        "nombres": "Ana",
        "apellidos": "Operadora",
        "correo": "operador@mediflow.pe",
        "rol": "OPERADOR",
        "estado": "ACTIVO",
    }


# ── 1. Tests de Autenticación y Autorización RBAC ──────────────────────────────


@pytest.mark.asyncio
async def test_pending_sin_token_retorna_401():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/coordination/pending")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_pending_rol_operador_retorna_403(mock_operador_user):
    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_operador_user
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/coordination/pending",
                headers={"Authorization": "Bearer token-operador"},
            )
    assert response.status_code == 403
    assert "No cuenta con permisos" in response.json()["detail"]


@pytest.mark.asyncio
async def test_resolve_rol_operador_retorna_403(mock_operador_user):
    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_operador_user
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/coordination/resolve/DOC-2026-0001",
                headers={"Authorization": "Bearer token-operador"},
                json={
                    "decision": "aprobar",
                    "justificacion_clinica": "Justificación clínica suficiente",
                },
            )
    assert response.status_code == 403


# ── 2. Tests de Consulta de Bandeja de Pendientes (US1) ────────────────────────


@pytest.mark.asyncio
async def test_pending_coordinador_exitoso(mock_coordinador_user):
    sample_rows = [
        {
            "documento_id": "DOC-2026-0001",
            "episodio_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "fecha_ingesta": datetime(2026, 10, 9, 10, 0, 0),
            "tiempo_espera_minutos": 45,
            "estado": "pendiente_auditoria",
            "canal_origen": "Admision",
            "especialidad_sugerida": "Cardiologia",
            "nivel_prioridad": "Urgente",
            "confianza_ia": 0.42,
            "motivo_hitl": "Baja confianza diagnóstica",
            "diagnostico_preliminar": "Dolor torácico atípico",
            "codigo_cie10": "R07.4",
            "paciente": {
                "id": "99999999-8888-7777-6666-555555555555",
                "nombres": "Juan",
                "apellidos": "Perez",
                "numero_documento": "12345678",
                "historia_clinica": "HC-12345678",
                "numero_telefono": "987654321",
                "genero": "MASCULINO",
            },
        }
    ]

    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.obtener_triajes_pendientes",
        new_callable=AsyncMock,
    ) as mock_repo:
        mock_verify.return_value = mock_coordinador_user
        mock_repo.return_value = sample_rows

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/coordination/pending?especialidad=Cardiologia&minutos_espera=30",
                headers={"Authorization": "Bearer token-coordinador"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["documento_id"] == "DOC-2026-0001"
    assert data[0]["especialidad_sugerida"] == "Cardiologia"
    assert data[0]["paciente"]["nombres"] == "Juan"


@pytest.mark.asyncio
async def test_pending_administrador_exitoso(mock_admin_user):
    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.obtener_triajes_pendientes",
        new_callable=AsyncMock,
    ) as mock_repo:
        mock_verify.return_value = mock_admin_user
        mock_repo.return_value = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/coordination/pending",
                headers={"Authorization": "Bearer token-admin"},
            )

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_pending_db_unavailable_retorna_503(mock_coordinador_user):
    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.obtener_triajes_pendientes",
        new_callable=AsyncMock,
    ) as mock_repo:
        mock_verify.return_value = mock_coordinador_user
        mock_repo.side_effect = DatabaseUnavailableError("PG caido")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/coordination/pending",
                headers={"Authorization": "Bearer token-coordinador"},
            )

    assert response.status_code == 503


# ── 3. Tests de Resolución y Dictamen Clínico HITL (US2) ───────────────────────


@pytest.mark.asyncio
async def test_resolve_aprobar_exitoso(mock_coordinador_user):
    resultado_mock = {
        "id": "aaaa1111-2222-3333-4444-555555555555",
        "documento_id": "DOC-2026-0001",
        "episodio_id": "bbbb2222-2222-3333-4444-555555555555",
        "coordinador_id": mock_coordinador_user["id"],
        "decision": "aprobar",
        "justificacion_clinica": "Se confirma cuadro clínico y se aprueba derivación.",
        "nuevo_estado": "procesado",
        "created_at": datetime(2026, 10, 9, 12, 0, 0),
    }

    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.resolver_triaje",
        new_callable=AsyncMock,
    ) as mock_resolver:
        mock_verify.return_value = mock_coordinador_user
        mock_resolver.return_value = resultado_mock

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/coordination/resolve/DOC-2026-0001",
                headers={"Authorization": "Bearer token-coordinador"},
                json={
                    "decision": "aprobar",
                    "justificacion_clinica": "Se confirma cuadro clínico y se aprueba derivación.",
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "aprobar"
    assert data["nuevo_estado"] == "procesado"
    assert data["documento_id"] == "DOC-2026-0001"


@pytest.mark.asyncio
async def test_resolve_reclasificar_con_destino_y_prioridad(mock_coordinador_user):
    resultado_mock = {
        "id": "aaaa1111-2222-3333-4444-555555555555",
        "documento_id": "DOC-2026-0002",
        "episodio_id": None,
        "coordinador_id": mock_coordinador_user["id"],
        "decision": "reclasificar",
        "justificacion_clinica": "Reclasificado a Farmacia Hospitalaria por tratarse de receta médica.",
        "nuevo_estado": "procesado",
        "created_at": datetime(2026, 10, 9, 12, 5, 0),
    }

    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.resolver_triaje",
        new_callable=AsyncMock,
    ) as mock_resolver:
        mock_verify.return_value = mock_coordinador_user
        mock_resolver.return_value = resultado_mock

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/coordination/resolve/DOC-2026-0002",
                headers={"Authorization": "Bearer token-coordinador"},
                json={
                    "decision": "reclasificar",
                    "justificacion_clinica": "Reclasificado a Farmacia Hospitalaria por tratarse de receta médica.",
                    "categoria_destino": "Farmacia_Hospitalaria",
                    "prioridad_sugerida": "Rutina",
                },
            )

    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "reclasificar"


@pytest.mark.asyncio
async def test_resolve_justificacion_muy_corta_retorna_422(mock_coordinador_user):
    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify:
        mock_verify.return_value = mock_coordinador_user
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/coordination/resolve/DOC-2026-0001",
                headers={"Authorization": "Bearer token-coordinador"},
                json={
                    "decision": "aprobar",
                    "justificacion_clinica": "ok",  # menor a 5 caracteres
                },
            )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_resolve_documento_no_encontrado_retorna_404(mock_coordinador_user):
    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.resolver_triaje",
        new_callable=AsyncMock,
    ) as mock_resolver:
        mock_verify.return_value = mock_coordinador_user
        mock_resolver.side_effect = ValueError("Documento no encontrado: DOC-INEXISTENTE")

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/v1/coordination/resolve/DOC-INEXISTENTE",
                headers={"Authorization": "Bearer token-coordinador"},
                json={
                    "decision": "rechazar",
                    "justificacion_clinica": "Documento ilegible o dañado.",
                },
            )

    assert response.status_code == 404
    assert "Documento de triaje no encontrado" in response.json()["detail"]


# ── 4. Tests de Historial y Consulta de Eventos (US3) ─────────────────────────


@pytest.mark.asyncio
async def test_audit_history_coordinador_exitoso(mock_coordinador_user):
    eventos_mock = [
        {
            "id": "11111111-aaaa-bbbb-cccc-dddddddddddd",
            "documento_id": "DOC-2026-0001",
            "episodio_id": None,
            "usuario_id": mock_coordinador_user["id"],
            "evento": "AUDITORIA_APROBADA",
            "descripcion": "Resolución HITL: aprobar.",
            "metadata": {"decision": "aprobar"},
            "created_at": datetime(2026, 10, 9, 12, 10, 0),
        }
    ]

    with patch("app.core.security.verify_access_token", new_callable=AsyncMock) as mock_verify, patch(
        "app.repositories.audit_repository.AuditRepository.obtener_eventos_documento",
        new_callable=AsyncMock,
    ) as mock_eventos:
        mock_verify.return_value = mock_coordinador_user
        mock_eventos.return_value = eventos_mock

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get(
                "/api/v1/coordination/audit/DOC-2026-0001",
                headers={"Authorization": "Bearer token-coordinador"},
            )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["evento"] == "AUDITORIA_APROBADA"
