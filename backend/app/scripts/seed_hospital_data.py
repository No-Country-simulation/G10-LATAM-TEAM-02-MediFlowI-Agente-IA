"""BD-04: semilla explícita y transaccional, sin archivos ni flujo clínico.

Desde backend: python -m app.scripts.seed_hospital_data --target test|development.
No lee .env ni el pool global. Desarrollo requiere terminal y confirmación humana.
"""

import argparse
import asyncio
import getpass
import json
import os
import sys
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, replace
from datetime import date
from typing import NoReturn
from urllib.parse import unquote, urlsplit
from uuid import UUID, uuid5

import asyncpg

NAMESPACE = UUID("7db6a203-fc73-5abe-bb54-f460519d6ba2")
SCHEMA_REVISION = "p9q909633lm5"
METADATA = '{"seed_source":"BD-04","seed_version":1}'
LOCK_KEY = int.from_bytes(b"BD04/v1\0", "big")


def seed_id(entity: str, key: str) -> UUID:
    return uuid5(NAMESPACE, f"BD-04/v1/{entity}/{key}")


@dataclass(frozen=True)
class Patient:
    key: str
    id: UUID
    numero_documento: str
    historia_clinica: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    tipo_documento: str = "DNI"


@dataclass(frozen=True)
class User:
    key: str
    id: UUID
    documento_identidad: str
    nombres: str
    apellidos: str
    especialidad_medica: str
    rol: str = "OPERADOR"


@dataclass(frozen=True)
class Document:
    key: str
    id: UUID
    documento_id: str
    paciente_id: UUID
    nivel_prioridad: str


_BIRTH_DATES = (
    date(1990, 10, 8), date(2000, 2, 29), date(1975, 1, 15), date(1985, 3, 20),
    date(1960, 7, 12), date(1995, 12, 5), date(2010, 6, 18), date(1980, 9, 25),
    date(2005, 4, 30), date(1955, 11, 2),
)
PATIENTS = tuple(Patient(
    f"P{i:02}", seed_id("patient", f"P{i:02}"), f"9904{i:04}", f"BD04-HC-{i:03}",
    f"Paciente sintético {i:02}", "BD04", dob,
) for i, dob in enumerate(_BIRTH_DATES, 1))
USERS = tuple(User(
    f"M{i:02}", seed_id("user", f"M{i:02}"), f"99041{i:03}",
    f"Médico sintético {i:02}", "BD04", specialty,
) for i, specialty in enumerate(
    ("Medicina General", "Cardiología", "Neumonología", "Traumatología"), 1))
DOCUMENTS = tuple(Document(
    f"D{i:02}", seed_id("document", f"D{i:02}"), f"BD04-DOC-{i:03}",
    PATIENTS[i - 1].id, priority,
) for i, priority in enumerate(("Urgente", "Rutina", "Ambiguo", "Rutina", "Urgente"), 1))


class SeedError(ValueError):
    """Error saneado: nunca incluir valores recibidos ni excepciones del driver."""


@dataclass(frozen=True)
class Target:
    mode: str
    url: str = field(repr=False)
    host: str
    port: int
    database: str
    username: str
    confirmed: bool = False


@dataclass(frozen=True)
class SeedResult:
    created: tuple[int, int, int]
    reused: tuple[int, int, int]


def validate_manifest() -> None:
    if ((len(PATIENTS), len(USERS), len(DOCUMENTS)) != (10, 4, 5)
        or any(type(p.fecha_nacimiento) is not date or p.fecha_nacimiento > date.today()
               for p in PATIENTS)
        or len({p.numero_documento for p in PATIENTS}) != 10
        or len({p.historia_clinica for p in PATIENTS}) != 10
        or len({u.documento_identidad for u in USERS}) != 4
        or any(u.rol != "OPERADOR" or len(u.documento_identidad) != 8
               or not u.documento_identidad.isascii() or not u.documento_identidad.isdigit()
               for u in USERS)
        or {u.especialidad_medica for u in USERS} != {
            "Medicina General", "Cardiología", "Neumonología", "Traumatología"}
        or {d.nivel_prioridad for d in DOCUMENTS} != {"Urgente", "Rutina", "Ambiguo"}
        or len({d.documento_id for d in DOCUMENTS}) != 5
        or any(d.paciente_id not in {p.id for p in PATIENTS} for d in DOCUMENTS)
        or len({p.id for p in PATIENTS} | {u.id for u in USERS} | {d.id for d in DOCUMENTS}) != 19):
        raise SeedError("entrada: manifiesto BD-04 inválido")


