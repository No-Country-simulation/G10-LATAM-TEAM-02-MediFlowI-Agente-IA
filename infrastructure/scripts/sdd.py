"""Herramientas del contrato. Sin descargas implícitas ni fallback a archivos antiguos."""

import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "specs/openapi.yaml"


def node_command(script: Path, *args: str) -> list[str]:
    node = shutil.which(os.environ.get("NODE_BINARY", "node"))
    if not node:
        raise RuntimeError("Falta Node.js >=22 en PATH (o define NODE_BINARY).")
    if not script.is_file():
        raise RuntimeError(f"Falta {script.name}. Ejecuta npm ci en la raíz del repositorio.")
    return [node, str(script), *map(str, args)]


def run(command: list[str]) -> None:
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Falló {Path(command[0]).name}:\n{result.stdout}\n{result.stderr}")


def bundle_spec(output: Path, spec: Path = SPEC) -> None:
    run(node_command(ROOT / "infrastructure/scripts/bundle_spec.mjs", str(spec), str(output)))


def validate_bundle(bundle: Path) -> None:
    # El bundling evita la incompatibilidad con referencias externas de Path Items
    # en Spectral 6.15 / OAS 3.1; conserva todos los componentes del contrato.
    command = node_command(
        ROOT / "node_modules/@stoplight/spectral-cli/dist/index.js",
        "lint",
        str(bundle),
        "--ruleset",
        str(ROOT / ".spectral.yaml"),
        "--format",
        "json",
    )
    result = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
        check=False,
    )
    try:
        diagnostics = json.loads(result.stdout)
    except ValueError as exc:
        raise RuntimeError(
            f"Spectral no pudo ejecutarse:\n{result.stderr}\n{result.stdout}"
        ) from exc
    errors = [item for item in diagnostics if item["severity"] == 0]
    warnings = [item for item in diagnostics if item["severity"] == 1]
    for item in errors + warnings:
        print(f"{item['code']}: {'.'.join(map(str, item['path']))}: {item['message']}")
    print(f"Spectral: {len(errors)} errores, {len(warnings)} advertencias.")
    if result.returncode or errors:
        raise RuntimeError("El contrato no pasó Spectral.")
