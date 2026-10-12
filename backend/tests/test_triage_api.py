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


def test_triage_auto_crea_episodio_paciente_sin_episodio_activo(client, bearer_headers):
    """US1 (P1): Si paciente está asociado y no tiene episodio activo, crea uno automáticamente."""
    mock_paciente = {
        "id": "11111111-2222-3333-4444-555555555555",
        "numero_documento": "12345678",
        "nombres": "Carlos",
        "apellidos": "Ruiz",
    }
    nuevo_epi = {
        "id": "aaaa1111-bbbb-2222-cccc-333333333333",
        "codigo_episodio": "EP-20261011-TEST",
        "paciente_id": mock_paciente["id"],
        "estado_atencion": "ingresado",
    }

    with (
        patch(
            "app.repositories.patient_repository.resolver_paciente_por_identificadores",
            new_callable=AsyncMock,
        ) as mock_resolver,
        patch(
            "app.repositories.episode_repository.get_active_episode_by_patient",
            new_callable=AsyncMock,
        ) as mock_get_active,
        patch(
            "app.repositories.episode_repository.create_episode",
            new_callable=AsyncMock,
        ) as mock_create_epi,
        patch(
            "app.repositories.audit_repository.AuditRepository.registrar_evento_trazabilidad",
            new_callable=AsyncMock,
        ) as mock_audit,
    ):
        mock_resolver.return_value = {"estado": "asociado", "paciente": mock_paciente}
        mock_get_active.return_value = None
        mock_create_epi.return_value = nuevo_epi
        mock_audit.return_value = {"id": "audit-uuid-1"}

        response = client.post(
            "/api/v1/triage",
            json={
                "documento_id": "DOC-AUTO-EPI-001",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Paciente Carlos Ruiz DNI 12345678. Dolor torácico moderado.",
            },
            headers=bearer_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["metadata"]["episodio_id"] == nuevo_epi["id"]
        assert data["metadata"]["codigo_episodio"] == nuevo_epi["codigo_episodio"]
        assert data["metadata"]["episodio_nuevo"] is True
        mock_create_epi.assert_called_once()


def test_triage_asocia_episodio_activo_existente_sin_duplicar(client, bearer_headers):
    """US2 (P2): Si paciente ya tiene episodio activo, asocia el documento sin duplicar."""
    mock_paciente = {
        "id": "11111111-2222-3333-4444-555555555555",
        "numero_documento": "12345678",
        "nombres": "Carlos",
        "apellidos": "Ruiz",
    }
    epi_existente = {
        "episodio_id": "bbbb2222-cccc-3333-dddd-444444444444",
        "codigo_episodio": "EP-20261011-EXIST",
        "paciente_id": mock_paciente["id"],
        "estado_atencion": "en_triaje",
    }

    with (
        patch(
            "app.repositories.patient_repository.resolver_paciente_por_identificadores",
            new_callable=AsyncMock,
        ) as mock_resolver,
        patch(
            "app.repositories.episode_repository.get_active_episode_by_patient",
            new_callable=AsyncMock,
        ) as mock_get_active,
        patch(
            "app.repositories.episode_repository.create_episode",
            new_callable=AsyncMock,
        ) as mock_create_epi,
        patch(
            "app.repositories.audit_repository.AuditRepository.registrar_evento_trazabilidad",
            new_callable=AsyncMock,
        ) as mock_audit,
    ):
        mock_resolver.return_value = {"estado": "asociado", "paciente": mock_paciente}
        mock_get_active.return_value = epi_existente
        mock_audit.return_value = {"id": "audit-uuid-2"}

        response = client.post(
            "/api/v1/triage",
            json={
                "documento_id": "DOC-LINK-EPI-002",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Paciente Carlos Ruiz DNI 12345678. Analítica de control.",
            },
            headers=bearer_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["metadata"]["episodio_id"] == epi_existente["episodio_id"]
        assert data["metadata"]["codigo_episodio"] == epi_existente["codigo_episodio"]
        assert data["metadata"]["episodio_nuevo"] is False
        mock_create_epi.assert_not_called()


def test_triage_registra_evento_inmutable_trazabilidad(client, bearer_headers):
    """US3 (P3): Verifica que se emite DOCUMENTO_ASOCIADO_A_EPISODIO en trazabilidad_eventos."""
    mock_paciente = {
        "id": "11111111-2222-3333-4444-555555555555",
        "numero_documento": "12345678",
    }
    nuevo_epi = {
        "id": "aaaa1111-bbbb-2222-cccc-333333333333",
        "codigo_episodio": "EP-20261011-TEST",
    }

    with (
        patch(
            "app.repositories.patient_repository.resolver_paciente_por_identificadores",
            new_callable=AsyncMock,
        ) as mock_resolver,
        patch(
            "app.repositories.episode_repository.get_active_episode_by_patient",
            new_callable=AsyncMock,
        ) as mock_get_active,
        patch(
            "app.repositories.episode_repository.create_episode",
            new_callable=AsyncMock,
        ) as mock_create_epi,
        patch(
            "app.repositories.audit_repository.AuditRepository.registrar_evento_trazabilidad",
            new_callable=AsyncMock,
        ) as mock_audit,
    ):
        mock_resolver.return_value = {"estado": "asociado", "paciente": mock_paciente}
        mock_get_active.return_value = None
        mock_create_epi.return_value = nuevo_epi
        mock_audit.return_value = {"id": "audit-uuid-3"}

        response = client.post(
            "/api/v1/triage",
            json={
                "documento_id": "DOC-AUDIT-EPI-003",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Paciente DNI 12345678 para triaje.",
            },
            headers=bearer_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        mock_audit.assert_called_once()
        args, kwargs = mock_audit.call_args
        assert kwargs.get("evento") == "DOCUMENTO_ASOCIADO_A_EPISODIO" or (len(args) > 3 and args[3] == "DOCUMENTO_ASOCIADO_A_EPISODIO")


def test_triage_resiliencia_si_falla_orquestacion_episodio(client, bearer_headers):
    """US4 (P4): Si la orquestación de episodio falla, el triaje entrega su resultado con 200 OK."""
    mock_paciente = {
        "id": "11111111-2222-3333-4444-555555555555",
        "numero_documento": "12345678",
    }

    with (
        patch(
            "app.repositories.patient_repository.resolver_paciente_por_identificadores",
            new_callable=AsyncMock,
        ) as mock_resolver,
        patch(
            "app.repositories.episode_repository.get_active_episode_by_patient",
            new_callable=AsyncMock,
            side_effect=Exception("Error transitorio en pool de episodios"),
        ),
    ):
        mock_resolver.return_value = {"estado": "asociado", "paciente": mock_paciente}

        response = client.post(
            "/api/v1/triage",
            json={
                "documento_id": "DOC-RESILIENCIA-004",
                "tipo_archivo": "TEXTO",
                "documento_texto": "Paciente DNI 12345678 informe.",
            },
            headers=bearer_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "episodio_error" in data["metadata"]