def parse_target(mode: str, url: str) -> Target:
    try:
        # Alias de SQLAlchemy usado por Compose; asyncpg recibe un DSN nativo.
        # Test conserva su contrato estricto y nunca hereda configuración de Docker.
        if mode == "development" and url.startswith("postgresql+asyncpg://"):
            url = "postgresql://" + url.removeprefix("postgresql+asyncpg://")
        parts = urlsplit(url)
        database = unquote(parts.path.removeprefix("/"))
        username = unquote(parts.username or "")
        host = parts.hostname or ""
        port = parts.port or 5432
        if (mode not in ("test", "development") or parts.scheme != "postgresql"
            or not host or not username or not parts.password
            or parts.query or parts.fragment):
            raise ValueError
        if mode == "test" and (host, port, username, database) != (
            "127.0.0.1", 55432, "bd04_test", "mediflow_bd04_test"
        ):
            raise ValueError
        if mode == "development" and database != "mediflow_dev":
            raise ValueError
    except (ValueError, TypeError):
        raise SeedError("destino: URL explícita no autorizada") from None
    return Target(mode, url, host, port, database, username)


def validate_target_declaration(target: Target) -> None:
    expected = parse_target(target.mode, target.url)
    if replace(target, confirmed=False) != expected:
        raise SeedError("destino: declaración incompatible")
    if target.mode == "development" and not target.confirmed:
        raise SeedError("destino: falta confirmación humana")


async def validate_connection(conn: asyncpg.Connection, target: Target) -> None:
    validate_target_declaration(target)
    row = await conn.fetchrow("""SELECT current_database() AS db, current_user AS usr,
        current_schema() AS schema, current_setting('search_path') AS path,
        host(inet_server_addr()) AS address, inet_server_port() AS port""")
    if (row["db"] != target.database or row["usr"] != target.username
        or row["schema"] != "public" or row["path"] not in ('"$user", public', "public")
        or (target.mode == "test" and (
            row["address"] != "127.0.0.1" or row["port"] not in (5432, 55432)))):
        raise SeedError("destino: conexión efectiva no autorizada")


async def validate_schema(conn: asyncpg.Connection) -> None:
    if await conn.fetchval("SELECT version_num FROM public.alembic_version") != SCHEMA_REVISION:
        raise SeedError("esquema: Alembic head incompatible; no se aplican migraciones")
    # Validación read-only de columnas requeridas antes de cualquier DML.
    await conn.fetch("SELECT id, numero_documento, historia_clinica, fecha_nacimiento FROM public.pacientes LIMIT 0")
    await conn.fetch("SELECT id, documento_identidad, password_hash, salt, especialidad_medica FROM public.usuarios LIMIT 0")
    await conn.fetch("SELECT id, documento_id, paciente_id, episodio_id, paciente_edad, metadata FROM public.documentos_triaje LIMIT 0")


def validate_password(password: str | None) -> str:
    from app.api.v1.users import validar_password_segura

    try:
        if not isinstance(password, str):
            raise ValueError
        return validar_password_segura(password)
    except ValueError:
        raise SeedError("credenciales: contraseña ausente o incompatible con la política vigente") from None


