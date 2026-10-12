"""Pruebas unitarias del repositorio de trazabilidad y auditoría de coordinación.

Mockea el connection pool de asyncpg para verificar las inserciones en
trazabilidad_eventos y auditorias_coordinacion sin mutar la base de datos
de desarrollo mediflow_dev (Regla de Oro de MediFlow).
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.audit_repository import AuditRepository
from app.repositories.postgres_storage import DatabaseUnavailableError

EPISODIO_ID = "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
DOCUMENTO_ID = "DOC-2026-000123"
USUARIO_ID = "11111111-2222-3333-4444-555555555555"
COORDINADOR_ID = "44444444-2222-3333-4444-555555555555"


def _pool_mockeado(fila_retorno: dict):
    """Construye un pool asyncpg simulado cuya conexión devuelve fila_retorno."""
    pool = MagicMock()
    conn = AsyncMock()
    conn.fetchrow.return_value = fila_retorno
    pool.acquire.return_value.__aenter__.return_value = conn
    pool.acquire.return_value.__aexit__.return_value = False
    return pool, conn


async def test_registrar_evento_trazabilidad_inserta_con_parametros_posicionales():
    """La bitácora se inserta en trazabilidad_eventos con parámetros $1..$6."""
    fila = {
        "id": "99999999-8888-7777-6666-555555555555",
        "episodio_id": EPISODIO_ID,
        "documento_id": "doc-uuid-interno",
        "usuario_id": USUARIO_ID,
        "evento": "ENRUTAMIENTO_COMPLETADO",
        "descripcion": "Documento enrutado a Cardiología.",
        "metadata": {"destino": "Cardiologia"},
        "created_at": "2026-10-05T10:00:00Z",
    }
    pool, conn = _pool_mockeado(fila)
    metadata = {"destino": "Cardiologia", "score": 0.93}

    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = pool
        resultado = await AuditRepository.registrar_evento_trazabilidad(
            EPISODIO_ID,
            DOCUMENTO_ID,
            USUARIO_ID,
            "ENRUTAMIENTO_COMPLETADO",
            "Documento enrutado a Cardiología.",
            metadata,
        )

    assert resultado == fila
    conn.fetchrow.assert_awaited_once()
    query, *params = conn.fetchrow.await_args.args
    assert "INSERT INTO trazabilidad_eventos" in query
    for placeholder in ("$1", "$2", "$3", "$4", "$5", "$6"):
        assert placeholder in query
    assert params == [
        EPISODIO_ID,
        DOCUMENTO_ID,
        USUARIO_ID,
        "ENRUTAMIENTO_COMPLETADO",
        "Documento enrutado a Cardiología.",
        json.dumps(metadata),
    ]


async def test_registrar_evento_trazabilidad_no_interpola_datos_en_sql():
    """Un payload malicioso viaja como parámetro y nunca dentro del SQL."""
    pool, conn = _pool_mockeado({})
    payload_malicioso = "'); DROP TABLE trazabilidad_eventos;--"

    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = pool
        await AuditRepository.registrar_evento_trazabilidad(
            EPISODIO_ID,
            DOCUMENTO_ID,
            USUARIO_ID,
            payload_malicioso,
            payload_malicioso,
            {"inyeccion": payload_malicioso},
        )

    query, *params = conn.fetchrow.await_args.args
    assert payload_malicioso not in query
    assert "DROP TABLE" not in query
    assert payload_malicioso in params
    assert json.loads(params[5]) == {"inyeccion": payload_malicioso}


async def test_registrar_evento_trazabilidad_metadata_vacia_por_defecto():
    """Sin metadata explícita se persiste un JSONB vacío, respetando el NOT NULL."""
    pool, conn = _pool_mockeado({})

    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = pool
        await AuditRepository.registrar_evento_trazabilidad(
            None, DOCUMENTO_ID, None, "DOCUMENTO_RECIBIDO", "Ingreso por admisión."
        )

    query, *params = conn.fetchrow.await_args.args
    assert "$6::jsonb" in query
    assert params[0] is None
    assert params[2] is None
    assert params[5] == "{}"


async def test_registrar_auditoria_coordinacion_inserta_con_parametros_posicionales():
    """El dictamen HITL se inserta en auditorias_coordinacion con parámetros $1..$5."""
    fila = {
        "id": "88888888-7777-6666-5555-444444444444",
        "episodio_id": EPISODIO_ID,
        "documento_id": "doc-uuid-interno",
        "coordinador_id": COORDINADOR_ID,
        "decision": "reclasificar",
        "justificacion_clinica": "Score ambiguo; se deriva a Medicina Interna.",
        "created_at": "2026-10-05T11:00:00Z",
    }
    pool, conn = _pool_mockeado(fila)

    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = pool
        resultado = await AuditRepository.registrar_auditoria_coordinacion(
            EPISODIO_ID,
            DOCUMENTO_ID,
            COORDINADOR_ID,
            "reclasificar",
            "Score ambiguo; se deriva a Medicina Interna.",
        )

    assert resultado == fila
    conn.fetchrow.assert_awaited_once()
    query, *params = conn.fetchrow.await_args.args
    assert "INSERT INTO auditorias_coordinacion" in query
    assert "justificacion_clinica" in query
    for placeholder in ("$1", "$2", "$3", "$4", "$5"):
        assert placeholder in query
    assert params == [
        EPISODIO_ID,
        DOCUMENTO_ID,
        COORDINADOR_ID,
        "reclasificar",
        "Score ambiguo; se deriva a Medicina Interna.",
    ]


async def test_registrar_auditoria_coordinacion_no_interpola_datos_en_sql():
    """La justificación clínica maliciosa viaja como parámetro y nunca en el SQL."""
    pool, conn = _pool_mockeado({})
    payload_malicioso = "rechazar', 'x'); DELETE FROM auditorias_coordinacion;--"

    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = pool
        await AuditRepository.registrar_auditoria_coordinacion(
            EPISODIO_ID,
            DOCUMENTO_ID,
            COORDINADOR_ID,
            payload_malicioso,
            payload_malicioso,
        )

    query, *params = conn.fetchrow.await_args.args
    assert payload_malicioso not in query
    assert "DELETE FROM" not in query
    assert params[3] == payload_malicioso
    assert params[4] == payload_malicioso


async def test_registrar_evento_trazabilidad_sin_pool_lanza_database_unavailable():
    """Sin PostgreSQL disponible la trazabilidad no se persiste y se reporta el error."""
    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = None
        with pytest.raises(DatabaseUnavailableError):
            await AuditRepository.registrar_evento_trazabilidad(
                EPISODIO_ID,
                DOCUMENTO_ID,
                USUARIO_ID,
                "DOCUMENTO_RECIBIDO",
                "Ingreso por admisión.",
            )


async def test_registrar_auditoria_coordinacion_sin_pool_lanza_database_unavailable():
    """Sin PostgreSQL disponible el dictamen HITL no se persiste y se reporta el error."""
    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = None
        with pytest.raises(DatabaseUnavailableError):
            await AuditRepository.registrar_auditoria_coordinacion(
                EPISODIO_ID,
                DOCUMENTO_ID,
                COORDINADOR_ID,
                "aprobar",
                "Criterio clínico confirmado.",
            )


async def test_error_de_bd_se_envuelve_en_database_unavailable():
    """Un fallo de inserción en PostgreSQL se traduce a DatabaseUnavailableError."""
    pool, conn = _pool_mockeado({})
    conn.fetchrow.side_effect = Exception("connection reset")

    with patch(
        "app.repositories.audit_repository.get_db_pool", new_callable=AsyncMock
    ) as mock_get_pool:
        mock_get_pool.return_value = pool
        with pytest.raises(DatabaseUnavailableError):
            await AuditRepository.registrar_evento_trazabilidad(
                EPISODIO_ID,
                DOCUMENTO_ID,
                USUARIO_ID,
                "OCR_COMPLETADO",
                "Texto extraído del documento.",
            )
        with pytest.raises(DatabaseUnavailableError):
            await AuditRepository.registrar_auditoria_coordinacion(
                EPISODIO_ID,
                DOCUMENTO_ID,
                COORDINADOR_ID,
                "aprobar",
                "Criterio clínico confirmado.",
            )
