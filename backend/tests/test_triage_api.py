import io
from unittest.mock import AsyncMock, patch

from fastapi import status

from app.agent.state import AgentState
from app.repositories.postgres_storage import DatabaseUnavailableError
from app.services.llm_service import LLMUnavailableError


def test_triage_sin_api_key(client):
    """POST /api/v1/triage sin API key debe retornar 401 Unauthorized."""
    payload = {
        "documento_id": "TEST-NO-AUTH",
        "tipo_archivo": "TEXTO",
        "documento_texto": "Texto de prueba",
    }
    response = client.post("/api/v1/triage", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_triage_api_key_invalida(client):
    """POST /api/v1/triage con API key inválida debe retornar 401."""
    payload = {
        "documento_id": "TEST-BAD-KEY",
        "tipo_archivo": "TEXTO",
        "documento_texto": "Texto de prueba",
    }
    response = client.post(
        "/api/v1/triage",
        json=payload,
        headers={"X-API-Key": "wrong-key-value"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_triage_accepts_authenticated_bearer_user(client, bearer_headers):
    """Un trabajador autenticado puede enviar un documento sin exponer una API Key."""
    response = client.post(
        "/api/v1/triage",
        json={
            "documento_id": "DOC-BEARER-TRIAGE",
            "tipo_archivo": "TEXTO",
            "documento_texto": "Analítica normal.",
        },
        headers=bearer_headers,
    )
    assert response.status_code == status.HTTP_200_OK


def test_triage_caso_rutina_api(client, bearer_headers):
    """POST /api/v1/triage procesando caso de rutina retorna 200 y destino Cola_Rutina."""
    payload = {
        "documento_id": "DOC-TEST-RUTINA",
        "tipo_archivo": "TEXTO",
        "documento_texto": "Analítica normal. Hemograma completo sin hallazgos.",
        "canal_origen": "Consulta_Externa",
    }
    response = client.post("/api/v1/triage", json=payload, headers=bearer_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["documento_id"] == "DOC-TEST-RUTINA"
    assert data["decision_enrutamiento"]["destino_principal"] == "Cola_Rutina"
    assert data["decision_enrutamiento"]["requiere_auditoria_humana"] is False


def test_triage_caso_urgencia_api(client, bearer_headers):
    """POST /api/v1/triage procesando urgencia médica retorna 200 y destino Cola_Emergencia_Medica."""
    payload = {
        "documento_id": "DOC-TEST-URGENTE",
        "tipo_archivo": "TEXTO",
        "documento_texto": "TEP agudo detectado. Tromboembolismo pulmonar masivo. Correlación urgente.",
        "canal_origen": "Guardia_Emergencias",
    }
    response = client.post("/api/v1/triage", json=payload, headers=bearer_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["decision_enrutamiento"]["destino_principal"] == "Cola_Emergencia_Medica"
    assert data["clasificacion"]["nivel_prioridad"] == "Urgente"


def test_triage_caso_ambiguo_api_multi_status(client, bearer_headers):
    """POST /api/v1/triage para caso ambiguo debe retornar status 207 Multi-Status."""
    payload = {
        "documento_id": "DOC-TEST-AMBIGUO",
        "tipo_archivo": "TEXTO",
        "documento_texto": "... texto ilegible ... px ??? ... ilegible",
        "canal_origen": "Admision",
    }
    response = client.post("/api/v1/triage", json=payload, headers=bearer_headers)
    assert response.status_code == status.HTTP_207_MULTI_STATUS
    data = response.json()
    assert data["decision_enrutamiento"]["destino_principal"] == "Cola_Revision_Ambigua"
    assert data["decision_enrutamiento"]["requiere_auditoria_humana"] is True


def test_triage_upload_archivo(client, bearer_headers):
    """POST /api/v1/triage/upload acepta una imagen cuya firma coincide con el MIME."""
    contenido = b"\x89PNG\r\n\x1a\ncontenido-prueba"
    archivo = ("reporte.png", io.BytesIO(contenido), "image/png")
    data = {
        "documento_id": "DOC-UPLOAD-01",
        "canal_origen": "Laboratorio_Central",
    }
    result = AgentState(documento_id="DOC-UPLOAD-01", tipo_archivo="IMAGEN", status="procesado")
    with patch(
        "app.services.triage_service.TriageService.procesar_documento",
        new=AsyncMock(return_value=result),
    ) as process:
        response = client.post(
            "/api/v1/triage/upload",
            data=data,
            files={"archivo": archivo},
            headers={"Authorization": bearer_headers["Authorization"]},
        )
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_207_MULTI_STATUS]
    res_data = response.json()
    assert res_data["documento_id"] == "DOC-UPLOAD-01"
    assert process.await_args.kwargs["tipo_archivo"] == "IMAGEN"


def test_triage_upload_rechaza_mime_no_permitido(client, bearer_headers):
    response = client.post(
        "/api/v1/triage/upload",
        data={"documento_id": "DOC-UPLOAD-TXT"},
        files={"archivo": ("reporte.txt", io.BytesIO(b"texto"), "text/plain")},
        headers={"Authorization": bearer_headers["Authorization"]},
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_triage_upload_rechaza_contenido_que_no_coincide_con_mime(client, bearer_headers):
    response = client.post(
        "/api/v1/triage/upload",
        data={"documento_id": "DOC-UPLOAD-FALSO"},
        files={"archivo": ("reporte.pdf", io.BytesIO(b"no es un pdf"), "application/pdf")},
        headers={"Authorization": bearer_headers["Authorization"]},
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE


def test_triage_retorna_503_si_postgres_no_persiste(client, bearer_headers):
    with patch(
        "app.repositories.postgres_storage.PostgresStorageRepository.guardar_resultado",
        new=AsyncMock(side_effect=DatabaseUnavailableError("PostgreSQL caído")),
    ):
        response = client.post(
            "/api/v1/triage",
            json={
                "documento_id": "DOC-DB-FAIL",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Analítica normal.",
            },
            headers=bearer_headers,
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"]["error"] == "POSTGRES_NO_DISPONIBLE"


def test_triage_retorna_503_si_no_hay_proveedor_llm(client, bearer_headers):
    with patch(
        "app.services.triage_service.TriageService.procesar_documento",
        new=AsyncMock(side_effect=LLMUnavailableError("Sin proveedor")),
    ):
        response = client.post(
            "/api/v1/triage",
            json={
                "documento_id": "DOC-LLM-FAIL",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Analítica normal.",
            },
            headers=bearer_headers,
        )

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"]["error"] == "LLM_NO_DISPONIBLE"
