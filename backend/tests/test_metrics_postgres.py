"""API-04 sandbox guards; real integration must never target development."""

import asyncio
import hashlib
import importlib
import json
import os
import re
import secrets
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from time import perf_counter, perf_counter_ns
from unittest.mock import AsyncMock
from urllib.parse import urlsplit
from uuid import uuid4

import asyncpg
import bcrypt
import httpx
import pytest


def _validate_metrics_registration(registration):
    """Require an explicit ownership record for a dedicated, local resource."""
    if not isinstance(registration, dict):
        raise ValueError("sandbox propio no registrado")
    user = registration.get("user")
    port = registration.get("port")
    if (
        registration.get("owned") is not True
        or registration.get("host") != "127.0.0.1"
        or registration.get("database") != "mediflow_api04_test"
        or registration.get("schema") != "public"
        or not isinstance(user, str)
        or not re.fullmatch(r"api04_[a-z0-9_]+", user)
        or user == "api04_bootstrap"
        or type(port) is not int
        or not 1024 <= port <= 65535
        or port == 5432
    ):
        raise ValueError("sandbox propio no autorizado")


def validate_metrics_test_url(url, registration):
    _validate_metrics_registration(registration)
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme == "postgresql"
            and parsed.hostname == registration["host"]
            and parsed.port == registration["port"]
            and parsed.username == registration["user"]
            and bool(parsed.password)
            and parsed.path == "/mediflow_api04_test"
            and not parsed.query
            and not parsed.fragment
        )
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise ValueError("URL de sandbox no autorizada")
    return url


async def guard_metrics_test_connection(conn, registration):
    """Read actual identity/version before permitting any DDL or DML."""
    _validate_metrics_registration(registration)
    row = await conn.fetchrow(
        """SELECT current_database() AS db, current_user AS usr,
        current_schema() AS schema, current_setting('search_path') AS path,
        host(inet_server_addr()) AS address, inet_server_port() AS port,
        current_setting('server_version_num')::integer AS version,
        (SELECT rolsuper FROM pg_roles WHERE rolname = current_user) AS superuser"""
    )
    if (
        row is None
        or row["db"] != registration["database"]
        or row["usr"] != registration["user"]
        or row["schema"] != registration["schema"]
        or row["path"] not in ('"$user", public', "public")
        or row["address"] != registration["host"]
        or row["port"] != registration["port"]
        or not 170000 <= row["version"] < 180000
        or row["superuser"] is not False
    ):
        raise ValueError("Conexión efectiva de sandbox no autorizada")


def metrics_sandbox_url(registration):
    url = os.environ.get("API04_TEST_DATABASE_URL", "")
    if not url:
        if os.environ.get("API04_REQUIRE_POSTGRES") == "1":
            raise ValueError("sandbox PostgreSQL API-04 requerido y ausente")
        pytest.skip("PostgreSQL API-04 no solicitado; no acredita integración")
    return validate_metrics_test_url(url, registration)


def _registered_metrics_sandbox():
    evidence = os.environ.get("API04_EVIDENCE_DIR", "")
    if not evidence:
        return None
    path = Path(evidence) / "sandbox" / "ownership.json"
    if not path.is_file():
        return None
    try:
        registration = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("Registro de sandbox inválido") from exc
    _validate_metrics_registration(registration)
    return registration


