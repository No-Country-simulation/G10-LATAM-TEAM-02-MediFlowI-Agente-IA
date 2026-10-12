from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_episode():
    response = client.post(
        "/api/v1/episodes/",
        json={
            "patient_id": "PAT-TEST-123",
            "motivo_consulta": "Dolor abdominal agudo",
            "canal_origen": "Urgencias"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "episode_id" in data
    assert data["motivo_consulta"] == "Dolor abdominal agudo"
    assert data["estado"] == "activo"

def test_get_episode_by_id():
    create_response = client.post(
        "/api/v1/episodes/",
        json={
            "patient_id": "PAT-TEST-456",
            "motivo_consulta": "Fiebre persistente",
            "canal_origen": "Consulta_Externa"
        }
    )
    created_data = create_response.json()
    episode_id = created_data["episode_id"]

    response = client.get(f"/api/v1/episodes/{episode_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["episode_id"] == episode_id
    # Verificamos que el episodio exista y devuelva sus datos correctamente
    assert "motivo_consulta" in data
    assert data["estado"] == "activo"