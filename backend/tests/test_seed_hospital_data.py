"""Pruebas de contrato/entrada BD-04, sin conexiones de desarrollo."""

import getpass
import importlib
import os
import subprocess
import sys
import warnings
from dataclasses import asdict, replace
from datetime import date, timedelta
from unittest.mock import AsyncMock, Mock

import pytest


@pytest.fixture
def seed():
    return importlib.import_module("app.scripts.seed_hospital_data")


def test_manifest_is_stable_typed_and_nonclinical(seed):
    assert (len(seed.PATIENTS), len(seed.USERS), len(seed.DOCUMENTS)) == (10, 4, 5)
    seed.validate_manifest()
    assert len({p.id for p in seed.PATIENTS}) == 10
    assert all(p.id.version == 5 for p in seed.PATIENTS)
    assert all(p.fecha_nacimiento <= date.today() for p in seed.PATIENTS)
    assert all(u.rol == "OPERADOR" for u in seed.USERS)
    assert all(len(u.documento_identidad) == 8 and u.documento_identidad.isdigit()
               for u in seed.USERS)
    assert {u.especialidad_medica for u in seed.USERS} == {
        "Medicina General", "Cardiología", "Neumonología", "Traumatología"}
    assert {d.nivel_prioridad for d in seed.DOCUMENTS} == {"Urgente", "Rutina", "Ambiguo"}
    assert [d.documento_id for d in seed.DOCUMENTS] == [f"BD04-DOC-{i:03}" for i in range(1, 6)]
    assert all("edad" not in asdict(p) for p in seed.PATIENTS)
    assert all("edad" not in asdict(d) for d in seed.DOCUMENTS)


@pytest.mark.parametrize("dob", [None, "invalid", date.today() + timedelta(days=1)])
def test_invalid_birth_dates_rejected(seed, monkeypatch, dob):
    monkeypatch.setattr(seed, "PATIENTS", (replace(seed.PATIENTS[0], fecha_nacimiento=dob),
                                         *seed.PATIENTS[1:]))
    with pytest.raises(seed.SeedError, match="manifiesto"):
        seed.validate_manifest()


@pytest.mark.parametrize("url", ["", "invalid", "postgresql://u:p@host/mediflow_dev",
    "postgresql://bd04_test:p@127.0.0.1:5432/mediflow_bd04_test",
    "postgresql://bd04_test:p@127.0.0.1:55432/mediflow_bd04_test?host=other"])
def test_target_test_rejects_unsafe_input(seed, url):
    with pytest.raises(seed.SeedError):
        seed.parse_target("test", url)


def test_cli_missing_url_has_no_fallback(seed, monkeypatch, capsys):
    monkeypatch.delenv("BD04_TEST_DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql://secret:secret@host/mediflow_dev")
    connect = AsyncMock()
    monkeypatch.setattr(seed.asyncpg, "connect", connect)
    assert seed.main(["--target", "test"]) != 0
    connect.assert_not_called()
    assert "secret" not in str(capsys.readouterr())


@pytest.mark.parametrize("scheme", ["postgresql", "postgresql+asyncpg"])
@pytest.mark.parametrize("interactive,answer", [(False, "mediflow_dev"), (True, "no")])
def test_development_without_human_confirmation_never_connects(
    seed, monkeypatch, capsys, interactive, answer, scheme
):
    monkeypatch.setenv("DATABASE_URL", f"{scheme}://u:secret@127.0.0.1:5432/mediflow_dev")
    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: interactive)
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: interactive)
    monkeypatch.setattr("builtins.input", lambda _: answer)
    connect = AsyncMock()
    monkeypatch.setattr(seed.asyncpg, "connect", connect)
    assert seed.main(["--target", "development"]) != 0
    connect.assert_not_called()
    assert "secret" not in str(capsys.readouterr())


def test_development_accepts_docker_url_without_exposing_credentials(seed):
    target = seed.parse_target("development",
        "postgresql+asyncpg://u:secret@postgres:5432/mediflow_dev")
    assert target.url == "postgresql://u:secret@postgres:5432/mediflow_dev"
    assert (target.host, target.port, target.database) == ("postgres", 5432, "mediflow_dev")
    assert "secret" not in repr(target)


@pytest.mark.parametrize("mode,url", [
    ("test", "postgresql+asyncpg://bd04_test:secret@127.0.0.1:55432/mediflow_bd04_test"),
    ("development", "postgresql+asyncpg://u:secret@postgres:5432/mediflow_bd04_test"),
    ("development", "postgresql+asyncpg://u:secret@postgres:5432/mediflow_dev?host=other"),
    ("development", "postgresql+asyncpg://u:secret@postgres:5432/mediflow_dev#other"),
    ("development", "postgresql+other://u:secret@postgres:5432/mediflow_dev"),
])
def test_docker_url_support_does_not_relax_destination_guards(seed, mode, url):
    with pytest.raises(seed.SeedError) as error:
        seed.parse_target(mode, url)
    assert "secret" not in str(error.value)


