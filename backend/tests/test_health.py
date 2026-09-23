def test_health_check_publico(client):
    """GET /health debe ser accesible sin autenticación y retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "version" in data
    assert "llm_disponible" in data
    assert "oci_disponible" in data
