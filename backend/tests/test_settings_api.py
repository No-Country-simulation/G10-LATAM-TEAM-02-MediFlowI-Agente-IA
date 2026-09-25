import pytest


def test_obtener_configuracion(client, admin_bearer_headers):
    """GET /api/v1/settings retorna la configuración actual."""
    response = client.get("/api/v1/settings", headers=admin_bearer_headers)
    assert response.status_code == 200
    data = response.json()
    assert "storage_mode" in data
    assert "oci_configured" in data
    assert "llm_provider" in data
    assert "llm_configured" in data
    assert "database_url_configured" in data


def test_actualizar_configuracion_local(client, admin_bearer_headers):
    """POST /api/v1/settings permite cambiar a modo LOCAL."""
    response = client.post("/api/v1/settings", headers=admin_bearer_headers, json={"storage_mode": "LOCAL"})
    assert response.status_code == 200
    data = response.json()
    assert data["storage_mode"] == "LOCAL"


def test_actualizar_configuracion_oci_o_validacion(client, admin_bearer_headers):
    """POST /api/v1/settings procesa la solicitud de OCI según credenciales."""
    response = client.post("/api/v1/settings", headers=admin_bearer_headers, json={"storage_mode": "OCI"})
    # Retorna 200 si OCI está configurado o 400 si faltan credenciales en el entorno
    assert response.status_code in [200, 400]
    data = response.json()
    if response.status_code == 200:
        assert data["storage_mode"] == "OCI"
    else:
        assert data["detail"]["error"] == "OCI_NO_CONFIGURADO"
