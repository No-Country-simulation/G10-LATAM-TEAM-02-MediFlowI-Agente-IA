"""SQL parametrizado y errores cerrados; sin conexiones a mediflow_dev."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.core.alerts import EVENTO_GUARDIA, MENSAJE_GUARDIA
from app.repositories.alert_repository import AlertRepository
from app.repositories.postgres_storage import DatabaseUnavailableError

pytestmark = pytest.mark.repository_mock


@pytest.fixture
def connection(monkeypatch):
    conn = AsyncMock()
    acquire = Mock()
    acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    monkeypatch.setattr(
        "app.repositories.alert_repository.get_db_pool",
        AsyncMock(return_value=Mock(acquire=acquire)),
    )
    return conn


async def test_evento_ligado_al_documento_y_episodio_confirmados(connection):
    episode_id = uuid4()
    connection.fetchrow.return_value = {
        "id": uuid4(),
        "episodio_id": episode_id,
        "documento_id": "DOC'--",
        "prioridad": "Urgente",
        "fecha": datetime.now(UTC),
        "mensaje": MENSAJE_GUARDIA,
    }
    event = await AlertRepository.registrar_alerta("DOC'--", None)
    sql, *args = connection.fetchrow.call_args.args
    assert args == ["DOC'--", None, EVENTO_GUARDIA, MENSAJE_GUARDIA]
    assert "DOC'--" not in sql
    assert "INSERT INTO trazabilidad_eventos" in sql
    assert "FROM documentos_triaje" in sql
    assert "destino_principal = 'Cola_Emergencia_Medica'" in sql
    assert event.episodio_id == episode_id
    assert event.documento_id == "DOC'--"
    assert not any(field in sql for field in ("nombre", "diagnostico", "documento_identidad"))


@pytest.mark.parametrize("error", [None, ConnectionError("sin conexión")])
async def test_documento_ausente_o_fallo_sql_no_confirma_alerta(connection, error):
    connection.fetchrow.return_value = None
    connection.fetchrow.side_effect = error
    with pytest.raises(DatabaseUnavailableError):
        await AlertRepository.registrar_alerta("DOC", None)


async def test_sin_postgres_no_hay_respaldo_en_memoria(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.alert_repository.get_db_pool", AsyncMock(return_value=None)
    )
    with pytest.raises(DatabaseUnavailableError):
        await AlertRepository.registrar_alerta("DOC", None)
