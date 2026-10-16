import os
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# Fuerza un proveedor determinista antes de importar la aplicación. Ninguna prueba
# automatizada debe depender de credenciales reales ni realizar llamadas LLM.
os.environ["GOOGLE_API_KEY"] = "your-test-placeholder"
os.environ["OPENAI_API_KEY"] = "your-test-placeholder"
os.environ["ALLOW_MOCK_LLM"] = "true"
# Impide conexiones a mediflow_dev aun si el desarrollador tiene un .env real.
# Las pruebas de SQL offline proporcionan su propia URL sin conectarse.
os.environ["DATABASE_URL"] = ""

from app.core.config import get_settings
from app.main import app

TEST_SESSIONS = {
    "test-operator-token": {"id": "11111111-2222-3333-4444-555555555555", "rol": "OPERADOR"},
    "test-auditor-token": {"id": "22222222-2222-3333-4444-555555555555", "rol": "AUDITOR"},
    "test-admin-token": {"id": "33333333-2222-3333-4444-555555555555", "rol": "ADMINISTRADOR"},
    "test-coordinador-token": {
        "id": "44444444-2222-3333-4444-555555555555",
        "rol": "COORDINADOR",
        "especialidad_medica": "Medicina de Urgencias",
    },
    "test-medico-token": {
        "id": "55555555-2222-3333-4444-555555555555",
        "rol": "MEDICO",
        "especialidad_medica": "Medicina Interna",
    },
}


async def _fake_active_session(token: str):
    return TEST_SESSIONS.get(token)


async def _fake_alert(documento_id, usuario_id):
    from app._generated.models import AlertaGuardia
    from app.core.alerts import MENSAJE_GUARDIA

    return AlertaGuardia(
        id=uuid4(),
        documento_id=documento_id,
        episodio_id=None,
        prioridad="Urgente",
        fecha=datetime.now(UTC),
        mensaje=MENSAJE_GUARDIA,
    )


@pytest.fixture(autouse=True)
def isolated_local_storage(tmp_path, monkeypatch):
    """Los documentos sintéticos de pytest nunca se mezclan con archivos del usuario."""
    monkeypatch.setattr("app.repositories.oci_storage.LOCAL_STORAGE_DIR", tmp_path / "storage")


@pytest.fixture(scope="session")
def settings():
    s = get_settings()
    return s


@pytest.fixture(autouse=True)
def mock_postgres_for_tests(request):
    """Evita que los tests automatizados de pytest inserten filas o alteren la BD de desarrollo."""
    if request.node.get_closest_marker("repository_mock"):
        # Esta prueba usa explícitamente un repositorio sin DATABASE_URL: conserva
        # el modo en memoria para verificar la trazabilidad sin tocar mediflow_dev.
        yield None
        return

    with (
        patch(
            "app.repositories.alert_repository.AlertRepository.registrar_alerta",
            side_effect=_fake_alert,
        ),
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.guardar_resultado"
        ) as mock_save,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.listar",
            new_callable=AsyncMock,
        ) as mock_list,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.listar_historial",
            new_callable=AsyncMock,
        ) as mock_history,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.obtener_por_id",
            new_callable=AsyncMock,
        ) as mock_get_document,
        patch(
            "app.repositories.postgres_storage.PostgresStorageRepository.registrar_auditoria",
            new_callable=AsyncMock,
        ) as mock_audit,
        patch(
            "app.repositories.postgres_storage.get_storage_mode", new_callable=AsyncMock
        ) as mock_storage_mode,
        patch("app.api.v1.settings._guardar_modo_almacenamiento_db") as mock_save_settings,
        patch(
            "app.api.v1.settings._obtener_modo_almacenamiento_db", new_callable=AsyncMock
        ) as mock_get_settings,
        patch("app.core.security.create_session", new_callable=AsyncMock),
        patch("app.core.security.revoke_session", new_callable=AsyncMock),
        patch("app.core.security.get_active_session_user", side_effect=_fake_active_session),
    ):
        mock_save.return_value = True
        mock_list.return_value = []
        mock_history.return_value = []
        mock_get_document.return_value = None
        mock_audit.return_value = False
        mock_storage_mode.return_value = "LOCAL"
        mock_save_settings.return_value = None
        mock_get_settings.return_value = "LOCAL"
        yield mock_save


@pytest.fixture
def client():
    """Cliente de pruebas FastAPI."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(settings):
    """Headers con la API Key configurada."""
    return {
        "X-API-Key": settings.api_key,
        "Content-Type": "application/json",
    }


@pytest.fixture
def bearer_headers():
    return {"Authorization": "Bearer test-operator-token", "Content-Type": "application/json"}


@pytest.fixture
def auditor_bearer_headers():
    return {"Authorization": "Bearer test-auditor-token", "Content-Type": "application/json"}


@pytest.fixture
def admin_bearer_headers():
    return {"Authorization": "Bearer test-admin-token", "Content-Type": "application/json"}


@pytest.fixture
def coordinador_bearer_headers():
    return {"Authorization": "Bearer test-coordinador-token", "Content-Type": "application/json"}


@pytest.fixture
def medico_bearer_headers():
    return {"Authorization": "Bearer test-medico-token", "Content-Type": "application/json"}


@pytest.fixture
def receta_medica_texto():
    """Receta médica ambulatoria estándar con dos fármacos y pauta completa."""
    return (
        "RECETA MÉDICA HOSPITALARIA\n"
        "Paciente: Juan Pérez  Edad: 45 años  DNI: 12345678\n"
        "Médico: Dra. Elena Morales  Matrícula: MN-98432\n"
        "Diagnóstico: Faringoamigdalitis aguda bacteriana (J03.9)\n"
        "Indicaciones farmacológicas:\n"
        "1. Amoxicilina 500 mg cada 8 horas vía oral por 7 días.\n"
        "2. Paracetamol 500 mg cada 8 horas vía oral si presenta dolor o fiebre.\n"
    )


@pytest.fixture
def receta_controlados_texto():
    """Receta médica con medicamentos controlados/narcóticos sujeta a fiscalización."""
    return (
        "RECETA MÉDICA DE ESTUPEFACIENTES Y PSICOFÁRMACOS\n"
        "Paciente: Roberto Gómez  Edad: 60 años  DNI: 87654321\n"
        "Médico: Dr. Carlos Santana  Matrícula: MN-55441\n"
        "Diagnóstico: Dolor oncológico severo\n"
        "Rp.\n"
        "1. Morfina 10 mg cada 4 horas vía subcutánea.\n"
        "2. Clonazepam 2 mg cada 24 horas vía oral antes de dormir.\n"
    )


@pytest.fixture
def informe_sin_medicamentos_texto():
    """Informe radiológico diagnóstico sin ninguna prescripción farmacológica."""
    return (
        "INFORME RADIOLÓGICO DE TÓRAX\n"
        "Paciente: María Lopez  Edad: 38 años  DNI: 45678912\n"
        "Médico Solicitante: Dr. Fernando Ruiz  Matrícula: MN-12345\n"
        "Estudio: Radiografía de tórax PA y lateral\n"
        "Hallazgos: Campos pulmonares bien ventilados. Silueta cardíaca dentro de límites normales. "
        "No se observan infiltrados ni consolidaciones pleuropulmonares activas.\n"
        "Conclusión: Estudio radiográfico de tórax sin hallazgos patológicos agudos.\n"
    )


