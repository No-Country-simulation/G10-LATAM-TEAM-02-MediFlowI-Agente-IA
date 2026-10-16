"""IA-08: HTTP, SSE y PostgreSQL reales en un contenedor desechable propio.

Activación explícita mediante IA08_TEST_DATABASE_URL e IA08_SANDBOX_REGISTRATION.
El LLM sigue siendo determinista; no se simulan sesiones, repositorios ni SSE.
"""

import asyncio
import json
import os
import secrets
import subprocess
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from time import monotonic
from urllib.parse import urlsplit
from uuid import UUID, uuid4

import asyncpg
import bcrypt
import httpx
import pytest


def validate_sandbox(url: str, registration: dict) -> str:
    """Exige un destino local explícitamente registrado, distinto de desarrollo."""
    parsed = urlsplit(url)
    if not (
        registration.get("owned") is True
        and registration.get("purpose") == "ia08-check"
        and registration.get("name", "").startswith("mediflow-ia08-check-")
        and parsed.scheme == "postgresql"
        and parsed.hostname == "127.0.0.1"
        and parsed.port == registration.get("port")
        and parsed.port is not None
        and 1024 <= parsed.port <= 65535
        and parsed.port != 5432
        and parsed.username == "ia08_test"
        and bool(parsed.password)
        and parsed.path == "/mediflow_ia08_test"
        and not parsed.query
        and not parsed.fragment
    ):
        raise ValueError("IA-08 exige PostgreSQL desechable propio; mediflow_dev no está permitido")
    return url


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://ia08_test:x@127.0.0.1:32155/mediflow_dev",
        "postgresql://ia08_test:x@127.0.0.1:5432/mediflow_ia08_test",
        "postgresql://ia08_test:x@remote:32155/mediflow_ia08_test",
        "postgresql://ia08_test:x@127.0.0.1:32155/mediflow_ia08_test?host=remote",
    ],
)
def test_rechaza_destinos_ajenos_al_sandbox(url):
    with pytest.raises(ValueError):
        validate_sandbox(
            url,
            {
                "owned": True,
                "purpose": "ia08-check",
                "name": "mediflow-ia08-check-test",
                "port": 32155,
            },
        )


def isolated_env(url: str, backend: Path) -> dict[str, str]:
    env = {
        key: value
        for key, value in os.environ.items()
        if key.upper()
        in {
            "SYSTEMROOT",
            "WINDIR",
            "PATH",
            "TEMP",
            "TMP",
            "USERPROFILE",
            "APPDATA",
            "LOCALAPPDATA",
            "COMSPEC",
            "PATHEXT",
            "PYTHONUTF8",
        }
    }
    env.update(
        DATABASE_URL=url,
        PYTHONPATH=str(backend),
        ALLOW_MOCK_LLM="true",
        GOOGLE_API_KEY="your-test-placeholder",
        OPENAI_API_KEY="your-test-placeholder",
        LANGSMITH_TRACING="false",
        LANGCHAIN_TRACING_V2="false",
        PYTHONIOENCODING="utf-8",
    )
    return env


