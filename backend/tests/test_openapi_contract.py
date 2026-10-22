"""Comparación de JSON reales del API con el contrato, con persistencia simulada."""

import importlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import yaml
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from app._generated.models import DocumentoClinico, ResultadoTriaje

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "infrastructure/scripts"))
from sdd import bundle_spec


@pytest.fixture(scope="module")
def contract(tmp_path_factory):
    path = tmp_path_factory.mktemp("contract") / "openapi.json"
    bundle_spec(path)
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(contract, obj):
    while "$ref" in obj:
        target = contract
        for key in obj["$ref"][2:].split("/"):
            target = target[key.replace("~1", "/").replace("~0", "~")]
        obj = target
    return obj


def assert_response(contract, route, method, response):
    declared = contract["paths"][route][method]["responses"][str(response.status_code)]
    schema = resolve(contract, declared)["content"]["application/json"]["schema"]
    Draft202012Validator({**schema, "components": contract["components"]}).validate(response.json())


@pytest.mark.parametrize(
    "text",
    [
        "Analítica normal. Hemograma sin hallazgos.",
        "TEP agudo. Tromboembolismo pulmonar masivo.",
        "... texto ilegible ... ???",
        "",
    ],
)
def test_triage_json_matches_contract(contract, client, bearer_headers, text):
    response = client.post(
        "/api/v1/triage",
        headers=bearer_headers,
        json={
            "documento_id": "CONTRACT-SYNTHETIC",
            "tipo_archivo": "TEXTO",
            "documento_texto": text,
        },
    )
    assert response.status_code in (200, 207)
    assert_response(contract, "/triage", "post", response)
    ResultadoTriaje.model_validate(response.json())


def test_http_errors_match_contract(contract, client, bearer_headers):
    unauthenticated = client.post("/api/v1/triage", json={})
    assert unauthenticated.status_code == 401
    assert_response(contract, "/triage", "post", unauthenticated)
    invalid = client.post(
        "/api/v1/triage", json={"tipo_archivo": "INVALID"}, headers=bearer_headers
    )
    assert invalid.status_code == 422
    assert_response(contract, "/triage", "post", invalid)
    missing = client.get("/api/v1/documents/CONTRACT-MISSING", headers=bearer_headers)
    assert missing.status_code == 404
    assert_response(contract, "/documents/{documento_id}", "get", missing)


def test_health_and_empty_document_list_match_contract(contract, client, bearer_headers):
    with patch("app.api.v1.health.get_db_pool", new=AsyncMock(return_value=None)):
        health = client.get("/api/v1/health")
    assert health.status_code == 503
    assert_response(contract, "/health", "get", health)
    documents = client.get("/api/v1/documents", headers=bearer_headers)
    assert documents.status_code == 200
    assert_response(contract, "/documents", "get", documents)


def test_request_nullable_and_required_fields_agree_with_schema(contract):
    schema = {"$ref": "#/components/schemas/DocumentoClinico", "components": contract["components"]}
    validator = Draft202012Validator(schema)
    payload = {"documento_id": "X", "tipo_archivo": "PDF", "documento_texto": None}
    validator.validate(payload)
    DocumentoClinico.model_validate(payload)
    for invalid in [{"tipo_archivo": "PDF"}, payload | {"canal_origen": None}]:
        assert not validator.is_valid(invalid)


