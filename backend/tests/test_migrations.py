"""Verificaciones de la salida SQL de las migraciones Alembic."""

from pathlib import Path
import subprocess
import sys


BACKEND_DIR = Path(__file__).resolve().parents[1]


def test_upgrade_sql_creates_document_traceability_schema():
    """La migración publicada debe crear historial y estados operacionales."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_DIR,
        text=True,
        capture_output=True,
        check=True,
    )

    sql = result.stdout
    assert "CREATE TABLE IF NOT EXISTS historial_documento" in sql
    assert "usuario_registro_id UUID" in sql
    assert "asignado_a_usuario_id UUID" in sql
    assert "ADD VALUE IF NOT EXISTS 'rechazado'" in sql