@pytest.fixture
async def sandbox(tmp_path, unused_tcp_port):
    url = os.environ.get("IA08_TEST_DATABASE_URL")
    registration_path = os.environ.get("IA08_SANDBOX_REGISTRATION")
    if not url or not registration_path:
        pytest.skip("IA-08 PostgreSQL requiere contenedor propio y activación explícita")
    validate_sandbox(url, json.loads(Path(registration_path).read_text(encoding="utf-8-sig")))
    backend = Path(__file__).resolve().parents[1]
    env = isolated_env(url, backend)
    conn = await asyncpg.connect(url)
    try:
        identity = await conn.fetchrow("SELECT current_database() AS db, current_user AS usr")
        assert dict(identity) == {"db": "mediflow_ia08_test", "usr": "ia08_test"}
        assert 170000 <= int(await conn.fetchval("SHOW server_version_num")) < 180000
        migration = await asyncio.to_thread(
            subprocess.run,
            [
                sys.executable,
                "-m",
                "alembic",
                "-c",
                str(backend / "alembic.ini"),
                "upgrade",
                "head",
            ],
            cwd=tmp_path,
            env=env,
            capture_output=True,
            timeout=60,
        )
        assert migration.returncode == 0, migration.stderr.decode(errors="replace")
        assert await conn.fetchval("SELECT version_num FROM alembic_version")
        password = secrets.token_urlsafe(24)
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        roles = ("MEDICO", "COORDINADOR", "ADMINISTRADOR", "OPERADOR", "AUDITOR")
        identities = {}
        document_base = 70000000 + secrets.randbelow(10000000)
        for index, role in enumerate(roles):
            uid, document = uuid4(), str(document_base + index)
            await conn.execute(
                """INSERT INTO usuarios
                (id, documento_identidad, password_hash, salt, nombres, apellidos, rol, estado,
                 especialidad_medica)
                VALUES ($1,$2,$3,'','IA08','Sintético',$4,'ACTIVO','Medicina General')""",
                uid,
                document,
                password_hash,
                role,
            )
            identities[role] = document
        launch = (
            "import sys; from pathlib import Path; "
            "from app.repositories import oci_storage; "
            "oci_storage.LOCAL_STORAGE_DIR=Path(sys.argv[1]); "
            "import uvicorn; uvicorn.run('app.main:app',host='127.0.0.1',"
            "port=int(sys.argv[2]),workers=1,access_log=False)"
        )
        with (tmp_path / "api.log").open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                [sys.executable, "-c", launch, str(tmp_path / "storage"), str(unused_tcp_port)],
                cwd=tmp_path,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=log,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            try:
                async with httpx.AsyncClient(
                    base_url=f"http://127.0.0.1:{unused_tcp_port}",
                    timeout=10,
                ) as client:
                    deadline = monotonic() + 30
                    while True:
                        assert process.poll() is None, "API de prueba terminó durante el inicio"
                        try:
                            if (await client.get("/api/v1/health")).status_code == 200:
                                break
                        except httpx.TransportError:
                            pass
                        assert monotonic() < deadline, "API de prueba no inició"
                        await asyncio.sleep(0.1)
                    headers = {}
                    for role, document in identities.items():
                        response = await client.post(
                            "/api/v1/auth/login",
                            json={
                                "documento_identidad": document,
                                "password": password,
                            },
                        )
                        assert response.status_code == 200, "Login sintético falló"
                        headers[role] = {
                            "Authorization": f"Bearer {response.json()['access_token']}"
                        }
                    yield conn, client, headers, url
            finally:
                process.terminate()
                try:
                    await asyncio.to_thread(process.wait, 10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    await asyncio.to_thread(process.wait, 10)
    finally:
        await conn.close()


async def next_alert(lines):
    event = {}
    async for line in lines:
        if not line:
            if "data" in event:
                return event
            continue
        if not line.startswith(":"):
            key, value = line.split(":", 1)
            event[key] = value.strip()
    raise AssertionError("La conexión terminó antes de recibir la alerta")


@pytest.mark.repository_mock
@pytest.mark.postgres_integration
async def test_alerta_guardia_http_sse_y_commit_reales(sandbox):
    conn, client, headers, url = sandbox
    path = "/api/v1/alerts/stream"
    assert (await client.get(path)).status_code == 401
    for role in ("OPERADOR", "AUDITOR"):
        assert (await client.get(path, headers=headers[role])).status_code == 403
    configuration = await conn.fetch("SELECT * FROM configuracion_sistema ORDER BY clave")
    assert (
        await conn.fetchval(
            "SELECT valor FROM configuracion_sistema WHERE clave='modo_almacenamiento'"
        )
        == "LOCAL"
    )
    patient_id, episode_id = uuid4(), uuid4()
    patient_document = str(80000000 + secrets.randbelow(10000000))
    patient_history = f"HC-IA08-{uuid4().hex[:12].upper()}"
    await conn.execute(
        """INSERT INTO pacientes (id,numero_documento,historia_clinica,nombres,apellidos)
        VALUES ($1,$2,$3,'Paciente','Sintético')""",
        patient_id,
        patient_document,
        patient_history,
    )
    await conn.execute(
        """INSERT INTO episodios_clinicos (id,codigo_episodio,paciente_id)
        VALUES ($1,$2,$3)""",
        episode_id,
        f"IA08-{uuid4().hex[:12]}",
        patient_id,
    )
    async with AsyncExitStack() as stack:
        readers = []
        for role in ("MEDICO", "COORDINADOR", "ADMINISTRADOR"):
            response = await stack.enter_async_context(
                client.stream("GET", path, headers=headers[role])
            )
            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            lines = response.aiter_lines()
            assert await anext(lines) == ": connected"
            assert await anext(lines) == ""
            readers.append(lines)
        doc_id = f"IA08-URGENTE-{uuid4().hex[:12]}"
        response = await client.post(
            "/api/v1/triage",
            headers=headers["OPERADOR"],
            json={
                "documento_id": doc_id,
                "tipo_archivo": "TEXTO",
                "documento_texto": f"DNI: {patient_document}. HC: {patient_history}. TEP agudo. Correlación urgente.",
            },
        )
        assert response.status_code == 200, response.text
        assert (
            response.json()["decision_enrutamiento"]["destino_principal"]
            == "Cola_Emergencia_Medica"
        )
        events = [await asyncio.wait_for(next_alert(lines), 5) for lines in readers]
        assert events[0] == events[1] == events[2]
        payload = json.loads(events[0]["data"])
        assert events[0]["event"] == "ALERTA_GUARDIA_EMITIDA"
        assert events[0]["id"] == payload["id"]
        assert set(payload) == {
            "id",
            "documento_id",
            "episodio_id",
            "prioridad",
            "fecha",
            "mensaje",
        }
        assert payload["documento_id"] == doc_id
        assert payload["episodio_id"] == str(episode_id)
        assert payload["prioridad"] == "Urgente"
        assert patient_document not in events[0]["data"]
        assert "Tromboembolismo" not in events[0]["data"]
        # Otra conexión demuestra visibilidad tras COMMIT, no solo en la sesión escritora.
        observer = await asyncpg.connect(url)
        try:
            row = await observer.fetchrow(
                """SELECT te.*, dt.documento_id AS codigo_documento
                FROM trazabilidad_eventos te JOIN documentos_triaje dt ON dt.id=te.documento_id
                WHERE te.id=$1""",
                UUID(payload["id"]),
            )
            assert row["evento"] == "ALERTA_GUARDIA_EMITIDA"
            assert row["codigo_documento"] == doc_id
            assert row["episodio_id"] == episode_id
            assert json.loads(row["metadata"])["mensaje"] == payload["mensaje"]
            assert row["created_at"].isoformat().replace("+00:00", "Z") == payload["fecha"]
        finally:
            await observer.close()

        # Un fallo real de INSERT debe devolver 503 y no emitir ningún evento SSE.
        await conn.execute("""CREATE FUNCTION ia08_reject_alert() RETURNS trigger AS $$
            BEGIN
                IF NEW.evento = 'ALERTA_GUARDIA_EMITIDA' THEN
                    RAISE EXCEPTION 'Fallo intencional de persistencia IA08';
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER ia08_reject_alert BEFORE INSERT ON trazabilidad_eventos
                FOR EACH ROW EXECUTE FUNCTION ia08_reject_alert();""")
        try:
            failed_id = f"IA08-FALLO-{uuid4().hex[:12]}"
            failed = await client.post(
                "/api/v1/triage",
                headers=headers["OPERADOR"],
                json={
                    "documento_id": failed_id,
                    "tipo_archivo": "TEXTO",
                    "documento_texto": "TEP agudo. Correlación urgente.",
                },
            )
            assert failed.status_code == 503
            assert (
                await conn.fetchval(
                    "SELECT count(*) FROM documentos_triaje WHERE documento_id=$1",
                    failed_id,
                )
                == 1
            )
            assert (
                await conn.fetchval(
                    """SELECT count(*) FROM trazabilidad_eventos te JOIN documentos_triaje dt
                ON dt.id=te.documento_id WHERE dt.documento_id=$1
                AND te.evento='ALERTA_GUARDIA_EMITIDA'""",
                    failed_id,
                )
                == 0
            )
            with pytest.raises(TimeoutError):
                await asyncio.wait_for(next_alert(readers[0]), 0.5)
        finally:
            await conn.execute(
                "DROP TRIGGER ia08_reject_alert ON trazabilidad_eventos; DROP FUNCTION ia08_reject_alert()"
            )
    assert await conn.fetch("SELECT * FROM configuracion_sistema ORDER BY clave") == configuration