async def test_hidden_inputs_only_for_missing_new_accounts(seed, monkeypatch, capsys):
    rows = [{k: v for k, v in asdict(u).items() if k != "key"} for u in seed.USERS]
    conn = AsyncMock()
    conn.fetch.side_effect = [[rows[0]], [], [rows[2]], []]
    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: True)
    prompt = Mock(return_value="HiddenPassword#2026")
    monkeypatch.setattr(getpass, "getpass", prompt)
    supplied = {"M02": "EnvironmentPassword#2026"}
    before_env = dict(os.environ)
    result = await seed.development_passwords(conn, supplied)
    assert result == {**supplied, "M04": "HiddenPassword#2026"}
    assert supplied == {"M02": "EnvironmentPassword#2026"}
    assert dict(os.environ) == before_env
    prompt.assert_called_once_with("Contraseña para M04: ")
    conn.execute.assert_not_called()
    conn.transaction.assert_not_called()
    assert "Password" not in str(capsys.readouterr())


@pytest.mark.parametrize("failure", ["no_tty", "echo_fallback", "invalid", "eof", "interrupt"])
async def test_hidden_input_fails_closed_without_writes_or_secret_leaks(
    seed, monkeypatch, capsys, failure
):
    conn = AsyncMock()
    conn.fetch.return_value = []
    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: failure != "no_tty")
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: True)
    secret = "unsafe-secret"

    def read(_):
        if failure == "echo_fallback":
            warnings.warn(secret, getpass.GetPassWarning, stacklevel=2)
            pytest.fail("No debe continuar con entrada visible")
        if failure == "eof":
            raise EOFError
        if failure == "interrupt":
            raise KeyboardInterrupt
        return secret

    prompt = Mock(side_effect=read)
    monkeypatch.setattr(getpass, "getpass", prompt)
    expected = {"eof": EOFError, "interrupt": KeyboardInterrupt}.get(failure, seed.SeedError)
    with pytest.raises(expected) as error:
        await seed.development_passwords(conn, {})
    assert secret not in str(error.value)
    conn.execute.assert_not_called()
    conn.transaction.assert_not_called()
    if failure == "no_tty":
        prompt.assert_not_called()
    assert secret not in str(capsys.readouterr())


async def test_invalid_configured_password_is_not_replaced_by_prompt(seed, monkeypatch):
    conn = AsyncMock()
    conn.fetch.return_value = []
    prompt = Mock()
    monkeypatch.setattr(getpass, "getpass", prompt)
    with pytest.raises(seed.SeedError, match="credenciales"):
        await seed.development_passwords(conn, {"M01": "invalid"})
    prompt.assert_not_called()
    conn.execute.assert_not_called()


@pytest.mark.parametrize("guard", ["validate_connection", "validate_schema"])
async def test_development_guards_run_before_password_prompts_and_loader(seed, monkeypatch, guard):
    conn = AsyncMock()
    monkeypatch.setattr(seed.asyncpg, "connect", AsyncMock(return_value=conn))
    monkeypatch.setattr(seed, "validate_connection", AsyncMock())
    monkeypatch.setattr(seed, "validate_schema", AsyncMock())
    monkeypatch.setattr(seed, guard, AsyncMock(side_effect=seed.SeedError("destino/esquema")))
    prompt = Mock()
    monkeypatch.setattr(getpass, "getpass", prompt)
    loader = AsyncMock()
    monkeypatch.setattr(seed, "seed_hospital_data", loader)
    target = replace(seed.parse_target("development",
        "postgresql+asyncpg://u:secret@postgres:5432/mediflow_dev"), confirmed=True)
    with pytest.raises(seed.SeedError):
        await seed.run_command(target, {})
    prompt.assert_not_called()
    loader.assert_not_called()
    conn.execute.assert_not_called()
    conn.close.assert_awaited_once()


