"""
MediFlow — Tests unitarios para el repositorio asíncrono episode_repository.

Valida todas las operaciones CRUD, generación de códigos, transiciones de estado,
filtros y manejo de fallos sin mutar la base de datos de desarrollo (Regla de Oro de MediFlow).
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
import pytest

from app.repositories.episode_repository import (
    ESTADOS_VALIDOS,
    _ensure_uuid,
    _generate_episode_code,
    _require_pool,
    assign_doctor,
    create_episode,
    get_episode_by_code,
    get_episode_by_id,
    list_episodes,
    update_episode_status,
)
from app.repositories.postgres_storage import DatabaseUnavailableError


def _make_mock_pool(mock_conn: AsyncMock):
    """Crea un mock de asyncpg.Pool con soporte para async with pool.acquire()."""
    pool = MagicMock()
    
    @asynccontextmanager
    async def acquire_ctx():
        yield mock_conn

    pool.acquire = acquire_ctx
    return pool


# ─── Tests Unitarios de Helpers ───────────────────────────────────────────────

def test_generate_episode_code():
    code = _generate_episode_code()
    assert code.startswith("EP-")
    parts = code.split("-")
    assert len(parts) == 3
    assert len(parts[1]) == 8  # YYYYMMDD
    assert len(parts[2]) == 4  # HEX4


def test_ensure_uuid():
    valid_uuid = uuid4()
    assert _ensure_uuid(valid_uuid) == valid_uuid
    assert _ensure_uuid(str(valid_uuid)) == valid_uuid
    assert _ensure_uuid(None) is None
    assert _ensure_uuid("invalid-uuid-string") is None
    assert _ensure_uuid(12345) is None


@pytest.mark.asyncio
async def test_require_pool_when_none():
    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with pytest.raises(DatabaseUnavailableError) as exc:
            await _require_pool()
        assert "no está disponible" in str(exc.value)


# ─── US1: Creación de Episodios ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_episode_success():
    paciente_id = uuid4()
    operador_id = uuid4()
    episode_id = uuid4()

    mock_row = {
        "id": episode_id,
        "codigo_episodio": "EP-20261005-9999",
        "paciente_id": paciente_id,
        "operador_ingreso_id": operador_id,
        "estado_atencion": "ingresado",
        "nivel_prioridad": "Urgencia",
        "motivo_consulta": "Dolor torácico agudo",
        "created_at": datetime.now(timezone.utc),
    }

    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        data = {
            "paciente_id": paciente_id,
            "operador_ingreso_id": operador_id,
            "nivel_prioridad": "Urgencia",
            "motivo_consulta": "Dolor torácico agudo",
        }
        res = await create_episode(data)

        assert res["id"] == episode_id
        assert res["estado_atencion"] == "ingresado"
        assert res["motivo_consulta"] == "Dolor torácico agudo"
        mock_conn.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_create_episode_custom_code():
    mock_row = {
        "id": uuid4(),
        "codigo_episodio": "EP-CUSTOM-001",
        "paciente_id": uuid4(),
        "estado_atencion": "ingresado",
    }
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await create_episode({"paciente_id": uuid4(), "codigo_episodio": "EP-CUSTOM-001"})
        assert res["codigo_episodio"] == "EP-CUSTOM-001"


@pytest.mark.asyncio
async def test_create_episode_invalid_status():
    with pytest.raises(ValueError) as exc:
        await create_episode({"paciente_id": uuid4(), "estado_atencion": "ESTADO_INEXISTENTE"})
    assert "Estado de atención inválido" in str(exc.value)


@pytest.mark.asyncio
async def test_create_episode_database_error():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.side_effect = RuntimeError("Conexión perdida con Postgres")
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        with pytest.raises(DatabaseUnavailableError) as exc:
            await create_episode({"paciente_id": uuid4()})
        assert "No fue posible crear episodio clínico" in str(exc.value)


# ─── US2: Consultas Detalladas desde v_episodios_detalle ─────────────────────

@pytest.mark.asyncio
async def test_get_episode_by_id_found():
    episode_id = uuid4()
    mock_row = {
        "episodio_id": episode_id,
        "codigo_episodio": "EP-20261005-1234",
        "paciente_nombre_completo": "Juan Pérez",
        "paciente_edad": 45,
        "medico_general_nombre": "Dra. García",
    }
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await get_episode_by_id(episode_id)
        assert res is not None
        assert res["episodio_id"] == episode_id
        assert res["paciente_nombre_completo"] == "Juan Pérez"
        assert res["paciente_edad"] == 45


@pytest.mark.asyncio
async def test_get_episode_by_id_not_found():
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = None
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await get_episode_by_id(uuid4())
        assert res is None


@pytest.mark.asyncio
async def test_get_episode_by_id_invalid_id():
    res = await get_episode_by_id("no-es-uuid")
    assert res is None


@pytest.mark.asyncio
async def test_get_episode_by_code():
    mock_row = {
        "episodio_id": uuid4(),
        "codigo_episodio": "EP-20261005-5555",
        "paciente_nombre_completo": "María López",
    }
    mock_conn = AsyncMock()
    mock_conn.fetchrow.return_value = mock_row
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await get_episode_by_code("EP-20261005-5555")
        assert res is not None
        assert res["codigo_episodio"] == "EP-20261005-5555"

        # Búsqueda vacía retorna None
        assert await get_episode_by_code("") is None
        assert await get_episode_by_code("   ") is None


# ─── US3: Transición de Estados, Asignación y Listado ────────────────────────

@pytest.mark.asyncio
async def test_update_episode_status_success():
    episode_id = uuid4()
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await update_episode_status(episode_id, "en_triaje")
        assert res is True
        mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_update_episode_status_not_found():
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 0"
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await update_episode_status(uuid4(), "atendido")
        assert res is False


@pytest.mark.asyncio
async def test_update_episode_status_invalid():
    with pytest.raises(ValueError):
        await update_episode_status(uuid4(), "ESTADO_DESCONOCIDO")


@pytest.mark.asyncio
async def test_assign_doctor_general_and_specialist():
    episode_id = uuid4()
    doctor_id = uuid4()

    mock_conn = AsyncMock()
    mock_conn.execute.return_value = "UPDATE 1"
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        # Médico General
        res_gen = await assign_doctor(episode_id, doctor_id, rol="general")
        assert res_gen is True

        # Especialista
        res_esp = await assign_doctor(episode_id, doctor_id, rol="especialista", especialidad="Cardiología")
        assert res_esp is True


@pytest.mark.asyncio
async def test_list_episodes_with_filters():
    paciente_id = uuid4()
    mock_rows = [
        {"episodio_id": uuid4(), "estado_atencion": "en_triaje", "nivel_prioridad": "Emergencia"},
        {"episodio_id": uuid4(), "estado_atencion": "en_triaje", "nivel_prioridad": "Urgencia"},
    ]
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = mock_rows
    mock_pool = _make_mock_pool(mock_conn)

    with patch("app.repositories.episode_repository.get_db_pool", new_callable=AsyncMock, return_value=mock_pool):
        res = await list_episodes(estado="en_triaje", nivel_prioridad="Emergencia", paciente_id=paciente_id, limit=10)
        assert len(res) == 2
        assert res[0]["estado_atencion"] == "en_triaje"
        
        # Validar llamada con argumentos correctos
        call_args = mock_conn.fetch.call_args[0]
        query = call_args[0]
        params = call_args[1:]
        assert "estado_atencion = $1" in query
        assert "nivel_prioridad = $2" in query
        assert "paciente_id = $3" in query
        assert params == ("en_triaje", "Emergencia", paciente_id, 10, 0)
