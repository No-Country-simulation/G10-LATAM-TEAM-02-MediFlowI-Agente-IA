"""BD-04: evidencia con commits reales, nunca con mediflow_dev.

El reset requiere un sandbox desechable registrado explícitamente como propio.
No existe limpieza entre las dos cargas de una prueba.
"""

import asyncio
import getpass
import importlib
import json
import os
import secrets
import subprocess
import sys
from datetime import date
from pathlib import Path
from unittest.mock import AsyncMock, Mock
from urllib.parse import urlsplit
from uuid import uuid4

import asyncpg
import pytest


@pytest.mark.parametrize("url", [
    "", "not-a-url", "postgresql://bd04_test:x@127.0.0.1:55432/mediflow_dev",
    "postgresql://other:x@127.0.0.1:55432/mediflow_bd04_test",
    "postgresql://bd04_test:x@remote:55432/mediflow_bd04_test",
    "postgresql://bd04_test:x@127.0.0.1:5432/mediflow_bd04_test",
    "postgresql://bd04_test:x@127.0.0.1:55432/mediflow_bd04_test?host=remote",
])
def test_fixture_rejects_unsafe_urls(url):
    with pytest.raises(ValueError):
        validate_test_url(url)


@pytest.mark.parametrize("field,value", [
    ("db", "mediflow_dev"), ("usr", "postgres"), ("schema", "other"),
    ("path", "other, public"), ("address", "192.168.1.2"), ("port", 5433),
])
async def test_fixture_rejects_unsafe_effective_connection(field, value):
    row = dict(db="mediflow_bd04_test", usr="bd04_test", schema="public",
               path='"$user", public', address="127.0.0.1", port=55432)
    row[field] = value
    conn = AsyncMock()
    conn.fetchrow.return_value = row
    with pytest.raises(ValueError):
        await guard_test_connection(conn)
    conn.execute.assert_not_called()


def test_missing_required_postgres_fails_not_skips(monkeypatch):
    monkeypatch.delenv("BD04_TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("BD04_REQUIRE_POSTGRES", "1")
    with pytest.raises(ValueError):
        sandbox_url()


def validate_test_url(url):
    parsed = urlsplit(url)
    if (parsed.scheme != "postgresql" or parsed.hostname != "127.0.0.1"
        or parsed.port != 55432 or parsed.username != "bd04_test"
        or parsed.path != "/mediflow_bd04_test" or not parsed.password
        or parsed.query or parsed.fragment):
        raise ValueError("URL de sandbox no autorizada")
    return url


def sandbox_url():
    url = os.environ.get("BD04_TEST_DATABASE_URL", "")
    if not url and os.environ.get("BD04_REQUIRE_POSTGRES") != "1":
        pytest.skip("Integración PostgreSQL no solicitada; no acredita BD-04")
    return validate_test_url(url)


async def guard_test_connection(conn):
    row = await conn.fetchrow("""SELECT current_database() AS db, current_user AS usr,
        current_schema() AS schema, current_setting('search_path') AS path,
        host(inet_server_addr()) AS address, inet_server_port() AS port""")
    if (row["db"] != "mediflow_bd04_test" or row["usr"] != "bd04_test"
        or row["schema"] != "public" or row["path"] not in ('"$user", public', 'public')
        or row["address"] != "127.0.0.1" or row["port"] not in (5432, 55432)):
        raise ValueError("Conexión efectiva no autorizada")


async def connect_sandbox():
    conn = await asyncpg.connect(sandbox_url(), timeout=10)
    try:
        await guard_test_connection(conn)
    except BaseException:
        await conn.close()
        raise
    return conn


@pytest.fixture(scope="session")
def migration_sql():
    env = dict(os.environ, DATABASE_URL=sandbox_url(), PYTHONIOENCODING="utf-8")
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=Path(__file__).resolve().parents[1], env=env, capture_output=True,
        text=True, encoding="utf-8", timeout=60)
    if result.returncode or not result.stdout.startswith("BEGIN;"):
        pytest.fail("Generación SQL offline falló (salida omitida por seguridad)")
    return result.stdout


@pytest.fixture
async def pg(migration_sql):
    # Autorización destructiva limitada EXCLUSIVAMENTE al recurso de test propio.
    if os.environ.get("BD04_TEST_SANDBOX_OWNED") != "1":
        pytest.fail("Registrar sandbox desechable propio: BD04_TEST_SANDBOX_OWNED=1")
    conn = await connect_sandbox()
    try:
        await guard_test_connection(conn)
        await conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        await conn.execute(migration_sql)  # intacto, incluye sus propios BEGIN/COMMIT
        await guard_test_connection(conn)
        yield conn
    finally:
        # No borrar filas al finalizar: el siguiente escenario restaura su sandbox.
        await conn.close()


