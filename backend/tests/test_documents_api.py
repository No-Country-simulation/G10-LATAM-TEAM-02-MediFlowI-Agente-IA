from fastapi import status


def test_listar_documentos_auth_required(client):
    """GET /api/v1/documents sin auth retorna 401."""
    response = client.get("/api/v1/documents")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_listar_documentos(client, auth_headers):
    """GET /api/v1/documents con auth retorna estructura de lista."""
    response = client.get("/api/v1/documents", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_obtener_documento_inexistente(client, auth_headers):
    """GET /api/v1/documents/no-existe retorna 404."""
    response = client.get("/api/v1/documents/NO-EXISTE-9999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_triage_y_obtener_documento(client, auth_headers):
    """Flujo completo: triage guarda el documento en mock storage y se puede consultar."""
    doc_id = "DOC-FLOW-123"
    triage_payload = {
        "documento_id": doc_id,
        "tipo_archivo": "TEXTO",
        "documento_texto": "Analítica normal de control.",
        "canal_origen": "Consulta_Externa",
    }
    post_res = client.post("/api/v1/triage", json=triage_payload, headers=auth_headers)
    assert post_res.status_code == status.HTTP_200_OK

    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert get_res.status_code == status.HTTP_200_OK
    doc_data = get_res.json()
    assert doc_data["documento_id"] == doc_id
