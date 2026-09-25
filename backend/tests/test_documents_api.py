from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.agent.state import AgentState
from app.api.v1.documents import DecisionAuditoriaRequest, _aplicar_correcciones
from app.core.config import get_settings
from app.repositories.postgres_storage import DatabaseUnavailableError, PostgresStorageRepository


def test_rechazar_documento_maps_to_rechazado_status():
    """Un rechazo HITL es una decisión clínica válida, no un fallo técnico."""
    from app.repositories.postgres_storage import estado_final_auditoria

    assert estado_final_auditoria("rechazar") == "rechazado"


def test_rechazar_documento_creates_rejection_history_event():
    """La trazabilidad distingue un rechazo de un error técnico."""
    from app.repositories.postgres_storage import evento_auditoria

    assert evento_auditoria("rechazar") == "AUDITORIA_RECHAZADA"


def test_aplicar_correcciones_hitl_updates_supported_clinical_fields():
    """Las correcciones enviadas por la UI se aplican al resultado clínico persistido."""
    document = {
        "clasificacion": {"tipo_documento": "Desconocido", "nivel_prioridad": "Ambiguo"},
        "datos_extraidos": {
            "paciente": {"nombre": "Paciente ilegible"},
            "medico_solicitante": {},
        },
        "decision_enrutamiento": {"destino_principal": "Cola_Revision_Ambigua"},
    }
    payload = DecisionAuditoriaRequest(
        decision="reclasificar",
        nueva_clasificacion={
            "tipo_documento": "Receta Médica",
            "nivel_prioridad": "Rutina",
            "destino": "Cola_Rutina",
        },
        datos_corregidos={
            "paciente": {"nombre": "Ana Pérez", "dni": "44556677", "edad": "38"},
            "medico": {"nombre": "Dra. Torres", "cmp": "CMP-123"},
            "diagnostico": "Hipertensión arterial",
            "cie10": "I10",
        },
    )

    _aplicar_correcciones(document, payload)

    assert document["clasificacion"]["tipo_documento"] == "Receta Médica"
    assert document["clasificacion"]["nivel_prioridad"] == "Rutina"
    assert document["datos_extraidos"]["paciente"] == {
        "nombre": "Ana Pérez",
        "documento_identidad": "44556677",
        "edad": 38,
    }
    assert document["datos_extraidos"]["medico_solicitante"]["matricula"] == "CMP-123"
    assert document["datos_extraidos"]["diagnostico_principal"] == "Hipertensión arterial"
    assert document["datos_extraidos"]["cie10_sugerido"] == "I10"
    assert document["decision_enrutamiento"]["destino_principal"] == "Cola_Rutina"


@pytest.mark.asyncio
async def test_postgres_sin_configuracion_no_activa_fallback_en_memoria():
    repository = PostgresStorageRepository(get_settings().model_copy(update={"database_url": ""}))

    with pytest.raises(DatabaseUnavailableError):
        await repository.inicializar()


@pytest.mark.repository_mock
@pytest.mark.asyncio
async def test_guardar_resultado_records_uploader_and_processing_history():
    """Guardar un triaje registra actor y secuencia funcional en PostgreSQL/mock."""
    repository = PostgresStorageRepository(
        get_settings().model_copy(update={"database_url": ""}),
        allow_in_memory=True,
    )
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


def test_auditoria_updates_and_returns_postgres_canonical_state(
    client,
    auditor_bearer_headers,
):
    pending = {"documento_id": "DOC-AUDIT-1", "status": "pendiente_auditoria"}
    updated = {
        "documento_id": "DOC-AUDIT-1",
        "status": "procesado",
        "tipo_documento": "Receta Médica",
        "nivel_prioridad": "Rutina",
        "requiere_auditoria_humana": False,
    }
    with (
        patch(
            "app.api.v1.documents.PostgresStorageRepository.obtener_por_id",
            new_callable=AsyncMock,
            side_effect=[pending, updated],
        ),
        patch(
            "app.api.v1.documents.PostgresStorageRepository.registrar_auditoria",
            new_callable=AsyncMock,
            return_value=True,
        ) as register,
    ):
        response = client.patch(
            "/api/v1/documents/DOC-AUDIT-1",
            json={"decision": "aprobar", "comentario": "Validado"},
            headers=auditor_bearer_headers,
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "procesado"
    assert response.json()["auditoria"]["auditor_id"] == ("22222222-2222-3333-4444-555555555555")
    register.assert_awaited_once()


def test_auditoria_rejects_document_that_is_no_longer_pending(
    client,
    auditor_bearer_headers,
):
    with patch(
        "app.api.v1.documents.PostgresStorageRepository.obtener_por_id",
        new_callable=AsyncMock,
        return_value={"documento_id": "DOC-DONE", "status": "procesado"},
    ):
        response = client.patch(
            "/api/v1/documents/DOC-DONE",
            json={"decision": "aprobar"},
            headers=auditor_bearer_headers,
        )

    assert response.status_code == status.HTTP_409_CONFLICT


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

    persisted_row = {
        "documento_id": doc_id,
        "status": "procesado",
        "tipo_documento": "Informe de Laboratorio",
        "nivel_prioridad": "Rutina",
    }
    with patch(
        "app.api.v1.documents.PostgresStorageRepository.obtener_por_id",
        new_callable=AsyncMock,
        return_value=persisted_row,
    ):
        get_res = client.get(f"/api/v1/documents/{doc_id}", headers=bearer_headers)
    assert get_res.status_code == status.HTTP_200_OK
    doc_data = get_res.json()
    assert doc_data["documento_id"] == doc_id


def test_obtener_documento_uses_postgres_without_physical_json(client, bearer_headers):
    row = {
        "documento_id": "DOC-PG-ONLY",
        "status": "procesado",
        "texto_extraido": "Contenido canónico",
        "tipo_documento": "Historia Clínica",
        "nivel_prioridad": "Rutina",
        "oci_status": "error",
    }
    with patch(
        "app.api.v1.documents.PostgresStorageRepository.obtener_por_id",
        new_callable=AsyncMock,
        return_value=row,
    ):
        response = client.get(
            "/api/v1/documents/DOC-PG-ONLY",
            headers=bearer_headers,
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["texto_extraido"] == "Contenido canónico"
    assert response.json()["almacenamiento_oci"]["status_backup"] == "error"
