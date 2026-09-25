from unittest.mock import AsyncMock, patch

from fastapi import status


class _Connection:
    async def fetchval(self, query: str) -> int:
        assert query == "SELECT 1"
        return 1


class _AcquireContext:
    async def __aenter__(self):
        return _Connection()

    async def __aexit__(self, exc_type, exc, traceback):
        return False


class _Pool:
    def acquire(self):
        return _AcquireContext()


def test_health_retorna_503_si_postgres_no_esta_disponible(client):
    with patch("app.api.v1.health.get_db_pool", new=AsyncMock(return_value=None)):
        response = client.get("/health")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["status"] == "unavailable"
    assert response.json()["postgres_disponible"] is False


def test_health_confirma_postgres_con_consulta_real(client):
    with patch("app.api.v1.health.get_db_pool", new=AsyncMock(return_value=_Pool())):
        response = client.get("/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"
    assert response.json()["postgres_disponible"] is True