def owned_row(
    rows: Sequence[Mapping[str, object]], expected: Mapping[str, object]
) -> Mapping[str, object] | None:
    """Solo UUID + claves + contenido compatible acreditan propiedad, nunca un nombre."""
    if not rows:
        return None
    if len(rows) != 1:
        raise SeedError("conflicto: múltiples identidades incompatibles con BD-04")
    row = rows[0]
    for key, value in expected.items():
        actual = row.get(key)
        if key == "metadata" and isinstance(actual, str):
            try:
                actual = json.loads(actual)
            except ValueError:
                raise SeedError("conflicto: propiedad documental incompatible") from None
        if actual != value:
            raise SeedError("conflicto: registro ajeno o contenido incompatible con BD-04")
    return row


async def seed_hospital_data(
    conn: asyncpg.Connection, passwords: Mapping[str, str], target: Target
) -> SeedResult:
    """Carga explícita; el caller adquiere/cierra conexión. Commit propio y atómico."""
    validate_manifest()
    await validate_connection(conn, target)
    if conn.is_in_transaction():
        raise SeedError("persistencia: la carga requiere su propia transacción")
    from app.core import security

    created = [0, 0, 0]
    async with conn.transaction():
        await conn.execute("SELECT pg_advisory_xact_lock($1::bigint)", LOCK_KEY)
        await validate_schema(conn)
        for p in PATIENTS:
            expected = asdict(p)
            expected.pop("key")
            rows = await conn.fetch("""SELECT * FROM public.pacientes
                WHERE id=$1 OR numero_documento=$2 OR historia_clinica=$3 FOR UPDATE""",
                p.id, p.numero_documento, p.historia_clinica)
            if owned_row(rows, expected) is not None:
                continue
            await conn.execute("""INSERT INTO public.pacientes
                (id, tipo_documento, numero_documento, historia_clinica, nombres,
                 apellidos, fecha_nacimiento) VALUES ($1,$2,$3,$4,$5,$6,$7)""",
                p.id, p.tipo_documento, p.numero_documento, p.historia_clinica,
                p.nombres, p.apellidos, p.fecha_nacimiento)
            created[0] += 1
        for u in USERS:
            expected = asdict(u)
            expected.pop("key")
            rows = await conn.fetch("""SELECT * FROM public.usuarios
                WHERE id=$1 OR documento_identidad=$2 FOR UPDATE""", u.id, u.documento_identidad)
            if owned_row(rows, expected) is not None:
                continue  # no hash, salt, estado o created_at nuevos
            password_hash, salt = security.hash_password(validate_password(passwords.get(u.key)))
            await conn.execute("""INSERT INTO public.usuarios (id, documento_identidad,
                nombres, apellidos, rol, especialidad_medica, password_hash, salt)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""", u.id, u.documento_identidad,
                u.nombres, u.apellidos, u.rol, u.especialidad_medica, password_hash, salt)
            created[1] += 1
        for d in DOCUMENTS:
            expected = dict(id=d.id, documento_id=d.documento_id, paciente_id=d.paciente_id,
                nivel_prioridad=d.nivel_prioridad, tipo_archivo="JSON", canal_origen="Admision",
                status="recibido", metadata=json.loads(METADATA), paciente_edad=None,
                episodio_id=None, destino_principal=None, archivo_original=None,
                resultado_json=None, oci_bucket=None, oci_ruta_objeto=None,
                diagnostico_principal=None, cie10_sugerido=None, score_confianza=None)
            rows = await conn.fetch("""SELECT * FROM public.documentos_triaje
                WHERE id=$1 OR documento_id=$2 FOR UPDATE""", d.id, d.documento_id)
            existing = owned_row(rows, expected)
            inserted = await conn.fetchrow("""INSERT INTO public.documentos_triaje
                (id, documento_id, tipo_archivo, status, paciente_id, nivel_prioridad, metadata)
                VALUES ($1,$2,'JSON','recibido',$3,$4,$5::jsonb)
                ON CONFLICT (documento_id) DO UPDATE SET documento_id=EXCLUDED.documento_id
                WHERE FALSE RETURNING id""", d.id, d.documento_id, d.paciente_id,
                d.nivel_prioridad, METADATA)
            if inserted is None:
                # UPSERT sin actualización no retorna fila. Comprobar también carreras
                # con escritores ajenos que no usan el bloqueo asesor BD-04.
                rows = await conn.fetch("""SELECT * FROM public.documentos_triaje
                    WHERE id=$1 AND documento_id=$2 FOR UPDATE""", d.id, d.documento_id)
                if owned_row(rows, expected) is None:
                    raise SeedError("conflicto: UPSERT sin identidad propia")
            elif existing is None:
                created[2] += 1
    counts = (created[0], created[1], created[2])
    return SeedResult(counts, (10 - counts[0], 4 - counts[1], 5 - counts[2]))