@pytest.mark.parametrize("cancel", [EOFError, KeyboardInterrupt])
def test_cli_hidden_input_cancellation_closes_connection_without_loading(
    seed, monkeypatch, capsys, cancel
):
    for u in seed.USERS:
        monkeypatch.delenv(f"BD04_PASSWORD_{u.key}", raising=False)
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:secret@postgres:5432/mediflow_dev")
    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: "mediflow_dev")
    conn = AsyncMock()
    conn.fetch.return_value = []
    monkeypatch.setattr(seed.asyncpg, "connect", AsyncMock(return_value=conn))
    monkeypatch.setattr(seed, "validate_connection", AsyncMock())
    monkeypatch.setattr(seed, "validate_schema", AsyncMock())
    monkeypatch.setattr(getpass, "getpass", Mock(side_effect=cancel))
    loader = AsyncMock()
    monkeypatch.setattr(seed, "seed_hospital_data", loader)
    assert seed.main(["--target", "development"]) == 1
    loader.assert_not_called()
    conn.close.assert_awaited_once()
    output = str(capsys.readouterr())
    assert "cancelada" in output and "secret" not in output and "Traceback" not in output


async def test_test_target_never_prompts_for_missing_credentials(seed, monkeypatch):
    conn = AsyncMock()
    monkeypatch.setattr(seed.asyncpg, "connect", AsyncMock(return_value=conn))
    loader = AsyncMock(return_value=seed.SeedResult((0, 0, 0), (10, 4, 5)))
    monkeypatch.setattr(seed, "seed_hospital_data", loader)
    prompt = Mock()
    monkeypatch.setattr(getpass, "getpass", prompt)
    target = seed.parse_target("test",
        "postgresql://bd04_test:secret@127.0.0.1:55432/mediflow_bd04_test")
    await seed.run_command(target, {})
    prompt.assert_not_called()
    loader.assert_awaited_once_with(conn, {}, target)
    conn.close.assert_awaited_once()


def test_cli_development_confirmation_then_hidden_passwords_then_loader(seed, monkeypatch, capsys):
    for u in seed.USERS:
        monkeypatch.delenv(f"BD04_PASSWORD_{u.key}", raising=False)
    monkeypatch.setenv("BD04_PASSWORD_M01", "EnvironmentPassword#2026")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:secret@postgres:5432/mediflow_dev")
    monkeypatch.setattr(seed.sys.stdin, "isatty", lambda: True)
    monkeypatch.setattr(seed.sys.stdout, "isatty", lambda: True)
    events = []

    def confirm(_):
        events.append("confirm")
        return "mediflow_dev"

    def prompt(message):
        events.append(message)
        return "HiddenPassword#2026"

    async def guard(*_):
        events.append("guard")

    async def load(conn, inputs, target):
        events.append("load")
        assert target.confirmed and target.url.startswith("postgresql://")
        assert inputs == {"M01": "EnvironmentPassword#2026", **{
            u.key: "HiddenPassword#2026" for u in seed.USERS[1:]}}
        return seed.SeedResult((10, 4, 5), (0, 0, 0))

    conn = AsyncMock()
    conn.fetch.return_value = []
    monkeypatch.setattr("builtins.input", confirm)
    monkeypatch.setattr(getpass, "getpass", prompt)
    monkeypatch.setattr(seed.asyncpg, "connect", AsyncMock(return_value=conn))
    monkeypatch.setattr(seed, "validate_connection", guard)
    monkeypatch.setattr(seed, "validate_schema", guard)
    monkeypatch.setattr(seed, "seed_hospital_data", load)
    assert seed.main(["--target", "development"]) == 0
    assert events == ["confirm", "guard", "guard", "Contraseña para M02: ",
                      "Contraseña para M03: ", "Contraseña para M04: ", "load"]
    conn.close.assert_awaited_once()
    output = str(capsys.readouterr())
    assert "postgres:5432/mediflow_dev" in output
    assert all(secret not in output for secret in ("secret", "HiddenPassword#2026", "EnvironmentPassword#2026"))


async def test_existing_identity_conflict_aborts_before_any_prompt(seed, monkeypatch):
    conn = AsyncMock()
    conn.fetch.side_effect = [[], [{"id": seed.USERS[1].id}]]
    prompt = Mock()
    monkeypatch.setattr(getpass, "getpass", prompt)
    with pytest.raises(seed.SeedError, match="conflicto"):
        await seed.development_passwords(conn, {})
    prompt.assert_not_called()
    conn.execute.assert_not_called()


def test_import_help_and_missing_target_have_no_effects(tmp_path):
    env = dict(os.environ, DATABASE_URL="", BD04_TEST_DATABASE_URL="",
               PYTHONIOENCODING="utf-8")
    before = list(tmp_path.iterdir())
    for args, expected in [(["-c", "import app.scripts.seed_hospital_data"], 0),
                           (["-m", "app.scripts.seed_hospital_data", "--help"], 0),
                           (["-m", "app.scripts.seed_hospital_data"], 2)]:
        proc = subprocess.run([sys.executable, *args], cwd=tmp_path, env=env,
                              capture_output=True, timeout=30)
        assert proc.returncode == expected
    assert list(tmp_path.iterdir()) == before