@pytest.mark.parametrize("nested", [False, True], ids=["postgres", "json-historico"])
@pytest.mark.parametrize(
    "stored_type, expected_type",
    [
        ("Analítica de Laboratorio", "Informe de Laboratorio"),
        ("Informe de Estudio por Imagenes", "Informe de Estudio por Imágenes"),
        ("Receta Médica", "Receta Médica"),
        ("FACTURA", "Otro"),
        (None, "Documento Clínico"),
        ("Desconocido", "Desconocido"),
        ("Error", "Error"),
        ("Documento Clínico", "Documento Clínico"),
    ],
)
def test_stored_documents_match_contract(
    contract, client, bearer_headers, nested, stored_type, expected_type
):
    """Consulta lista y detalle sin escribir en PostgreSQL ni alterar el registro original."""
    row = {"documento_id": "CONTRACT-HISTORY", "status": "procesado"}
    if nested:
        row.update(
            clasificacion={
                "tipo_documento": stored_type,
                "nivel_prioridad": "Rutina",
                "score_confianza_clasificacion": 0.92,
            },
            datos_extraidos={},
            decision_enrutamiento={
                "destino_principal": "Cola_Rutina",
                "requiere_auditoria_humana": False,
                "justificacion_enrutamiento": "Documento histórico de prueba.",
            },
        )
    else:
        row.update(tipo_documento=stored_type, score_confianza=0.92)
    original = deepcopy(row)
    with (
        patch(
            "app.api.v1.documents.PostgresStorageRepository.listar",
            new=AsyncMock(return_value=[row]),
        ),
        patch(
            "app.api.v1.documents.PostgresStorageRepository.obtener_por_id",
            new=AsyncMock(return_value=row),
        ),
    ):
        listing = client.get("/api/v1/documents", headers=bearer_headers)
        detail = client.get("/api/v1/documents/CONTRACT-HISTORY", headers=bearer_headers)
    assert listing.status_code == detail.status_code == 200
    assert_response(contract, "/documents", "get", listing)
    assert_response(contract, "/documents/{documento_id}", "get", detail)
    assert listing.json()["total"] == 1
    for document in [listing.json()["items"][0], detail.json()]:
        ResultadoTriaje.model_validate(document)
        assert document["clasificacion"]["tipo_documento"] == expected_type
    assert row == original


@pytest.fixture(scope="module")
def metrics_design():
    path = Path(__file__).resolve().parents[2] / "specs/006-api04-metricas-triaje/contracts/metrics.openapi.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def metrics_generated_model():
    # Import here: absence of the new model must not prevent existing test collection.
    return importlib.import_module("app._generated.models").MetricsResponse


def test_metrics_contract_matches_approved_design(contract, metrics_design):
    schemas = contract["components"]["schemas"]
    for name in ("MetricsResponse", "DistribucionPrioridadMetrics"):
        assert schemas[name] == metrics_design["components"]["schemas"][name]
    operation = contract["paths"]["/metrics"]["get"]
    assert operation["operationId"] == "obtenerMetricasTriaje"
    assert operation["security"] == [{"BearerAuth": []}]
    assert set(operation["responses"]) == {"200", "401", "503"}
    assert operation["responses"]["200"]["content"]["application/json"]["examples"] == (
        metrics_design["paths"]["/metrics"]["get"]["responses"]["200"]["content"]["application/json"]["examples"]
    )


@pytest.mark.parametrize("name", ["normal", "cero", "vacio", "sinTiempos"])
def test_metrics_examples_schema_and_generated_model(contract, metrics_design, name):
    payload = metrics_design["paths"]["/metrics"]["get"]["responses"]["200"]["content"]["application/json"]["examples"][name]["value"]
    validator = Draft202012Validator({"$ref": "#/components/schemas/MetricsResponse", "components": contract["components"]})
    validator.validate(payload)
    model = metrics_generated_model()
    assert json.loads(model.model_validate(payload).model_dump_json()) == payload
    assert all(field.is_required() for field in model.model_fields.values())
    colors = payload["distribucion_prioridad"]
    assert set(colors) == {"Rojo", "Amarillo", "Verde"}
    assert all(type(value) is int and value >= 0 for value in colors.values())


@pytest.mark.parametrize("change", ["missing-rate", "missing-time", "missing-color", "extra", "extra-color", "negative-color", "fraction-color", "negative-time", "negative-rate", "over-rate"])
def test_metrics_closed_required_bounded_models(contract, change):
    payload = {"distribucion_prioridad": {"Rojo": 0, "Amarillo": 0, "Verde": 1}, "tasa_hitl": 0, "tiempo_promedio_ia_segundos": 0}
    if change == "missing-rate":
        del payload["tasa_hitl"]
    elif change == "missing-time":
        del payload["tiempo_promedio_ia_segundos"]
    elif change == "missing-color":
        del payload["distribucion_prioridad"]["Rojo"]
    elif change == "extra":
        payload["total"] = 1
    elif change == "extra-color":
        payload["distribucion_prioridad"]["Azul"] = 1
    elif change == "negative-color":
        payload["distribucion_prioridad"]["Rojo"] = -1
    elif change == "fraction-color":
        payload["distribucion_prioridad"]["Rojo"] = 0.5
    elif change == "negative-time":
        payload["tiempo_promedio_ia_segundos"] = -0.1
    elif change == "negative-rate":
        payload["tasa_hitl"] = -0.1
    elif change == "over-rate":
        payload["tasa_hitl"] = 100.01
    validator = Draft202012Validator({"$ref": "#/components/schemas/MetricsResponse", "components": contract["components"]})
    assert not validator.is_valid(payload)
    with pytest.raises(ValidationError):
        metrics_generated_model().model_validate(payload)


