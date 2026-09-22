#!/usr/bin/env python3
"""
MediFlow — Script SDD: Valida specs/openapi.yaml con Spectral.

Uso: python infrastructure/scripts/validate_spec.py
     make validate
"""

import subprocess
import sys
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SPEC_FILE = ROOT / "specs" / "openapi.yaml"


def validar_con_spectral():
    """Valida el spec con Spectral CLI (linter OpenAPI)."""
    print("🔍 Validando specs/openapi.yaml con Spectral...\n")

    try:
        resultado = subprocess.run(
            ["npx", "--yes", "@stoplight/spectral-cli", "lint", str(SPEC_FILE)],
            capture_output=False,
            timeout=60,
        )
        if resultado.returncode == 0:
            print("\n✅ Spec válido — sin errores de linting")
        else:
            print("\n⚠️  Spectral encontró problemas. Revisa los errores arriba.")
            sys.exit(1)
    except FileNotFoundError:
        print("⚠️  npx no disponible. Validación básica con PyYAML...")
        validar_yaml_basico()


def validar_yaml_basico():
    """Validación mínima: parsear el YAML sin errores."""
    try:
        import yaml
        with open(SPEC_FILE, encoding="utf-8") as f:
            spec = yaml.safe_load(f)

        # Verificaciones mínimas OpenAPI
        assert spec.get("openapi", "").startswith("3."), "Debe ser OpenAPI 3.x"
        assert "info" in spec, "Falta campo 'info'"
        assert "paths" in spec, "Falta campo 'paths'"

        print(f"✅ YAML válido: OpenAPI {spec['openapi']}")
        print(f"   Título: {spec['info'].get('title')}")
        print(f"   Paths: {list(spec['paths'].keys())}")

    except ImportError:
        print("⚠️  PyYAML no instalado. Instala con: pip install pyyaml")
        sys.exit(1)
    except AssertionError as e:
        print(f"❌ Spec inválido: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al parsear YAML: {e}")
        sys.exit(1)


if __name__ == "__main__":
    validar_con_spectral()