@pytest.fixture
async def metrics_pg():
    """T003: bootstrap only an owned, effectively validated API-04 sandbox."""
    registration = _registered_metrics_sandbox()
    url = metrics_sandbox_url(registration)
    conn = await asyncpg.connect(url, timeout=10)
    try:
        await guard_metrics_test_connection(conn, registration)
        if await conn.fetchval("SELECT to_regclass('public.alembic_version')") is None:
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
                cwd=Path(__file__).resolve().parents[1],
                env=dict(os.environ, DATABASE_URL=url, PYTHONIOENCODING="utf-8"),
                capture_output=True, text=True, encoding="utf-8", timeout=60,
            )
            if result.returncode or not result.stdout.startswith("BEGIN;"):
                pytest.fail("Alembic offline de sandbox falló; salida sensible omitida")
            await guard_metrics_test_connection(conn, registration)
            await conn.execute(result.stdout)
        await guard_metrics_test_connection(conn, registration)
        head = await conn.fetchval("SELECT version_num FROM alembic_version")
        if head != "p9q909633lm5":
            pytest.fail("Head físico del sandbox no coincide con el esquema aprobado")
        sources = (
            "documentos_triaje", "auditorias_hitl", "auditorias_coordinacion", "historial_documento",
        )
        counts = {table: await conn.fetchval(f"SELECT count(*) FROM {table}") for table in sources}
        columns = await conn.fetch(
            """SELECT table_name, column_name, data_type FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = ANY($1::text[])
            ORDER BY table_name, ordinal_position""", list(sources),
        )
        constraints = await conn.fetch(
            """SELECT table_name, constraint_name, constraint_type
            FROM information_schema.table_constraints
            WHERE table_schema = 'public' AND table_name = ANY($1::text[])
            ORDER BY table_name, constraint_name""", list(sources),
        )
        indexes = await conn.fetch(
            """SELECT tablename, indexname, indexdef FROM pg_indexes
            WHERE schemaname = 'public' AND tablename = ANY($1::text[])
            ORDER BY tablename, indexname""", list(sources),
        )
        evidence = Path(os.environ["API04_EVIDENCE_DIR"]) / "sandbox"
        record = {
            "head": head, "sources_readable": counts,
            "connection": {key: registration[key] for key in ("host", "port", "database", "user", "schema")},
            "server_version_num": await conn.fetchval("SHOW server_version_num"),
            "columns": [dict(row) for row in columns],
            "constraints": [dict(row) for row in constraints],
            "indexes": [dict(row) for row in indexes],
            "foreign_keys": [dict(row) for row in await conn.fetch(
                """SELECT conname, pg_get_constraintdef(oid) AS definition
                FROM pg_constraint WHERE contype = 'f' AND connamespace = 'public'::regnamespace
                ORDER BY conname"""
            )],
            "permissions": {table: await conn.fetchval(
                "SELECT has_table_privilege(current_user, $1, 'SELECT,INSERT,UPDATE,DELETE')", table
            ) for table in sources},
            "schema_digest": hashlib.sha256(json.dumps([dict(row) for row in columns], sort_keys=True).encode()).hexdigest(),
        }
        (evidence / "schema.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        yield conn
    finally:
        await conn.close()


@pytest.fixture
async def metrics_http(metrics_pg, unused_tcp_port):
    """Own one real API process and ephemeral fixture accounts; no session mocks."""
    registration = _registered_metrics_sandbox()
    url = metrics_sandbox_url(registration)
    await guard_metrics_test_connection(metrics_pg, registration)
    # Existing migrations contain three example documents. Remove only in our disposable base.
    await metrics_pg.execute("TRUNCATE documentos_triaje CASCADE")
    password = secrets.token_urlsafe(24)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt).decode()
    roles = ("ADMINISTRADOR", "COORDINADOR", "SUPERVISOR", "AUDITOR", "OPERADOR")
    identities = {role: (uuid4(), f"{91000000 + index:08d}") for index, role in enumerate(roles)}
    for role, (uid, document) in identities.items():
        await metrics_pg.execute(
            """INSERT INTO usuarios (id, documento_identidad, password_hash, salt,
            nombres, apellidos, rol, estado) VALUES ($1,$2,$3,$4,'API04','Sintético',$5,'ACTIVO')""",
            uid, document, hashed, salt.decode(), role,
        )
    # Explicit whitelist: do not inherit any developer credential or real .env setting.
    env = {key: value for key, value in os.environ.items() if key.upper() in {
        "SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "USERPROFILE", "APPDATA",
        "LOCALAPPDATA", "COMSPEC", "PATHEXT", "PYTHONIOENCODING", "PYTHONUTF8",
    }}
    env.update(DATABASE_URL=url, ALLOW_MOCK_LLM="true", GOOGLE_API_KEY="your-test-placeholder",
               OPENAI_API_KEY="your-test-placeholder", LANGSMITH_TRACING="false",
               PYTHONPATH=str(Path(__file__).resolve().parents[1]))
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
         "--port", str(unused_tcp_port), "--workers", "1", "--no-access-log"],
        cwd=Path(os.environ["API04_EVIDENCE_DIR"]), env=env,
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{unused_tcp_port}", timeout=5) as client:
            deadline = perf_counter() + 40
            while True:
                if process.poll() is not None:
                    pytest.fail("API sandbox terminó durante inicio; logs sensibles no persistidos")
                try:
                    if (await client.get("/api/v1/health")).status_code == 200:
                        break
                except httpx.TransportError:
                    pass
                if perf_counter() >= deadline:
                    pytest.fail("API sandbox no inició en 40 segundos")
                await asyncio.sleep(0.1)
            tokens = {}
            for role, (_, document) in identities.items():
                response = await client.post("/api/v1/auth/login", json={
                    "documento_identidad": document, "password": password,
                })
                if response.status_code != 200:
                    pytest.fail("Login sintético falló; credenciales/cuerpo omitidos")
                tokens[role] = response.json()["access_token"]
            yield client, tokens
    finally:
        process.terminate()
        try:
            await asyncio.to_thread(process.wait, 10)
        except subprocess.TimeoutExpired:
            process.kill()
            await asyncio.to_thread(process.wait, 10)
        await guard_metrics_test_connection(metrics_pg, registration)
        ids = [uid for uid, _ in identities.values()]
        await metrics_pg.execute("DELETE FROM sesiones_usuario WHERE usuario_id = ANY($1::uuid[])", ids)
        await metrics_pg.execute("DELETE FROM usuarios WHERE id = ANY($1::uuid[])", ids)


