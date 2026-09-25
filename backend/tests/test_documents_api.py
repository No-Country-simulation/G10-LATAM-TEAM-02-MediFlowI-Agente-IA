import pytest
from fastapi import status

from app.agent.state import AgentState
from app.core.config import get_settings
from app.repositories.postgres_storage import PostgresStorageRepository


def test_rechazar_documento_maps_to_rechazado_status():
    """Un rechazo HITL es una decisión clínica válida, no un fallo técnico."""
    from app.repositories.postgres_storage import estado_final_auditoria

    assert estado_final_auditoria("rechazar") == "rechazado"


def test_rechazar_documento_creates_rejection_history_event():
    """La trazabilidad distingue un rechazo de un error técnico."""
    from app.repositories.postgres_storage import evento_auditoria

    assert evento_auditoria("rechazar") == "AUDITORIA_RECHAZADA"


@pytest.mark.repository_mock
@pytest.mark.asyncio
async def test_guardar_resultado_records_uploader_and_processing_history():
    """Guardar un triaje registra actor y secuencia funcional en PostgreSQL/mock."""
    repository = PostgresStorageRepository(get_settings().model_copy(update={"database_url": ""}))
    result = AgentState(documento_id="DOC-HISTORY-1", tipo_archivo="TEXTO", status="procesado")

    await repository.guardar_resultado(
        result,
        usuario_registro_id="11111111-2222-3333-4444-555555555555",
    )

    saved = await repository.obtener_por_id("DOC-HISTORY-1")
    history = await repository.listar_historial("DOC-HISTORY-1")
    assert saved["usuario_registro_id"] == "11111111-2222-3333-4444-555555555555"
    assert [event["evento"] for event in history] == [
        "DOCUMENTO_RECIBIDO",
        "PROCESAMIENTO_INICIADO",
        "OCR_COMPLETADO",
        "EXTRACCION_IA_COMPLETADA",
        "CLASIFICACION_COMPLETADA",
        "ENRUTAMIENTO_COMPLETADO",
        "PROCESAMIENTO_FINALIZADO",
    ]


def test_listar_documentos_auth_required(client):
    """GET /api/v1/documents sin auth retorna 401."""
    response = client.get("/api/v1/documents")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_listar_documentos(client, bearer_headers):
    """GET /api/v1/documents con auth retorna estructura de lista."""
    response = client.get("/api/v1/documents", headers=bearer_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "items" in data
    assert isinstance(data["items"], list)


def test_listar_documentos_accepts_authenticated_bearer_user(client, bearer_headers):
    """La consola clínica consulta documentos mediante su sesión Bearer."""
    response = client.get("/api/v1/documents", headers=bearer_headers)
    assert response.status_code == status.HTTP_200_OK


def test_historial_documento_requires_authentication(client):
    response = client.get("/api/v1/documents/DOC-HISTORY-1/historial")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_historial_documento_is_available_to_authenticated_user(client, bearer_headers):
    response = client.get("/api/v1/documents/DOC-HISTORY-1/historial", headers=bearer_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"documento_id": "DOC-HISTORY-1", "items": []}


def test_auditoria_uses_authenticated_auditor_not_request_body(client, auditor_bearer_headers):
    """El endpoint no debe requerir un auditor_id controlado por el cliente."""
    response = client.patch(
        "/api/v1/documents/DOC-INEXISTENTE",
        json={"decision": "aprobar"},
        headers=auditor_bearer_headers,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_operador_cannot_register_audit_decision(client, bearer_headers):
    """Un operador no puede ejecutar decisiones HITL."""
    response = client.patch(
        "/api/v1/documents/DOC-INEXISTENTE",
        json={"decision": "aprobar"},
        headers=bearer_headers,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_obtener_documento_inexistente(client, bearer_headers):
    """GET /api/v1/documents/no-existe retorna 404."""
    response = client.get("/api/v1/documents/NO-EXISTE-9999", headers=bearer_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_triage_y_obtener_documento(client, bearer_headers):
    """Flujo completo: triage guarda el documento en mock storage y se puede consultar."""
    doc_id = "DOC-FLOW-123"
    triage_payload = {
        "documento_id": doc_id,
        "tipo_archivo": "TEXTO",
        "documento_texto": "Analítica normal de control.",
        "canal_origen": "Consulta_Externa",
    }
    post_res = client.post("/api/v1/triage", json=triage_payload, headers=bearer_headers)
    assert post_res.status_code == status.HTTP_200_OK

    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=bearer_headers)
    assert get_res.status_code == status.HTTP_200_OK
    doc_data = get_res.json()
    assert doc_data["documento_id"] == doc_id
