"""Contract testing automatizado con Schemathesis + pruebas de borde (US-14).

Dos niveles de verificación del contrato ``specs/openapi.yaml``:

1. **Schemathesis (property-based)** — genera peticiones a partir del **contrato
   SDD** (``specs/openapi.yaml``, la fuente de verdad) y comprueba que cada
   respuesta sea conforme (sin errores de servidor, códigos y content-types
   declarados, payload válido contra el schema). El contract testing necesita la
   API con su base de datos real, por lo que se ejecuta contra un servidor vivo:
   se activa cuando se define ``CONTRACT_BASE_URL`` (p. ej.
   ``http://localhost:8000/api/v1`` con ``make dev-docker`` levantado). Si la
   variable no está definida, la prueba se omite — el mismo patrón de *gating* que
   usan las pruebas de integración PostgreSQL del repositorio.

2. **Pruebas de borde (in-process)** — payloads malformados y límites de tamaño,
   rechazados por FastAPI/Pydantic antes de tocar la base de datos. Son
   deterministas y se ejecutan siempre con ``TestClient`` y los mocks de
   ``conftest.py``.
"""

import os
from pathlib import Path

import pytest
import schemathesis
from hypothesis import HealthCheck, settings

# ─────────────────────────── 1. Schemathesis (servidor vivo) ───────────────────────────

# El esquema se carga desde el **contrato SDD** (fuente de verdad), no desde el
# /openapi.json que autogenera FastAPI (que declara menos respuestas por operación).
SPEC_PATH = Path(__file__).resolve().parents[2] / "specs" / "openapi.yaml"

CONTRACT_BASE_URL = os.getenv("CONTRACT_BASE_URL")

if CONTRACT_BASE_URL:
    _schema = schemathesis.openapi.from_path(str(SPEC_PATH))
    # Operaciones no aptas para fuzzing automático:
    #  - /alerts/stream: Server-Sent Events (streaming, no request/response).
    #  - /triage/upload: subida multipart de archivos binarios.
    #  - /documents/{id}/file: descarga binaria (no JSON).
    _schema = _schema.exclude(path_regex=r"stream|upload|/file$")

    _token = os.getenv("CONTRACT_BEARER")
    _AUTH_HEADERS = {"Authorization": f"Bearer {_token}"} if _token else {}

    @_schema.parametrize()
    @settings(
        max_examples=20,
        deadline=None,
        derandomize=True,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_api_cumple_contrato_openapi(case):
        """Cada operación del contrato SDD responde de forma conforme."""
        case.call_and_validate(base_url=CONTRACT_BASE_URL, headers=_AUTH_HEADERS)

else:

    @pytest.mark.skip(
        reason="Contract testing con Schemathesis: define CONTRACT_BASE_URL "
        "(p. ej. http://localhost:8000/api/v1) con la API corriendo. "
        "Opcional: CONTRACT_BEARER=<token> para autenticar."
    )
    def test_api_cumple_contrato_openapi():
        ...


# ─────────────────────────── 2. Pruebas de borde (in-process) ───────────────────────────

TRIAGE = "/api/v1/triage"


def test_triage_sin_autenticacion_devuelve_401(client):
    """Sin token, el endpoint protegido responde 401 (documentado en el contrato)."""
    response = client.post(
        TRIAGE,
        json={"documento_id": "EDGE-001", "tipo_archivo": "TEXTO", "documento_texto": "t"},
    )
    assert response.status_code == 401


def test_triage_tipo_archivo_invalido_devuelve_422(client, bearer_headers):
    """Valor fuera del enum de tipo_archivo → 422 de validación."""
    response = client.post(
        TRIAGE,
        headers=bearer_headers,
        json={"documento_id": "EDGE-002", "tipo_archivo": "FORMATO_INEXISTENTE", "documento_texto": "t"},
    )
    assert response.status_code == 422


def test_triage_campos_requeridos_faltantes_devuelve_422(client, bearer_headers):
    """Cuerpo vacío sin los campos requeridos → 422."""
    assert client.post(TRIAGE, headers=bearer_headers, json={}).status_code == 422


def test_triage_tipos_incorrectos_devuelve_422(client, bearer_headers):
    """Tipos de dato incorrectos en cada campo → 422."""
    response = client.post(
        TRIAGE,
        headers=bearer_headers,
        json={"documento_id": 123, "tipo_archivo": ["TEXTO"], "documento_texto": {"x": 1}},
    )
    assert response.status_code == 422


def test_triage_json_sintacticamente_invalido_devuelve_422(client, bearer_headers):
    """JSON malformado (no parseable) → 422, sin romper el servidor."""
    response = client.post(TRIAGE, headers=bearer_headers, content="{ esto no es json ")
    assert response.status_code == 422


def test_triage_texto_sobredimensionado_no_genera_error_de_servidor(client, bearer_headers):
    """Límite de tamaño: un documento enorme se maneja o se rechaza, nunca 5xx."""
    response = client.post(
        TRIAGE,
        headers=bearer_headers,
        json={"documento_id": "EDGE-BIG", "tipo_archivo": "TEXTO", "documento_texto": "A" * 2_000_000},
    )
    assert response.status_code < 500
