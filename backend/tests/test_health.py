from unittest.mock import AsyncMock, patch


def test_health_check_publico(client):
    """Sin PostgreSQL el endpoint público informa 503, nunca 401 por falta de token."""
    with patch("app.api.v1.health.get_db_pool", new=AsyncMock(return_value=None)):
        response = client.get("/health")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "unavailable"
    assert data["postgres_disponible"] is False
    assert "version" in data
    assert "llm_disponible" in data
    assert "oci_disponible" in data