async def development_passwords(
    conn: asyncpg.Connection, passwords: Mapping[str, str]
) -> dict[str, str]:
    """Preflight de solo lectura: claves en memoria solo para cuentas nuevas.

    El caller debe validar antes destino/esquema. El loader vuelve a comprobar
    propiedad bajo su bloqueo transaccional; esta lectura no autoriza escrituras.
    """
    collected = dict(passwords)
    new_users = []
    for user in USERS:
        expected = asdict(user)
        expected.pop("key")
        rows = await conn.fetch("""SELECT * FROM public.usuarios
            WHERE id=$1 OR documento_identidad=$2""", user.id, user.documento_identidad)
        if owned_row(rows, expected) is None:
            new_users.append(user)
    for user in new_users:
        if user.key not in collected:
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                raise SeedError("credenciales: entrada oculta requiere terminal interactiva")
            try:
                with warnings.catch_warnings():
                    # getpass puede recurrir a input visible: abortar antes de leerlo.
                    warnings.simplefilter("error", getpass.GetPassWarning)
                    collected[user.key] = getpass.getpass(f"Contraseña para {user.key}: ")
            except getpass.GetPassWarning:
                raise SeedError("credenciales: no se pudo ocultar la entrada") from None
        validate_password(collected[user.key])
    return collected


async def run_command(target: Target, passwords: Mapping[str, str]) -> SeedResult:
    validate_target_declaration(target)  # también protege llamadas Python directas
    conn = await asyncpg.connect(target.url, timeout=10)
    try:
        if target.mode == "development":
            await validate_connection(conn, target)
            await validate_schema(conn)
            passwords = await development_passwords(conn, passwords)
        return await seed_hospital_data(conn, passwords, target)
    finally:
        await conn.close()


class SafeParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        # argparse normalmente repite argumentos desconocidos (pueden ser secretos).
        self.print_usage(sys.stderr)
        self.exit(2, "entrada: argumentos inválidos; consulte --help\n")


def main(args: Sequence[str] | None = None) -> int:
    parser = SafeParser(description="BD-04: 10 pacientes / 4 médicos / 5 documentos ficticios")
    parser.add_argument("--target", choices=("test", "development"), required=True)
    options = parser.parse_args(args)
    try:
        variable = "BD04_TEST_DATABASE_URL" if options.target == "test" else "DATABASE_URL"
        target = parse_target(options.target, os.environ.get(variable, ""))
        if target.mode == "development":
            if not sys.stdin.isatty() or not sys.stdout.isatty():
                raise SeedError("destino: desarrollo requiere terminal interactiva")
            print(f"Destino: {target.host}:{target.port}/{target.database}")
            if input("Confirme escribiendo mediflow_dev: ") != "mediflow_dev":
                raise SeedError("destino: carga cancelada")
            target = replace(target, confirmed=True)
        passwords = {u.key: os.environ[f"BD04_PASSWORD_{u.key}"] for u in USERS
                     if f"BD04_PASSWORD_{u.key}" in os.environ}
        result = asyncio.run(run_command(target, passwords))
    except SeedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("entrada: carga cancelada", file=sys.stderr)
        return 1
    except Exception:
        print("persistencia: no se completó BD-04; revise conexión/esquema/conflictos", file=sys.stderr)
        return 1
    print(json.dumps({"total": [10, 4, 5], "created": result.created, "reused": result.reused}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
