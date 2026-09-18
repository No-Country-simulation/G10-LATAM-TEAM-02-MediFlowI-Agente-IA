"""
Test de Contrato: Valida que la API FastAPI responde según la especificación OpenAPI 3.0
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check_contract():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "version" in data
    assert "services" in data

def test_triaje_urgencia_tep_contract():
    """Valida Caso 2: TEP Agudo hacia Cola_Emergencia_Medica"""
    payload = {
        "documento_id": "DOC-CLIN-2026-8942",
        "tipo_archivo": "PDF",
        "documento_texto": "HOSPITAL SANTA LUCIA - INFORME RADIOLOGICO. Paciente: Carlos Eduardo Mendes, 52 anos. Medico Solicitante: Dra. Renata Silveira MP 145892. Estudio: Tomografia de Torax con contraste. CONCLUSION: Tromboembolismo Pulmonar Agudo (TEP).",
        "canal_origen": "Guardia_Emergencias"
    }
    response = client.post("/api/v1/triaje", json=payload)
    assert response.status_code == 200
    res = response.json()

    # Validar campos de contrato
    assert res["status"] == "procesado"
    assert res["documento_id"] == "DOC-CLIN-2026-8942"
    assert res["clasificacion"]["nivel_prioridad"] == "Urgente"
    assert res["decision_enrutamiento"]["destino_principal"] == "Cola_Emergencia_Medica"
    assert res["decision_enrutamiento"]["requiere_auditoria_humana"] is False
    assert res["decision_enrutamiento"]["notificacion_generada"] is not None
    assert "TEP" in res["decision_enrutamiento"]["notificacion_generada"]["mensaje"]
    assert "procesados/urgentes" in res["almacenamiento_oci"]["ruta_objeto"]

def test_triaje_hitl_ambiguo_contract():
    """Valida Caso 3: Documento ilegible derivado a Cola_Auditoria_Humana"""
    payload = {
        "documento_id": "DOC-CLIN-2026-9999",
        "tipo_archivo": "IMAGEN",
        "documento_texto": "Texto borroso ilegible. Prescripcion no identificable.",
        "canal_origen": "Consulta_Externa"
    }
    response = client.post("/api/v1/triaje", json=payload)
    assert response.status_code == 200
    res = response.json()

    assert res["status"] == "pendiente_auditoria"
    assert res["clasificacion"]["score_confianza_clasificacion"] < 0.85
    assert res["decision_enrutamiento"]["destino_principal"] == "Cola_Auditoria_Humana"
    assert res["decision_enrutamiento"]["requiere_auditoria_humana"] is True
    assert "auditoria_humana" in res["almacenamiento_oci"]["ruta_objeto"]


def test_resolver_auditoria_contract():
    """Valida contrato del endpoint POST /api/v1/auditoria/{documento_id} según openapi.yaml"""
    payload = {
        "decision": "aprobado",
        "auditor_nombre": "Dr. Alejandro Morales",
        "comentarios": "Confirmada dosis de heparina e indicación de guardia",
        "datos_corregidos": {
            "paciente": {
                "nombre": "Carlos Eduardo Mendes",
                "edad": 52
            },
            "diagnostico_principal": "Tromboembolismo Pulmonar Agudo",
            "cie10_sugerido": "I26.9",
            "medicamentos": [{"nombre": "Heparina Sodica"}],
            "medico_solicitante": {"nombre": "Dra. Renata Silveira"}
        }
    }
    response = client.post("/api/v1/auditoria/DOC-CLIN-2026-9999", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["status"] == "auditoria_completada"
    assert res["documento_id"] == "DOC-CLIN-2026-9999"
    assert "procesados/auditados/DOC-CLIN-2026-9999.json" in res["nueva_ruta_oci"]


def test_resolver_auditoria_invalid_payload_contract():
    """Valida que un payload sin los campos requeridos por openapi.yaml falle con 422 (Unprocessable Entity)"""
    payload_invalido = {
        "auditor_id": "AUD-01"  # Campo legacy obsoleto, faltan decision, datos_corregidos, auditor_nombre
    }
    response = client.post("/api/v1/auditoria/DOC-CLIN-2026-9999", json=payload_invalido)
    assert response.status_code == 422

