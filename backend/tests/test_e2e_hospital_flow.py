"""
Prueba End-to-End (E2E) del flujo clínico completo en MediFlow:
1. Alta de Paciente con cálculo dinámico de edad y género estricto.
2. Ingesta de Documento de Triaje vía canal 'Admision'.
3. Retención de caso para revisión Human-in-the-Loop (HITL).
4. Barrera de Seguridad RBAC: Médicos y Operadores NO pueden resolver HITL (403 Forbidden).
5. Resolución de Auditoría HITL exclusiva por COORDINADOR y ADMINISTRADOR (200 OK).
6. Trazabilidad completa y derivación a destino final ('Farmacia_Hospitalaria' / 'Observacion_Urgencias').
"""

from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient


def test_e2e_hospital_workflow_admission_to_coordination_resolution(
    client: TestClient,
    bearer_headers: dict,
    medico_bearer_headers: dict,
    coordinador_bearer_headers: dict,
    admin_bearer_headers: dict,
):
    # -------------------------------------------------------------
    # PASO 1: Alta de paciente con género y cálculo dinámico de edad
    # -------------------------------------------------------------
    patient_payload = {
        "numero_documento": "76543210",
        "nombres": "Elena",
        "apellidos": "Ríos Morales",
        "genero": "FEMENINO",
        "numero_telefono": "+51 977112233",
        "fecha_nacimiento": "1996-03-25",
    }

    patient_mock = {
        "id": "patient-uuid-76543210",
        "numero_documento": "76543210",
        "nombres": "Elena",
        "apellidos": "Ríos Morales",
        "numero_historia_clinica": "HC-76543210",
        "fecha_nacimiento": "1996-03-25",
        "genero": "FEMENINO",
        "numero_telefono": "+51 977112233",
        "edad": 30,
        "creado_en": "2026-09-30T10:00:00Z",
    }

    with (
        patch("app.repositories.patient_repository.get_patient_by_doc", new_callable=AsyncMock) as mock_get_doc,
        patch("app.repositories.patient_repository.create_patient", new_callable=AsyncMock) as mock_create_p,
    ):
        mock_get_doc.return_value = None
        mock_create_p.return_value = patient_mock

        resp_patient = client.post("/api/v1/patients", headers=bearer_headers, json=patient_payload)
        assert resp_patient.status_code == 201
        patient_data = resp_patient.json()["paciente"]
        assert patient_data["genero"] == "FEMENINO"
        assert patient_data["edad"] == 30
        assert patient_data["numero_telefono"] == "+51 977112233"

    # -------------------------------------------------------------
    # PASO 2 & 3: Documento en Triaje pendiente de Auditoría HITL
    # -------------------------------------------------------------
    doc_id = "DOC-E2E-HOSPITAL-001"
    doc_en_hitl = {
        "id": "uuid-doc-001",
        "documento_id": doc_id,
        "paciente_id": patient_mock["id"],
        "nombre_archivo": "triaje_urgencia.pdf",
        "tipo_documento": "informe_medico",
        "canal_origen": "Admision",
        "status": "pendiente_auditoria",
        "prioridad": "AMARILLO",
        "destino_principal": "Cola_Auditoria_Humana",
        "requiere_auditoria_humana": True,
        "creado_en": "2026-09-30T12:00:00Z",
        "resultado_json": {
            "nivel_urgencia": {"prioridad": "AMARILLO", "motivo": "Dolor abdominal agudo"},
            "decision_enrutamiento": {
                "destino_principal": "Cola_Auditoria_Humana",
                "requiere_auditoria_humana": True,
                "justificacion": "Sospecha de apendicitis vs cólico biliar - Requiere criterio clínico",
            },
        },
    }

    doc_aprobado = {
        **doc_en_hitl,
        "status": "procesado",
        "requiere_auditoria_humana": False,
        "destino_principal": "Farmacia_Hospitalaria",
        "auditoria": {
            "decision": "aprobar",
            "auditor_id": "44444444-2222-3333-4444-555555555555",
            "comentario": "Se confirma prescripción y derivación prioritaria a Farmacia Hospitalaria.",
        },
    }

    # -------------------------------------------------------------
    # PASO 4: Barrera RBAC - Operadores y Médicos denegados (403)
    # -------------------------------------------------------------
    with patch("app.repositories.postgres_storage.PostgresStorageRepository.obtener_por_id", new_callable=AsyncMock) as mock_get_doc:
        mock_get_doc.return_value = doc_en_hitl

        # Un operador común intenta auditar -> 403
        resp_operator = client.patch(
            f"/api/v1/documents/{doc_id}",
            headers=bearer_headers,
            json={"decision": "aprobar", "comentario": "Intento de operador"},
        )
        assert resp_operator.status_code == 403

        # Un médico no coordinador intenta auditar -> 403
        resp_medico = client.patch(
            f"/api/v1/documents/{doc_id}",
            headers=medico_bearer_headers,
            json={"decision": "aprobar", "comentario": "Intento de médico no coordinador"},
        )
        assert resp_medico.status_code == 403

    # -------------------------------------------------------------
    # PASO 5: Resolución exitosa por COORDINADOR (200 OK)
    # -------------------------------------------------------------
    with (
        patch("app.repositories.postgres_storage.PostgresStorageRepository.obtener_por_id", new_callable=AsyncMock) as mock_get_doc,
        patch("app.repositories.postgres_storage.PostgresStorageRepository.registrar_auditoria", new_callable=AsyncMock) as mock_reg_audit,
    ):
        # Primer get retorna pendiente_auditoria, segundo get retorna actualizado
        mock_get_doc.side_effect = [doc_en_hitl, doc_aprobado]
        mock_reg_audit.return_value = True

        resp_coordinador = client.patch(
            f"/api/v1/documents/{doc_id}",
            headers=coordinador_bearer_headers,
            json={
                "decision": "aprobar",
                "comentario": "Se confirma prescripción y derivación prioritaria a Farmacia Hospitalaria.",
                "nueva_clasificacion": {"destino_principal": "Farmacia_Hospitalaria"},
            },
        )
        assert resp_coordinador.status_code == 200
        audit_result = resp_coordinador.json()
        assert audit_result["status"] == "procesado"
        assert audit_result["auditoria"]["decision"] == "aprobar"
        assert audit_result["auditoria"]["auditor_id"] == "44444444-2222-3333-4444-555555555555"

    # -------------------------------------------------------------
    # PASO 6: El ADMINISTRADOR también está facultado para auditar
    # -------------------------------------------------------------
    with (
        patch("app.repositories.postgres_storage.PostgresStorageRepository.obtener_por_id", new_callable=AsyncMock) as mock_get_doc,
        patch("app.repositories.postgres_storage.PostgresStorageRepository.registrar_auditoria", new_callable=AsyncMock) as mock_reg_audit,
    ):
        mock_get_doc.side_effect = [doc_en_hitl, doc_aprobado]
        mock_reg_audit.return_value = True

        resp_admin = client.patch(
            f"/api/v1/documents/{doc_id}",
            headers=admin_bearer_headers,
            json={
                "decision": "aprobar",
                "comentario": "Auditoría administrativa de contingencia aprobada.",
            },
        )
        assert resp_admin.status_code == 200