def test_ownership_requires_all_identifiers_not_name_or_salt(seed):
    from uuid import uuid4

    p = seed.PATIENTS[0]
    expected = dict(id=p.id, numero_documento=p.numero_documento, historia_clinica=p.historia_clinica)
    assert seed.owned_row([], expected) is None
    assert seed.owned_row([expected], expected) == expected
    for row in [dict(expected, id=uuid4()), dict(expected, historia_clinica="foreign")]:
        with pytest.raises(seed.SeedError, match="conflicto"):
            seed.owned_row([row], expected)
    with pytest.raises(seed.SeedError, match="conflicto"):
        seed.owned_row([expected, expected], expected)
    doc = dict(id=seed.DOCUMENTS[0].id, documento_id=seed.DOCUMENTS[0].documento_id,
               metadata={"seed_source": "BD-04", "seed_version": 1})
    assert seed.owned_row([dict(doc, metadata=seed.METADATA)], doc)
    with pytest.raises(seed.SeedError, match="conflicto"):
        seed.owned_row([dict(doc, metadata={})], doc)


@pytest.mark.parametrize("password", [None, "Short#1", "lowercase_only123!",
    "UPPERCASE_ONLY123!", "NoNumbersAllowed!", "NoSymbolsAllowed123"])
def test_current_password_policy_enforced_without_leaks(seed, password):
    with pytest.raises(seed.SeedError, match="credenciales") as error:
        seed.validate_password(password)
    if password:
        assert password not in str(error.value)


def test_cli_driver_error_is_sanitized(seed, monkeypatch, capsys):
    secret = "driver-secret-must-not-leak"
    monkeypatch.setenv("BD04_TEST_DATABASE_URL",
                       f"postgresql://bd04_test:{secret}@127.0.0.1:55432/mediflow_bd04_test")

    async def fail(*_):
        raise RuntimeError(secret)

    monkeypatch.setattr(seed, "run_command", fail)
    assert seed.main(["--target", "test"]) == 1
    output = capsys.readouterr()
    assert secret not in str(output) and "Traceback" not in str(output)
    assert not output.out


def test_unknown_cli_argument_not_echoed(seed, capsys):
    with pytest.raises(SystemExit) as error:
        seed.main(["--target", "test", "--password=secret-must-not-leak"])
    assert error.value.code == 2
    assert "secret-must-not-leak" not in str(capsys.readouterr())


@pytest.mark.parametrize("field,value", [("db", "mediflow_dev"), ("usr", "other"),
    ("schema", "other"), ("path", "other,public"), ("port", 5433), ("address", "10.0.0.1")])
async def test_loader_checks_effective_destination_before_dml(seed, field, value):
    row = dict(db="mediflow_bd04_test", usr="bd04_test", schema="public",
               path='"$user", public', address="127.0.0.1", port=55432)
    row[field] = value
    conn = AsyncMock()
    conn.fetchrow.return_value = row
    with pytest.raises(seed.SeedError, match="destino"):
        await seed.seed_hospital_data(conn, {}, seed.parse_target("test",
            "postgresql://bd04_test:unused@127.0.0.1:55432/mediflow_bd04_test"))
    conn.execute.assert_not_called()
    conn.transaction.assert_not_called()


async def test_command_closes_connection_when_load_fails(seed, monkeypatch):
    conn = AsyncMock()
    conn.fetchrow.return_value = dict(db="mediflow_dev", usr="bd04_test", schema="public",
        path="public", address="127.0.0.1", port=55432)
    monkeypatch.setattr(seed.asyncpg, "connect", AsyncMock(return_value=conn))
    with pytest.raises(seed.SeedError):
        await seed.run_command(seed.parse_target("test",
            "postgresql://bd04_test:unused@127.0.0.1:55432/mediflow_bd04_test"), {})
    conn.close.assert_awaited_once()


@pytest.mark.parametrize("mode", ["forged_test", "unconfirmed_development"])
async def test_command_revalidates_declaration_before_connect(seed, monkeypatch, mode):
    connect = AsyncMock()
    monkeypatch.setattr(seed.asyncpg, "connect", connect)
    if mode == "forged_test":
        target = replace(seed.parse_target("test",
            "postgresql://bd04_test:unused@127.0.0.1:55432/mediflow_bd04_test"),
            url="postgresql://bd04_test:unused@127.0.0.1:55432/mediflow_dev")
    else:
        target = seed.parse_target("development", "postgresql://u:unused@127.0.0.1:5432/mediflow_dev")
    with pytest.raises(seed.SeedError, match="destino"):
        await seed.run_command(target, {})
    connect.assert_not_called()
