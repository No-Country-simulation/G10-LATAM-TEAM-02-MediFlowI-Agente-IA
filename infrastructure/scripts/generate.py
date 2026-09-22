#!/usr/bin/env python3
"""
MediFlow — Script SDD: Genera código desde specs/openapi.yaml

Uso: python infrastructure/scripts/generate.py
     make generate

Genera:
  - backend/app/_generated/models.py       (Pydantic models)
  - backend/app/_generated/routers/        (endpoint stubs)
  - frontend/src/_generated/api/           (TypeScript client)
"""

import subprocess
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
SPEC_FILE = ROOT / "specs" / "openapi.yaml"
BACKEND_GEN = ROOT / "backend" / "app" / "_generated"
FRONTEND_GEN = ROOT / "frontend" / "src" / "_generated" / "api"


def log(msg: str, ok: bool = True):
    icon = "✅" if ok else "❌"
    print(f"{icon} {msg}")


def verificar_spec():
    if not SPEC_FILE.exists():
        log(f"No se encontró {SPEC_FILE}", ok=False)
        sys.exit(1)
    log(f"Spec encontrado: {SPEC_FILE}")


def generar_backend_pydantic():
    """
    Genera modelos Pydantic desde el spec usando datamodel-code-generator.
    Instalar: pip install datamodel-code-generator
    """
    BACKEND_GEN.mkdir(parents=True, exist_ok=True)
    output_file = BACKEND_GEN / "models.py"

    try:
        resultado = subprocess.run(
            [
                "datamodel-codegen",
                "--input", str(SPEC_FILE),
                "--input-file-type", "openapi",
                "--output", str(output_file),
                "--use-annotated",
                "--target-python-version", "3.11",
                "--field-constraints",
            ],
            capture_output=True, text=True, timeout=60,
        )
        if resultado.returncode == 0:
            log(f"Backend models generados: {output_file}")
        else:
            log(f"datamodel-codegen falló: {resultado.stderr}", ok=False)
            log("Generando stub manual...", ok=True)
            _generar_stub_models(output_file)
    except FileNotFoundError:
        log("datamodel-codegen no instalado. Generando stub manual.", ok=True)
        _generar_stub_models(output_file)


def _generar_stub_models(output_file: Path):
    """Genera un stub básico de models.py si datamodel-codegen no está disponible."""
    stub = '''# AUTO-GENERADO — NO EDITAR MANUALMENTE
# Ejecutar `make generate` para regenerar desde specs/openapi.yaml
# Para generación completa, instalar: pip install datamodel-code-generator

"""
Stub de modelos generados desde specs/openapi.yaml.
En producción, usar datamodel-codegen para generar modelos completos.
"""

from pydantic import BaseModel
from typing import Optional, Literal, List

# Importar modelos completos desde app.agent.state
# (los modelos manuales son la fuente de verdad hasta que se instale datamodel-codegen)
from app.agent.state import AgentState, DatosExtraidosState, ClasificacionState
'''
    output_file.write_text(stub, encoding="utf-8")
    log(f"Stub generado: {output_file}")


def generar_frontend_typescript():
    """
    Genera cliente TypeScript desde el spec usando @hey-api/openapi-ts.
    Requiere Node.js y npx.
    """
    FRONTEND_GEN.mkdir(parents=True, exist_ok=True)

    try:
        resultado = subprocess.run(
            [
                "npx", "--yes", "@hey-api/openapi-ts",
                "--input", str(SPEC_FILE),
                "--output", str(FRONTEND_GEN),
                "--client", "fetch",
            ],
            capture_output=True, text=True, timeout=60,
            cwd=ROOT / "frontend",
        )
        if resultado.returncode == 0:
            log(f"Frontend TypeScript client generado: {FRONTEND_GEN}")
        else:
            log(f"@hey-api/openapi-ts falló: {resultado.stderr[:200]}", ok=False)
            _generar_stub_typescript()
    except FileNotFoundError:
        log("npx no disponible. Generando stub TypeScript.", ok=True)
        _generar_stub_typescript()


def _generar_stub_typescript():
    """Genera un stub de types.ts si openapi-ts no está disponible."""
    stub_types = FRONTEND_GEN / "types.ts"
    stub_types.parent.mkdir(parents=True, exist_ok=True)
    stub_types.write_text(
        "// AUTO-GENERADO — NO EDITAR MANUALMENTE\n"
        "// Ejecutar `make generate` con Node.js instalado para generar tipos completos\n"
        "// Los tipos manuales están en: frontend/src/api/triage.api.ts\n",
        encoding="utf-8",
    )
    log(f"Stub TypeScript generado: {stub_types}")


def main():
    print("🚀 MediFlow SDD — Generando código desde spec...\n")
    verificar_spec()
    generar_backend_pydantic()
    generar_frontend_typescript()
    print("\n✅ Generación completada. Revisa los archivos _generated/ antes de continuar.")


if __name__ == "__main__":
    main()