@pytest.mark.parametrize("payload", [
    {"distribucion_prioridad": {"Rojo": 2, "Amarillo": 3, "Verde": 5}, "tasa_hitl": 30, "tiempo_promedio_ia_segundos": 2},
    {"distribucion_prioridad": {"Rojo": 0, "Amarillo": 0, "Verde": 1}, "tasa_hitl": 0, "tiempo_promedio_ia_segundos": 0},
    {"distribucion_prioridad": {"Rojo": 0, "Amarillo": 0, "Verde": 0}, "tasa_hitl": None, "tiempo_promedio_ia_segundos": None},
    {"distribucion_prioridad": {"Rojo": 0, "Amarillo": 1, "Verde": 0}, "tasa_hitl": 0, "tiempo_promedio_ia_segundos": None},
    {"distribucion_prioridad": {"Rojo": 0, "Amarillo": 0, "Verde": 2}, "tasa_hitl": 0, "tiempo_promedio_ia_segundos": 1.667},
], ids=["normal", "cero", "vacio", "sin-tiempos", "redondeo-final"])
def test_metrics_http_json_matches_contract(contract, client, bearer_headers, monkeypatch, payload):
    module = importlib.import_module("app.repositories.metrics_repository")
    monkeypatch.setattr(module, "obtener_metricas", AsyncMock(return_value=metrics_generated_model().model_validate(payload)))
    response = client.get("/api/v1/metrics", headers=bearer_headers)
    assert response.status_code == 200
    assert_response(contract, "/metrics", "get", response)
    assert response.json() == payload
    metrics_generated_model().model_validate(response.json())


@pytest.mark.parametrize("kind", ["unauthorized", "auth-unavailable", "calculation-unavailable"])
def test_metrics_http_errors_match_contract(contract, client, bearer_headers, monkeypatch, kind):
    from app.repositories.postgres_storage import DatabaseUnavailableError
    reader = AsyncMock(side_effect=DatabaseUnavailableError("sandbox unavailable"))
    monkeypatch.setattr(importlib.import_module("app.repositories.metrics_repository"), "obtener_metricas", reader)
    if kind == "auth-unavailable":
        monkeypatch.setattr("app.core.security.get_active_session_user", AsyncMock(side_effect=RuntimeError("sandbox unavailable")))
    response = client.get("/api/v1/metrics", headers={} if kind == "unauthorized" else bearer_headers)
    assert response.status_code == (401 if kind == "unauthorized" else 503)
    assert_response(contract, "/metrics", "get", response)
    if kind != "calculation-unavailable":
        reader.assert_not_awaited()


@pytest.mark.parametrize("prioridad", ["Urgente", None])
def test_alerta_guardia_payload_minimo_coincide_con_contrato(contract, prioridad):
    from datetime import UTC, datetime
    from uuid import uuid4

    from app._generated.models import AlertaGuardia
    from app.core.alerts import MENSAJE_GUARDIA

    alerta = AlertaGuardia(
        id=uuid4(), documento_id="DOC-SINTETICO", episodio_id=None,
        prioridad=prioridad, fecha=datetime.now(UTC), mensaje=MENSAJE_GUARDIA,
    )
    validator = Draft202012Validator({
        "$ref": "#/components/schemas/AlertaGuardia", "components": contract["components"],
    })
    payload = alerta.model_dump(mode="json")
    validator.validate(payload)
    assert not validator.is_valid({**payload, "diagnostico": "dato privado"})
    with pytest.raises(ValidationError):
        AlertaGuardia.model_validate({**payload, "diagnostico": "dato privado"})


def test_stream_declarado_en_openapi_runtime(client):
    operation = client.get("/openapi.json").json()["paths"]["/api/v1/alerts/stream"]["get"]
    assert "text/event-stream" in operation["responses"]["200"]["content"]
