"""Comparación de JSON reales del API con el contrato, con persistencia simulada."""

import json
import sys
from copy import deepcopy
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from jsonschema import Draft202012Validator

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