@pytest.fixture
def sandbox_registration():
    """Synthetic ownership record for guard tests, not a live sandbox claim."""
    return {
        "owned": True,
        "host": "127.0.0.1",
        "port": 55434,
        "database": "mediflow_api04_test",
        "user": "api04_test",
        "schema": "public",
    }


@pytest.mark.parametrize(
    "url",
    [
        "", "not-a-url",
        "postgresql://api04_test:x@127.0.0.1:55434/mediflow_dev",
        "postgresql://postgres:x@127.0.0.1:55434/mediflow_api04_test",
        "postgresql://api04_test:x@remote:55434/mediflow_api04_test",
        "postgresql://api04_test:x@127.0.0.1:5432/mediflow_api04_test",
        "postgresql://api04_test:x@127.0.0.1:55435/mediflow_api04_test",
        "postgresql://api04_test:x@127.0.0.1:55434/other",
        "postgresql://api04_test:x@127.0.0.1:55434/mediflow_api04_test?host=remote",
        "postgresql://api04_test:x@127.0.0.1:55434/mediflow_api04_test#override",
        "postgresql://api04_test@127.0.0.1:55434/mediflow_api04_test",
    ],
)
def test_metrics_guard_rejects_unsafe_urls(url, sandbox_registration):
    with pytest.raises(ValueError):
        validate_metrics_test_url(url, sandbox_registration)


def test_metrics_guard_accepts_only_registered_owned_target(sandbox_registration):
    url = "postgresql://api04_test:x@127.0.0.1:55434/mediflow_api04_test"
    assert validate_metrics_test_url(url, sandbox_registration) == url
    for ownership in (None, {}, dict(sandbox_registration, owned=False)):
        with pytest.raises(ValueError):
            validate_metrics_test_url(url, ownership)


@pytest.mark.parametrize(
    "field,value",
    [
        ("db", "mediflow_dev"), ("usr", "postgres"), ("schema", "other"),
        ("path", "other, public"), ("address", "192.168.1.2"), ("port", 5432),
        ("port", 55435), ("version", 160009), ("version", 180001),
        ("superuser", True),
    ],
)
async def test_metrics_guard_rejects_unsafe_effective_connection(
    field, value, sandbox_registration,
):
    row = dict(db="mediflow_api04_test", usr="api04_test", schema="public",
               path='"$user", public', address="127.0.0.1", port=55434,
               version=170006, superuser=False)
    row[field] = value
    conn = AsyncMock()
    conn.fetchrow.return_value = row
    with pytest.raises(ValueError):
        await guard_metrics_test_connection(conn, sandbox_registration)
    conn.execute.assert_not_called()


async def test_metrics_guard_validates_effective_identity_before_writes(sandbox_registration):
    conn = AsyncMock()
    conn.fetchrow.return_value = dict(
        db="mediflow_api04_test", usr="api04_test", schema="public",
        path="public", address="127.0.0.1", port=55434,
        version=170006, superuser=False,
    )
    await guard_metrics_test_connection(conn, sandbox_registration)
    conn.fetchrow.assert_awaited_once()
    conn.execute.assert_not_called()