@pytest.mark.postgres_integration
async def test_fixture_bootstraps_real_head(pg):
    assert await pg.fetchval("SELECT version_num FROM alembic_version") == "p9q909633lm5"
    assert await pg.fetchval("SELECT count(*) FROM usuarios") == 4
    assert await pg.fetchval("SELECT count(*) FROM documentos_triaje") == 3
    assert await pg.fetchval("SELECT current_database()") == "mediflow_bd04_test"
    assert os.environ["DATABASE_URL"] == ""


@pytest.fixture
def seed():
    return importlib.import_module("app.scripts.seed_hospital_data")


@pytest.fixture
def passwords():
    return {f"M{i:02}": "Aa1!" + secrets.token_hex(16) for i in range(1, 5)}


async def snapshot(conn):
    """Todas las tablas reales: detectar efectos incluso si no conocemos su nombre."""
    tables = await conn.fetch("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    result = {}
    for row in tables:
        name = row["tablename"]
        # Identificador del catálogo PostgreSQL, nunca entrada del usuario.
        quoted = '"' + name.replace('"', '""') + '"'
        result[name] = await conn.fetchval(
            f"SELECT COALESCE(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text), '[]') FROM {quoted} t")
    return result


async def seed_rows(conn, seed):
    return {table: [dict(r) for r in await conn.fetch(
        f"SELECT * FROM {table} WHERE id=ANY($1::uuid[]) ORDER BY id", [x.id for x in manifest])]
        for table, manifest in [("pacientes", seed.PATIENTS), ("usuarios", seed.USERS),
                                 ("documentos_triaje", seed.DOCUMENTS)]}


@pytest.mark.postgres_integration
async def test_first_load_10_4_5_committed_no_side_effects(pg, seed, passwords, tmp_path, monkeypatch):
    from app.core.security import verify_password

    monkeypatch.chdir(tmp_path)  # script no debe crear archivos en cwd
    baseline = await snapshot(pg)
    result = await seed.seed_hospital_data(pg, passwords, seed.parse_target("test", sandbox_url()))
    assert result.created == (10, 4, 5)
    other = await connect_sandbox()
    try:
        rows = await seed_rows(other, seed)
        assert tuple(len(rows[t]) for t in ("pacientes", "usuarios", "documentos_triaje")) == (10, 4, 5)
        for user in seed.USERS:
            row = next(r for r in rows["usuarios"] if r["id"] == user.id)
            assert row["rol"] == "OPERADOR"
            assert row["especialidad_medica"] == user.especialidad_medica
            assert row["estado"] == "ACTIVO"
            assert verify_password(passwords[user.key], row["password_hash"], row["salt"])
        assert {r["nivel_prioridad"] for r in rows["documentos_triaje"]} == {"Urgente", "Rutina", "Ambiguo"}
        for doc in rows["documentos_triaje"]:
            assert doc["paciente_id"] in {p.id for p in seed.PATIENTS}
            assert doc["status"] == "recibido" and doc["canal_origen"] == "Admision"
            assert doc["tipo_archivo"] == "JSON"
            for key in ("paciente_edad", "episodio_id", "archivo_original", "resultado_json",
                        "oci_bucket", "oci_ruta_objeto", "destino_principal",
                        "diagnostico_principal", "cie10_sugerido", "score_confianza"):
                assert doc[key] is None
            assert json.loads(doc["metadata"]) == {"seed_source": "BD-04", "seed_version": 1}
        after = await snapshot(other)
        for table, prior in baseline.items():
            if table not in rows:
                assert after[table] == prior
            else:
                current = json.loads(after[table])
                assert all(r in current for r in json.loads(prior))
        assert not list(tmp_path.iterdir())
    finally:
        await other.close()


@pytest.mark.postgres_integration
async def test_two_committed_runs_without_cleanup_preserve_every_row(pg, seed, passwords):
    target = seed.parse_target("test", sandbox_url())
    first = await seed.seed_hospital_data(pg, passwords, target)
    assert first.created == (10, 4, 5)
    reader = await connect_sandbox()
    try:
        before = await snapshot(reader)  # conexión distinta prueba commit real
        assert tuple(map(len, (await seed_rows(reader, seed)).values())) == (10, 4, 5)
        # Sin cleanup ni rollback. No requerir contraseñas si todas las cuentas existen.
        second = await seed.seed_hospital_data(pg, {}, target)
        assert second.created == (0, 0, 0) and second.reused == (10, 4, 5)
        assert await snapshot(reader) == before  # incluye salt, estado, FK, timestamps y triggers
        third = await seed.seed_hospital_data(pg, {u.key: "different" for u in seed.USERS}, target)
        assert third.reused == (10, 4, 5)
        assert await snapshot(reader) == before
    finally:
        await reader.close()


@pytest.mark.postgres_integration
async def test_partial_owned_set_completed_credentials_not_reset(pg, seed, passwords):
    target = seed.parse_target("test", sandbox_url())
    await seed.seed_hospital_data(pg, passwords, target)
    # Escenario parcial separado: preparar SOLO filas BD-04 propias, antes de la carga a probar.
    await pg.execute("DELETE FROM documentos_triaje WHERE id=ANY($1::uuid[])",
                     [d.id for d in seed.DOCUMENTS[1:]])
    await pg.execute("DELETE FROM pacientes WHERE id=ANY($1::uuid[])", [p.id for p in seed.PATIENTS[1:]])
    await pg.execute("DELETE FROM usuarios WHERE id=ANY($1::uuid[])", [u.id for u in seed.USERS[1:]])
    await pg.execute("UPDATE usuarios SET estado='INACTIVO' WHERE id=$1", seed.USERS[0].id)
    existing = dict(await pg.fetchrow("SELECT * FROM usuarios WHERE id=$1", seed.USERS[0].id))
    inputs = dict(passwords)
    inputs.pop("M01")
    result = await seed.seed_hospital_data(pg, inputs, target)
    assert result.created == (9, 3, 4) and result.reused == (1, 1, 1)
    assert dict(await pg.fetchrow("SELECT * FROM usuarios WHERE id=$1", seed.USERS[0].id)) == existing


@pytest.mark.postgres_integration
@pytest.mark.parametrize("kind", ["patient_uuid", "patient_doc", "patient_hc", "user_uuid",
                                 "user_dni", "doc_uuid", "doc_id", "doc_metadata", "doc_fk"])
async def test_collisions_roll_back_whole_invocation_preserve_foreign(pg, seed, passwords, kind):
    p, u, d = seed.PATIENTS[-1], seed.USERS[-1], seed.DOCUMENTS[-1]
    if kind.startswith("patient"):
        await pg.execute("""INSERT INTO pacientes (id, numero_documento, historia_clinica, nombres, apellidos)
            VALUES ($1,$2,$3,'Ajeno','No BD04')""", p.id if kind == "patient_uuid" else uuid4(),
            p.numero_documento if kind == "patient_doc" else "OTHER-PATIENT",
            p.historia_clinica if kind == "patient_hc" else "OTHER-HC")
    elif kind.startswith("user"):
        await pg.execute("""INSERT INTO usuarios (id, documento_identidad, password_hash, salt, nombres, apellidos)
            VALUES ($1,$2,'foreign-hash','foreign-salt','Ajeno','No BD04')""",
            u.id if kind == "user_uuid" else uuid4(),
            u.documento_identidad if kind == "user_dni" else "88779900")
    else:
        await pg.execute("""INSERT INTO documentos_triaje (id, documento_id, tipo_archivo, metadata)
            VALUES ($1,$2,'JSON',$3::jsonb)""",
            d.id if kind in ("doc_uuid", "doc_metadata", "doc_fk") else uuid4(),
            "OTHER-DOC" if kind == "doc_uuid" else d.documento_id,
            seed.METADATA if kind == "doc_fk" else "{}")
    before = await snapshot(pg)
    with pytest.raises(seed.SeedError, match="conflicto"):
        await seed.seed_hospital_data(pg, passwords, seed.parse_target("test", sandbox_url()))
    assert await snapshot(pg) == before  # incluye el conflicto documental tardío
    assert not pg.is_in_transaction()


async def invoke_cli(passwords):
    env = dict(os.environ, DATABASE_URL="", PYTHONIOENCODING="utf-8",
               **{f"BD04_PASSWORD_{k}": v for k, v in passwords.items()})
    def run():
        return subprocess.run([sys.executable, "-m", "app.scripts.seed_hospital_data", "--target", "test"],
            cwd=Path(__file__).resolve().parents[1], env=env, capture_output=True,
            text=True, encoding="utf-8", timeout=60)
    return await asyncio.to_thread(run)


@pytest.mark.postgres_integration
async def test_two_independent_cli_processes_consecutive_commits(pg, seed, passwords):
    first = await invoke_cli(passwords)
    assert first.returncode == 0, "CLI falló (salida omitida por seguridad)"
    assert json.loads(first.stdout)["created"] == [10, 4, 5]
    before = await snapshot(pg)
    second = await invoke_cli(passwords)
    assert second.returncode == 0, "CLI falló (salida omitida por seguridad)"
    assert json.loads(second.stdout)["reused"] == [10, 4, 5]
    assert await snapshot(pg) == before
    assert not any(p in first.stdout + second.stdout + first.stderr + second.stderr for p in passwords.values())


@pytest.mark.postgres_integration
async def test_concurrent_loads_serialize_without_duplicates(pg, seed, passwords):
    other = await connect_sandbox()
    try:
        target = seed.parse_target("test", sandbox_url())
        results = await asyncio.gather(seed.seed_hospital_data(pg, passwords, target),
                                       seed.seed_hospital_data(other, passwords, target))
        assert sorted(r.created for r in results) == [(0, 0, 0), (10, 4, 5)]
        assert tuple(map(len, (await seed_rows(pg, seed)).values())) == (10, 4, 5)
        assert await pg.fetchval("SELECT count(*) FROM episodios_clinicos") == 0
        assert await pg.fetchval("SELECT count(*) FROM cola_procesamiento WHERE documento_id LIKE 'BD04-%'") == 0
    finally:
        await other.close()


@pytest.mark.postgres_integration
async def test_four_hashes_use_existing_helper_only_for_new_accounts(pg, seed, passwords, monkeypatch):
    from app.core import security

    hash_spy = Mock(wraps=security.hash_password)
    monkeypatch.setattr(security, "hash_password", hash_spy)
    target = seed.parse_target("test", sandbox_url())
    await seed.seed_hospital_data(pg, passwords, target)
    assert hash_spy.call_count == 4
    rows = await seed_rows(pg, seed)
    assert len({u["salt"] for u in rows["usuarios"]}) == 4
    for user in seed.USERS:
        row = next(u for u in rows["usuarios"] if u["id"] == user.id)
        assert security.verify_password(passwords[user.key], row["password_hash"], row["salt"])
        assert not security.verify_password("wrong-password", row["password_hash"], row["salt"])
    serialized = json.dumps(await snapshot(pg))
    assert all(p not in serialized for p in passwords.values())
    await pg.execute("UPDATE usuarios SET estado='INACTIVO' WHERE id=$1", seed.USERS[0].id)
    before = await snapshot(pg)
    hash_spy.reset_mock()
    await seed.seed_hospital_data(pg, {}, target)
    hash_spy.assert_not_called()
    assert await snapshot(pg) == before


@pytest.mark.postgres_integration
@pytest.mark.parametrize("inputs", ["missing", "invalid"])
async def test_missing_or_invalid_new_credentials_roll_back(pg, seed, passwords, inputs):
    before = await snapshot(pg)
    if inputs == "missing":
        passwords.pop("M04")  # error tardío, luego de pacientes + primeras cuentas
    else:
        passwords["M04"] = "unsafe"
    with pytest.raises(seed.SeedError, match="credenciales"):
        await seed.seed_hospital_data(pg, passwords, seed.parse_target("test", sandbox_url()))
    assert await snapshot(pg) == before


@pytest.mark.postgres_integration
async def test_dynamic_age_real_repository_and_sql_birthday_without_reseed(pg, seed, passwords, monkeypatch):
    from app.repositories import patient_repository as repo

    await seed.seed_hospital_data(pg, passwords, seed.parse_target("test", sandbox_url()))
    before = await snapshot(pg)
    pool = await asyncpg.create_pool(sandbox_url(), min_size=1, max_size=2,
                                    init=guard_test_connection)
    try:
        monkeypatch.setattr(repo, "get_db_pool", AsyncMock(return_value=pool))
        assert "age(CURRENT_DATE, fecha_nacimiento)" in repo.PATIENT_COLUMNS
        rows = await repo.list_patients()
        assert len(rows) == 10
        for row in rows:
            actual = await pg.fetchval("SELECT EXTRACT(YEAR FROM age(CURRENT_DATE, $1::date))::INT",
                                      row["fecha_nacimiento"])
            assert row["edad"] == actual
        assert (await repo.get_patient_by_doc(seed.PATIENTS[0].numero_documento))["id"] == seed.PATIENTS[0].id
        projection = repo.PATIENT_COLUMNS.replace("CURRENT_DATE", "$2::date")
        # Solo controla fecha de referencia en la proyección TEST, no cambia código ni DOB.
        for patient, ref, expected in [
            (seed.PATIENTS[0], date(2026, 10, 7), 35),
            (seed.PATIENTS[0], date(2026, 10, 8), 36),
            (seed.PATIENTS[1], date(2025, 2, 28), 24),
            (seed.PATIENTS[1], date(2025, 3, 1), 25),
            (seed.PATIENTS[1], date(2024, 2, 29), 24),
        ]:
            row = await pg.fetchrow(f"SELECT {projection} FROM pacientes WHERE id=$1", patient.id, ref)
            assert row["edad"] == expected
            assert row["fecha_nacimiento"] == patient.fecha_nacimiento
        assert not await pg.fetchval("""SELECT count(*) FROM information_schema.columns
            WHERE table_schema='public' AND table_name='pacientes' AND column_name='edad'""")
        assert await snapshot(pg) == before
    finally:
        await pool.close()


@pytest.mark.postgres_integration
async def test_schema_mismatch_aborts_without_migration_or_writes(pg, seed, passwords):
    await pg.execute("UPDATE alembic_version SET version_num='old-schema'")
    before = await snapshot(pg)
    with pytest.raises(seed.SeedError, match="esquema"):
        await seed.seed_hospital_data(pg, passwords, seed.parse_target("test", sandbox_url()))
    assert await snapshot(pg) == before


@pytest.mark.postgres_integration
async def test_outer_rollback_transaction_not_accepted_as_committed_load(pg, seed, passwords):
    async with pg.transaction():
        with pytest.raises(seed.SeedError, match="propia transacción"):
            await seed.seed_hospital_data(pg, passwords, seed.parse_target("test", sandbox_url()))
    assert await pg.fetchval("SELECT count(*) FROM pacientes") == 0


@pytest.mark.postgres_integration
async def test_hidden_password_collection_readonly_then_two_committed_loads(
    pg, seed, passwords, monkeypatch, capsys
):
    from app.core import security

    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: True)
    prompt = Mock(side_effect=[passwords[u.key] for u in seed.USERS])
    monkeypatch.setattr(getpass, "getpass", prompt)
    before = await snapshot(pg)
    inputs = await seed.development_passwords(pg, {})  # conexión real exclusivamente de test
    assert prompt.call_count == 4
    assert await snapshot(pg) == before
    target = seed.parse_target("test", sandbox_url())
    first = await seed.seed_hospital_data(pg, inputs, target)
    assert first.created == (10, 4, 5)
    reader = await connect_sandbox()
    try:
        committed = await snapshot(reader)
        rows = await seed_rows(reader, seed)
        for u in seed.USERS:
            row = next(r for r in rows["usuarios"] if r["id"] == u.id)
            assert security.verify_password(passwords[u.key], row["password_hash"], row["salt"])
        prompt.reset_mock(side_effect=True)
        inputs = await seed.development_passwords(pg, {})
        prompt.assert_not_called()
        assert inputs == {}
        second = await seed.seed_hospital_data(pg, inputs, target)
        assert second.created == (0, 0, 0) and second.reused == (10, 4, 5)
        assert await snapshot(reader) == committed
        output = str(capsys.readouterr())
        assert not any(p in output for p in passwords.values())
    finally:
        await reader.close()


