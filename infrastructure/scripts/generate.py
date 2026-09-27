#!/usr/bin/env python3
"""Genera Pydantic v2 y TypeScript desde el mismo contrato validado."""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from sdd import ROOT, SPEC, bundle_spec, node_command, run, validate_bundle


def generate(output_root: Path = ROOT, spec: Path = SPEC, check: bool = False) -> None:
    # Ambas herramientas deben terminar antes de publicar cualquiera de las salidas.
    with tempfile.TemporaryDirectory(prefix="mediflow-generate-") as directory:
        stage = Path(directory)
        bundle = stage / "openapi.json"
        bundle_spec(bundle, spec)
        validate_bundle(bundle)
        run(
            [
                sys.executable,
                "-m",
                "datamodel_code_generator",
                "--input",
                str(bundle),
                "--input-file-type",
                "openapi",
                "--output",
                str(stage / "models.py"),
                "--output-model-type",
                "pydantic_v2.BaseModel",
                "--target-python-version",
                "3.11",
                "--encoding",
                "utf-8",
                "--use-standard-collections",
                "--use-union-operator",
                "--field-constraints",
                "--enum-field-as-literal",
                "all",
                "--disable-timestamp",
                "--strict-nullable",
                "--custom-file-header",
                "# AUTO-GENERADO desde specs/openapi.yaml. NO EDITAR.\n# Ejecutar make generate.",
            ]
        )
        run(
            node_command(
                ROOT / "node_modules/openapi-typescript/bin/cli.js",
                str(bundle),
                "--output",
                str(stage / "types.ts"),
                "--default-non-nullable",
                "false",
            )
        )
        schemas = json.loads(bundle.read_text(encoding="utf-8"))["components"]["schemas"]
        barrel = "// AUTO-GENERADO desde specs/openapi.yaml. NO EDITAR.\n"
        barrel += "import type { components } from './types'\nexport type * from './types'\n"
        for name in schemas:
            barrel += f"export type {name} = components['schemas']['{name}']\n"
        outputs = {
            Path("backend/app/_generated/models.py"): (stage / "models.py").read_text(encoding="utf-8").encode("utf-8"),
            Path(
                "backend/app/_generated/__init__.py"
            ): b'"""Modelos generados desde OpenAPI; ver models.py."""\n',
            Path("frontend/src/_generated/api/types.ts"): (stage / "types.ts").read_text(encoding="utf-8").encode("utf-8"),
            Path("frontend/src/_generated/api/index.ts"): barrel.encode("utf-8"),
        }
        compile(outputs[Path("backend/app/_generated/models.py")], "models.py", "exec")
        run(
            node_command(
                ROOT / "node_modules/typescript/bin/tsc",
                "--noEmit",
                "--strict",
                "--skipLibCheck",
                str(stage / "types.ts"),
            )
        )
        publish(outputs, output_root, check)


def publish(outputs: dict[Path, bytes], output_root: Path, check: bool) -> None:
    previous = {
        path: (output_root / path).read_bytes() if (output_root / path).exists() else None
        for path in outputs
    }
    changed = [path for path, data in outputs.items() if previous[path] != data]
    if check:
        if changed:
            raise RuntimeError("Tipos desactualizados: " + ", ".join(map(str, changed)))
        print("Los tipos versionados coinciden con la generación actual.")
        return
    written = []
    try:
        for path in changed:
            target = output_root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            written.append(path)
            target.write_bytes(outputs[path])
    except OSError:
        for path in reversed(written):
            target = output_root / path
            if previous[path] is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(previous[path])
        raise
    print(f"Generación real completada: {len(outputs)} archivos; {len(changed)} actualizados.")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--spec", type=Path, default=SPEC)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        generate(args.output_root.resolve(), args.spec.resolve(), args.check)
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"Generación fallida: {exc}", file=sys.stderr)
        sys.exit(1)
