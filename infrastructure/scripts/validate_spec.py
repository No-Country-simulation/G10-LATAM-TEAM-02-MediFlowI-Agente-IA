#!/usr/bin/env python3
"""Valida el contrato completo con Spectral; nunca sustituye lint por parseo YAML."""

import subprocess
import sys
import tempfile
from pathlib import Path

from sdd import bundle_spec, validate_bundle


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mediflow-validate-") as directory:
        bundle = Path(directory) / "openapi.json"
        bundle_spec(bundle)
        validate_bundle(bundle)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        main()
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"Validación fallida: {exc}", file=sys.stderr)
        sys.exit(1)
