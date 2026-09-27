"""Prueba la cadena SDD real y sus fallos sin escribir en las salidas del repositorio."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "infrastructure/scripts"))
import generate  # noqa: E402 -- scripts CLI importados desde su directorio.
import sdd  # noqa: E402


def test_generation_from_empty_directory_is_reproducible_and_tracks_spec(tmp_path):
    output = tmp_path / "output"
    generate.generate(output)
    first = {p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()}
    assert len(first) == 4
    probe = output / "typecheck.ts"
    probe.write_text(
        """import type { DocumentoClinico, Clasificacion, DatosExtraidos } from './frontend/src/_generated/api'
const minimal: DocumentoClinico = { documento_id: 'X', tipo_archivo: 'PDF', documento_texto: null }
const nullable: DatosExtraidos = { paciente: null }
// @ts-expect-error El enum del contrato no admite texto arbitrario.
const invalid: Clasificacion['tipo_documento'] = 'FACTURA'
// @ts-expect-error documento_id es obligatorio.
const missing: DocumentoClinico = { tipo_archivo: 'PDF' }
// @ts-expect-error canal_origen es opcional pero no acepta null.
const nullChannel: DocumentoClinico = { documento_id: 'X', tipo_archivo: 'PDF', canal_origen: null }
""",
        encoding="utf-8",
    )
    sdd.run(
        sdd.node_command(
            ROOT / "node_modules/typescript/bin/tsc",
            "--noEmit",
            "--strict",
            "--skipLibCheck",
            str(probe),
        )
    )
    probe.unlink()
    generate.generate(output, check=True)
    assert first == {
        p.relative_to(output): p.read_bytes() for p in output.rglob("*") if p.is_file()
    }
    # Una modificación del contrato debe llegar a ambos lenguajes, no usar el fallback.
    bundle = tmp_path / "changed.json"
    sdd.bundle_spec(bundle)
    document = json.loads(bundle.read_text(encoding="utf-8"))
    document["components"]["schemas"]["DocumentoClinico"]["properties"]["revision_prueba"] = {
        "type": "string",
        "description": "Campo sintético para verificar regeneración.",
    }
    bundle.write_text(json.dumps(document), encoding="utf-8")
    generate.generate(output, spec=bundle)
    for relative in ["backend/app/_generated/models.py", "frontend/src/_generated/api/types.ts"]:
        assert "revision_prueba" in (output / relative).read_text(encoding="utf-8")
    module_spec = importlib.util.spec_from_file_location(
        "generated_probe", output / "backend/app/_generated/models.py"
    )
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    try:
        module_spec.loader.exec_module(module)
        assert (
            module.DocumentoClinico(
                documento_id="TEST", tipo_archivo="PDF", revision_prueba="v2"
            ).revision_prueba
            == "v2"
        )
    finally:
        sys.modules.pop(module_spec.name, None)


@pytest.mark.parametrize("failure", ["datamodel_code_generator", "cli.js"])
def test_tool_failure_preserves_existing_outputs(tmp_path, monkeypatch, failure):
    files = ["backend/app/_generated/models.py", "frontend/src/_generated/api/types.ts"]
    for name in files:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("contenido anterior", encoding="utf-8")
    real_run = generate.run

    def failing_run(command):
        if any(failure in str(argument) for argument in command):
            raise RuntimeError("fallo de herramienta simulado")
        real_run(command)

    monkeypatch.setattr(generate, "run", failing_run)
    with pytest.raises(RuntimeError, match="simulado"):
        generate.generate(tmp_path)
    assert all(
        (tmp_path / name).read_text(encoding="utf-8") == "contenido anterior" for name in files
    )


def test_missing_node_is_an_error(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda _: None)
    with pytest.raises(RuntimeError, match="Falta Node"):
        sdd.node_command(ROOT / "infrastructure/scripts/bundle_spec.mjs")


def test_cli_reports_missing_tool_with_nonzero_exit(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "infrastructure/scripts/generate.py"),
            "--output-root",
            str(tmp_path),
        ],
        env={**os.environ, "NODE_BINARY": "mediflow-nonexistent-node"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert result.returncode != 0
    assert "Falta Node" in result.stderr
    assert not (tmp_path / "backend/app/_generated/models.py").exists()


@pytest.mark.parametrize("mutation", ["reference", "score", "operation", "nullable", "security"])
def test_invalid_contract_fails_validation(tmp_path, mutation):
    bundle = tmp_path / "openapi.json"
    sdd.bundle_spec(bundle)
    document = json.loads(bundle.read_text(encoding="utf-8"))
    if mutation == "reference":
        document["paths"]["/triage"]["post"]["requestBody"]["content"]["application/json"][
            "schema"
        ] = {"$ref": "#/components/schemas/Missing"}
    elif mutation == "score":
        del document["components"]["schemas"]["Clasificacion"]["properties"][
            "score_confianza_clasificacion"
        ]["maximum"]
    elif mutation == "operation":
        del document["paths"]["/triage"]["post"]["operationId"]
    elif mutation == "nullable":
        document["components"]["schemas"]["DocumentoClinico"]["properties"]["documento_texto"][
            "nullable"
        ] = True
    else:
        document["security"] = []
    bundle.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(RuntimeError, match="Spectral"):
        sdd.validate_bundle(bundle)