@pytest.mark.postgres_integration
async def test_hidden_password_partial_set_asks_only_missing_and_preserves_credentials(
    pg, seed, passwords, monkeypatch
):
    target = seed.parse_target("test", sandbox_url())
    await seed.seed_hospital_data(pg, passwords, target)
    await pg.execute("DELETE FROM usuarios WHERE id=ANY($1::uuid[])", [u.id for u in seed.USERS[1:]])
    await pg.execute("UPDATE usuarios SET estado='INACTIVO' WHERE id=$1", seed.USERS[0].id)
    before = await snapshot(pg)
    old_user = dict(await pg.fetchrow("SELECT * FROM usuarios WHERE id=$1", seed.USERS[0].id))
    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: True)
    prompt = Mock(side_effect=[passwords["M03"], passwords["M04"]])
    monkeypatch.setattr(getpass, "getpass", prompt)
    inputs = await seed.development_passwords(pg, {"M02": passwords["M02"]})
    assert [call.args[0] for call in prompt.call_args_list] == ["Contraseña para M03: ", "Contraseña para M04: "]
    assert await snapshot(pg) == before
    result = await seed.seed_hospital_data(pg, inputs, target)
    assert result.created == (0, 3, 0) and result.reused == (10, 1, 5)
    assert dict(await pg.fetchrow("SELECT * FROM usuarios WHERE id=$1", seed.USERS[0].id)) == old_user