def test_metrics_missing_required_sandbox_fails_without_skipping(monkeypatch):
    monkeypatch.delenv("API04_TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("API04_REQUIRE_POSTGRES", "1")
    with pytest.raises(ValueError, match="sandbox"):
        metrics_sandbox_url(None)


async def test_metrics_sandbox_real_head_and_sources(metrics_pg):
    """T003 requires the actual migrated head and all four readable sources."""
    assert await metrics_pg.fetchval("SELECT version_num FROM alembic_version") == "p9q909633lm5"
    for table in (
        "documentos_triaje", "auditorias_hitl", "auditorias_coordinacion", "historial_documento",
    ):
        assert await metrics_pg.fetchval(f"SELECT count(*) FROM {table}") >= 0


async def test_metrics_sandbox_real_sessions_and_process(metrics_http, metrics_pg):
    client, tokens = metrics_http
    assert set(tokens) == {"ADMINISTRADOR", "COORDINADOR", "SUPERVISOR", "AUDITOR", "OPERADOR"}
    for role, token in tokens.items():
        response = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json()["rol"] == role
    assert await metrics_pg.fetchval("SELECT count(*) FROM documentos_triaje") == 0
    assert (await client.get("/api/v1/auth/me")).status_code == 401


def manifest_document(*, eligible=True, reviewed=False, **attributes):
    """Membership/review are fixture declarations, not derived from the SQL."""
    return dict(eligible=eligible, reviewed=reviewed, status="procesado", priority="Rutina",
                time=1000, finals=1, flag=False, legacy=[], coordination=[], events=[]) | attributes


def manifest_oracle(documents):
    cohort = [doc for doc in documents if doc["eligible"]]
    times = [doc["time"] for doc in cohort if doc["time"] is not None and doc["time"] >= 0]
    colors = {color: sum(doc["priority"] == priority for doc in cohort) for color, priority in (
        ("Rojo", "Urgente"), ("Amarillo", "Ambiguo"), ("Verde", "Rutina"),
    )}
    rate = (Decimal(100 * sum(doc["reviewed"] for doc in cohort)) / Decimal(len(cohort))).quantize(Decimal(".01"), rounding=ROUND_HALF_UP) if cohort else None
    time = (Decimal(sum(times)) / Decimal(len(times)) / 1000).quantize(Decimal(".001"), rounding=ROUND_HALF_UP) if times else None
    return {"distribucion_prioridad": colors, "tasa_hitl": None if rate is None else float(rate), "tiempo_promedio_ia_segundos": None if time is None else float(time)}


MATRIX = [
    ("distribution-normal", [manifest_document(priority=p) for p in ("Urgente", "Urgente", "Ambiguo", "Rutina", "Rutina", "Rutina")]),
    ("distribution-null-priority", [manifest_document(priority=None, reviewed=True, flag=True), manifest_document()]),
    ("distribution-no-final", [manifest_document(eligible=False, finals=0, flag=True), manifest_document()]),
    ("distribution-final-duplicates", [manifest_document(finals=4, events=["DOCUMENTO_RECIBIDO"] * 4)]),
    ("distribution-same-patient", [manifest_document(patient=True), manifest_document(patient=True)]),
    ("distribution-no-links", [manifest_document()]),
    ("distribution-seed-received", [manifest_document(eligible=False, status="recibido", seed=True, time=None)]),
    ("distribution-seed-processed", [manifest_document(seed=True, time=None)]),
    ("distribution-historical", [manifest_document(old=True)]),
    ("hitl-flag-alone", [manifest_document(reviewed=True, flag=True)]),
    ("hitl-ambiguous-alone-excluded", [manifest_document(priority="Ambiguo")]),
    ("hitl-unrelated-document", [manifest_document(), manifest_document(eligible=False, reviewed=True, status="recibido", legacy=["aprobar"], events=["AUDITORIA_APROBADA"], coordination=["aprobado"])]),
    ("hitl-uuid-over-discordant-external", [manifest_document(reviewed=True, legacy=["aprobar"], external_audit="API04-MATRIX-0001"), manifest_document()]),
    ("hitl-overlap-duplicates", [manifest_document(reviewed=True, flag=True, legacy=["aprobar"] * 3, coordination=["aprobado"] * 3, events=["AUDITORIA_RECHAZADA"] * 3, finals=3)]),
    ("hitl-thirty", [manifest_document(reviewed=i < 3, flag=i < 3) for i in range(10)]),
    ("hitl-third", [manifest_document(reviewed=i == 0, flag=i == 0) for i in range(3)]),
    ("hitl-tie", [manifest_document(reviewed=i == 0, flag=i == 0) for i in range(32)]),
    ("hitl-below-tie", [manifest_document(reviewed=i == 0, flag=i == 0) for i in range(33)]),
    ("hitl-above-tie", [manifest_document(reviewed=i == 0, flag=i == 0) for i in range(31)]),
    ("time-normal", [manifest_document(time=t) for t in (1000, 2000, 3000)]),
    ("time-divisor", [manifest_document(time=t) for t in (0, 1000, None, -1)]),
    ("time-tie", [manifest_document(time=t) for t in (1000, 2333)]),
    ("time-below-tie", [manifest_document(time=t) for t in (1000, 2332)]),
    ("time-above-tie", [manifest_document(time=t) for t in (1000, 2334)]),
    ("time-zero", [manifest_document(time=0), manifest_document(time=0)]),
    ("time-missing", [manifest_document(time=None), manifest_document(time=-1)]),
    ("time-equal-not-distinct", [manifest_document(time=t, finals=3) for t in (1000, 1000, 4000)]),
    ("time-persisted-synthetic", [manifest_document(time=777, seed=True)]),
    ("time-overflow-safe", [manifest_document(time=2147483647), manifest_document(time=2147483647)]),
    ("empty", []),
]
MATRIX += [(f"distribution-status-{s}", [manifest_document(eligible=s in ("procesado", "pendiente_auditoria", "rechazado"), status=s)]) for s in (
    "procesado", "pendiente_auditoria", "rechazado", "recibido", "procesando", "error", "no_soportado",
)]
MATRIX += [(f"hitl-legacy-{decision}-flag-off", [manifest_document(reviewed=True, flag=False, legacy=[decision], status="rechazado" if decision == "rechazar" else "procesado")]) for decision in ("aprobar", "reclasificar", "rechazar")]
MATRIX += [(f"hitl-event-{event}-alone", [manifest_document(reviewed=True, events=[event])]) for event in (
    "PENDIENTE_AUDITORIA", "AUDITORIA_APROBADA", "AUDITORIA_RECLASIFICADA", "AUDITORIA_RECHAZADA",
)]
MATRIX += [(f"hitl-coordination-{decision}-alone", [manifest_document(reviewed=True, coordination=[decision])]) for decision in (
    "aprobar", "aprobado", "reclasificar", "reclasificado", "rechazar", "rechazado",
)]
MATRIX += [(f"hitl-coordination-{decision}-excluded", [manifest_document(coordination=[decision])]) for decision in ("reasignado", "derivar", "APROBAR", "aprobar ")]
MATRIX += [("hitl-null-episode-only-excluded", [manifest_document(null_coordination=True)])]


@pytest.fixture
async def metrics_clean(metrics_pg):
    await guard_metrics_test_connection(metrics_pg, _registered_metrics_sandbox())
    await metrics_pg.execute("TRUNCATE documentos_triaje CASCADE")
    auditor = uuid4()
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", secrets.token_bytes(24), salt.encode(), 100000).hex()
    await metrics_pg.execute(
        """INSERT INTO usuarios (id, documento_identidad, password_hash, salt, nombres, apellidos, rol)
        VALUES ($1,'92999999',$2,$3,'API04','Auditor sintético','AUDITOR')""", auditor, password_hash, salt,
    )
    try:
        yield metrics_pg, auditor
    finally:
        await guard_metrics_test_connection(metrics_pg, _registered_metrics_sandbox())
        await metrics_pg.execute("TRUNCATE documentos_triaje CASCADE")
        await metrics_pg.execute("DELETE FROM usuarios WHERE id=$1", auditor)
        await metrics_pg.execute("DELETE FROM pacientes WHERE numero_documento='API04-PATIENT'")
        await metrics_pg.execute("DELETE FROM episodios_clinicos WHERE codigo_episodio='API04-EPISODE'")


async def load_metrics_manifest(conn, auditor, documents):
    await guard_metrics_test_connection(conn, _registered_metrics_sandbox())
    ids = []
    async with conn.transaction():
        patient = None
        if any(doc.get("patient") for doc in documents):
            patient = await conn.fetchval("""INSERT INTO pacientes (numero_documento,nombres,apellidos)
              VALUES ('API04-PATIENT','API04','Sintético') RETURNING id""")
        for index, doc in enumerate(documents):
            uid = uuid4()
            ids.append(uid)
            await conn.execute(
                """INSERT INTO documentos_triaje (id,documento_id,tipo_archivo,status,nivel_prioridad,
                requiere_auditoria_humana,tiempo_procesamiento_ms,metadata,paciente_id,created_at)
                VALUES ($1,$2,'TEXTO',$3,$4,$5,$6,$7::jsonb,$8,
                CASE WHEN $9 THEN '2000-01-01'::timestamptz ELSE now() END)""",
                uid, f"API04-MATRIX-{index:04d}", doc["status"], doc["priority"], doc["flag"], doc["time"],
                json.dumps({"seed": doc.get("seed", False)}), patient if doc.get("patient") else None, doc.get("old", False),
            )
            for event in ["PROCESAMIENTO_FINALIZADO"] * doc["finals"] + doc["events"]:
                await conn.execute("INSERT INTO historial_documento (documento_triaje_id,evento) VALUES ($1,$2)", uid, event)
            for decision in doc["legacy"]:
                await conn.execute("""INSERT INTO auditorias_hitl (documento_triaje_id,documento_id,decision,auditor_id)
                  VALUES ($1,$2,$3,$4)""", uid, doc.get("external_audit", f"API04-MATRIX-{index:04d}"), decision, auditor)
            for decision in doc["coordination"]:
                await conn.execute("""INSERT INTO auditorias_coordinacion (documento_id,decision,justificacion_clinica)
                  VALUES ($1,$2,'API04 sintético')""", uid, decision)
            if doc.get("null_coordination"):
                episode = await conn.fetchval("INSERT INTO episodios_clinicos (codigo_episodio) VALUES ('API04-EPISODE') RETURNING id")
                await conn.execute("""INSERT INTO auditorias_coordinacion (episodio_id,decision,justificacion_clinica)
                  VALUES ($1,'aprobado','Solo episodio sintético')""", episode)
    return ids


@pytest.fixture
async def metrics_reader(metrics_pg, monkeypatch):
    module = importlib.import_module("app.repositories.metrics_repository")
    registration = _registered_metrics_sandbox()
    pool = await asyncpg.create_pool(metrics_sandbox_url(registration), min_size=1, max_size=5,
                                    init=lambda conn: guard_metrics_test_connection(conn, registration))
    original = module.get_db_pool
    async def provider():
        return pool
    try:
        with monkeypatch.context() as local:
            local.setattr(module, "get_db_pool", provider)
            yield module.obtener_metricas
        assert module.get_db_pool is original
    finally:
        await asyncio.wait_for(pool.close(), 10)


@pytest.mark.parametrize("name,documents", MATRIX, ids=[name for name, _ in MATRIX])
async def test_metrics_sql_matrix(metrics_clean, metrics_reader, name, documents):
    conn, auditor = metrics_clean
    await load_metrics_manifest(conn, auditor, documents)
    before = await clinical_snapshot(conn)
    result = json.loads((await metrics_reader()).model_dump_json())
    expected = manifest_oracle(documents)
    folder = Path(os.environ["API04_EVIDENCE_DIR"]) / "tdd-core"
    folder.mkdir(exist_ok=True)
    record = {"manifest": documents, "expected": expected, "actual": result,
              "snapshot_before": before, "snapshot_after": await clinical_snapshot(conn)}
    (folder / (name + ".json")).write_text(json.dumps(record, indent=2), encoding="utf-8")
    if name.startswith("hitl-"):
        hitl = folder.parent / "hitl"
        hitl.mkdir(exist_ok=True)
        (hitl / (name + ".json")).write_text(json.dumps(record, indent=2), encoding="utf-8")
    assert result == expected
    assert record["snapshot_after"] == before


async def test_metrics_foreign_keys_remain_enforced(metrics_clean):
    conn, auditor = metrics_clean
    for table, column in (("historial_documento", "documento_triaje_id"), ("auditorias_coordinacion", "documento_id")):
        async with conn.transaction():
            with pytest.raises(asyncpg.ForeignKeyViolationError):
                async with conn.transaction():
                    if table == "historial_documento":
                        await conn.execute(f"INSERT INTO {table} ({column},evento) VALUES ($1,'PROCESAMIENTO_FINALIZADO')", uuid4())
                    else:
                        await conn.execute(f"INSERT INTO {table} ({column},decision,justificacion_clinica) VALUES ($1,'aprobado','API04')", uuid4())
    with pytest.raises(asyncpg.ForeignKeyViolationError):
        async with conn.transaction():
            await conn.execute("""INSERT INTO auditorias_hitl
              (documento_triaje_id,documento_id,decision,auditor_id) VALUES ($1,'API04-ORPHAN','aprobar',$2)""", uuid4(), auditor)


async def clinical_snapshot(conn):
    tables = ("documentos_triaje", "historial_documento", "auditorias_hitl", "auditorias_coordinacion",
              "pacientes", "episodios_clinicos", "trazabilidad_eventos", "notificaciones", "cola_procesamiento", "configuracion_sistema")
    snapshot = {}
    for table in tables:
        rows = await conn.fetch(f"SELECT to_jsonb(t)::text AS value FROM {table} t ORDER BY to_jsonb(t)::text")
        snapshot[table] = hashlib.sha256(json.dumps([row["value"] for row in rows]).encode()).hexdigest()
    return snapshot


async def metrics_transition(conn, auditor, read):
    ids = await load_metrics_manifest(conn, auditor, [manifest_document(), manifest_document()])
    before = manifest_oracle([manifest_document(), manifest_document()])
    after = manifest_oracle([manifest_document(priority="Urgente", reviewed=True), manifest_document()])
    sequence = []
    async def sample(phase):
        start = perf_counter_ns()
        body = await read()
        sequence.append(dict(phase=phase, start_ns=start, end_ns=perf_counter_ns(), body=body))
        return body
    baseline = await clinical_snapshot(conn)
    assert await sample("stationary") == before
    assert await clinical_snapshot(conn) == baseline
    for round_index in range(4):
        target = after if round_index % 2 == 0 else before
        old = before if round_index % 2 == 0 else after
        transaction = conn.transaction()
        await transaction.start()
        try:
            await conn.execute("UPDATE documentos_triaje SET nivel_prioridad=$2 WHERE id=$1", ids[0], "Urgente" if round_index % 2 == 0 else "Rutina")
            if round_index % 2 == 0:
                await conn.execute("""INSERT INTO auditorias_coordinacion (documento_id,decision,justificacion_clinica)
                    VALUES ($1,'aprobado','API04 transición')""", ids[0])
            else:
                await conn.execute("DELETE FROM auditorias_coordinacion WHERE documento_id=$1", ids[0])
            assert await sample("uncommitted") == old
            barrier = asyncio.Event()
            async def concurrent():
                await barrier.wait()  # noqa: B023  # barrier se consume en la misma iteración
                return await sample("around-commit")
            requests = [asyncio.create_task(concurrent()) for _ in range(5)]
            barrier.set()
            await transaction.commit()
            results = await asyncio.gather(*requests)
            assert all(result in (before, after) for result in results)
            assert await sample("started-after-confirmed-commit") == target
        except BaseException:
            if conn.is_in_transaction():
                await transaction.rollback()
            raise
    final_snapshot = await clinical_snapshot(conn)
    assert await sample("stationary-final") == before
    assert await clinical_snapshot(conn) == final_snapshot
    folder = Path(os.environ["API04_EVIDENCE_DIR"]) / "tdd-core"
    folder.mkdir(exist_ok=True)
    (folder / ("transition-" + read.__name__ + ".json")).write_text(json.dumps({"responses": sorted(sequence, key=lambda row: row["start_ns"]), "stationary_before": baseline, "stationary_after": final_snapshot}, indent=2), encoding="utf-8")


async def test_metrics_readonly_fresh_coherent_transition(metrics_clean, metrics_reader):
    conn, auditor = metrics_clean
    async def direct():
        return json.loads((await metrics_reader()).model_dump_json())
    await metrics_transition(conn, auditor, direct)


async def test_metrics_distribution_seed_becomes_eligible_without_time(metrics_clean, metrics_reader):
    conn, auditor = metrics_clean
    documents = [manifest_document(eligible=False, status="recibido", finals=0, seed=True, time=None)]
    ids = await load_metrics_manifest(conn, auditor, documents)
    assert json.loads((await metrics_reader()).model_dump_json()) == manifest_oracle(documents)
    async with conn.transaction():
        await conn.execute("UPDATE documentos_triaje SET status='procesado' WHERE id=$1", ids[0])
        await conn.execute("INSERT INTO historial_documento (documento_triaje_id,evento) VALUES ($1,'PROCESAMIENTO_FINALIZADO')", ids[0])
    assert json.loads((await metrics_reader()).model_dump_json()) == manifest_oracle([manifest_document(seed=True, time=None)])
    assert await conn.fetchval("SELECT nodos_ejecutados::text FROM documentos_triaje WHERE id=$1", ids[0]) == "[]"


@pytest.mark.parametrize("role", ["ADMINISTRADOR", "COORDINADOR", "SUPERVISOR", "AUDITOR", "OPERADOR"])
async def test_metrics_http_real_active_roles_empty(metrics_http, role):
    client, tokens = metrics_http
    response = await client.get("/api/v1/metrics", headers={"Authorization": f"Bearer {tokens[role]}"})
    assert response.status_code == 200
    assert response.json() == manifest_oracle([])
    record_metrics_http(f"active-{role}", response, manifest_oracle([]))


@pytest.mark.parametrize("kind", ["absent", "malformed", "unknown", "expired", "revoked", "inactive"])
async def test_metrics_http_real_invalid_sessions(metrics_http, metrics_pg, kind):
    client, tokens = metrics_http
    token = tokens["OPERADOR"]
    digest = hashlib.sha256(token.encode()).hexdigest()
    if kind == "expired":
        await metrics_pg.execute("UPDATE sesiones_usuario SET expires_at=now()-interval '1 second' WHERE token_hash=$1", digest)
    elif kind == "revoked":
        await metrics_pg.execute("UPDATE sesiones_usuario SET revoked_at=now() WHERE token_hash=$1", digest)
    elif kind == "inactive":
        await metrics_pg.execute("UPDATE usuarios SET estado='INACTIVO' WHERE id=(SELECT usuario_id FROM sesiones_usuario WHERE token_hash=$1)", digest)
    headers = {} if kind == "absent" else {"Authorization": "Basic invalid" if kind == "malformed" else f"Bearer {secrets.token_urlsafe(32) if kind == 'unknown' else token}"}
    response = await client.get("/api/v1/metrics", headers=headers)
    assert response.status_code == 401
    record_metrics_http(f"session-{kind}", response)


@pytest.mark.parametrize("table", ["sesiones_usuario", "historial_documento"])
async def test_metrics_http_real_inaccessible_source(metrics_http, metrics_pg, table):
    client, tokens = metrics_http
    await guard_metrics_test_connection(metrics_pg, _registered_metrics_sandbox())
    await metrics_pg.execute(f"ALTER TABLE {table} RENAME TO api04_unavailable_source")
    try:
        response = await client.get("/api/v1/metrics", headers={"Authorization": f"Bearer {tokens['OPERADOR']}"})
        assert response.status_code == 503
        record_metrics_http(f"source-{table}", response)
        if table == "sesiones_usuario":
            assert response.json() == {"detail": "El servicio de autenticación no está disponible temporalmente."}
        else:
            assert response.json()["detail"]["error"] == "POSTGRESQL_NO_DISPONIBLE"
    finally:
        await guard_metrics_test_connection(metrics_pg, _registered_metrics_sandbox())
        await metrics_pg.execute(f"ALTER TABLE api04_unavailable_source RENAME TO {table}")


@pytest.mark.parametrize("documents", [[], [manifest_document(time=0)], [manifest_document(priority="Ambiguo", time=None)], [manifest_document(time=1000), manifest_document(time=2333)]], ids=["empty", "zero", "no-time", "tie"])
async def test_metrics_http_real_numeric_payload_readonly(metrics_http, metrics_clean, documents):
    from app._generated.models import MetricsResponse
    client, tokens = metrics_http
    conn, auditor = metrics_clean
    await load_metrics_manifest(conn, auditor, documents)
    before = await clinical_snapshot(conn)
    response = await client.get("/api/v1/metrics", headers={"Authorization": f"Bearer {tokens['OPERADOR']}"})
    assert response.status_code == 200
    assert response.json() == manifest_oracle(documents)
    MetricsResponse.model_validate(response.json())
    assert await clinical_snapshot(conn) == before
    record_metrics_http(f"payload-{len(documents)}-{documents[0]['time'] if documents else 'empty'}", response, manifest_oracle(documents))


async def test_metrics_http_real_commit_transition(metrics_http, metrics_clean):
    client, tokens = metrics_http
    conn, auditor = metrics_clean
    async def http():
        response = await client.get("/api/v1/metrics", headers={"Authorization": f"Bearer {tokens['OPERADOR']}"})
        assert response.status_code == 200
        return response.json()
    await metrics_transition(conn, auditor, http)


def record_metrics_http(name, response, expected=None):
    """Persist aggregate/error bodies only, never headers or login/user data."""
    folder = Path(os.environ["API04_EVIDENCE_DIR"]) / "http-postgres"
    folder.mkdir(exist_ok=True)
    (folder / (name + ".json")).write_text(json.dumps({
        "status": response.status_code, "body": response.json(), "expected": expected,
    }, indent=2), encoding="utf-8")
