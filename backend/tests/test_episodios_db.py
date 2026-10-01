"""
MediFlow — Tests unitarios para la vista relacional v_episodios_detalle.

Valida la generación de DDL offline con Alembic y la estructura de la consulta
agregada sin mutar la base de datos de desarrollo (Regla de Oro de MediFlow).
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
OFFLINE_ENV = {
    **os.environ,
    "DATABASE_URL": "postgresql+asyncpg://test:test@localhost/mediflow_test",
}


def _load_migration():
    migration_file = BACKEND_DIR / "alembic" / "versions" / "p9q909633lm5_add_v_episodios_detalle_view.py"
    spec = importlib.util.spec_from_file_location("migration_v_episodios_detalle", migration_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_upgrade_sql_creates_v_episodios_detalle_view():
    """Valida que la migración Alembic genera la sentencia CREATE OR REPLACE VIEW v_episodios_detalle."""
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_DIR,
        env=OFFLINE_ENV,
        text=True,
        capture_output=True,
        check=True,
    )

    sql = result.stdout
    assert "CREATE OR REPLACE VIEW v_episodios_detalle" in sql
    assert "COMMENT ON VIEW v_episodios_detalle" in sql


def test_vista_sql_contains_required_fields_and_dynamic_age():
    """Valida que la vista proyecte los campos clínicos, cálculo dinámico de edad y profesionales."""
    migration = _load_migration()
    UPGRADE_STATEMENTS = migration.UPGRADE_STATEMENTS
    DOWNGRADE_STATEMENTS = migration.DOWNGRADE_STATEMENTS

    create_view_sql = UPGRADE_STATEMENTS[0]

    # Columnas del Episodio
    assert "e.id AS episodio_id" in create_view_sql
    assert "e.codigo_episodio" in create_view_sql
    assert "e.estado_atencion" in create_view_sql
    assert "e.nivel_prioridad" in create_view_sql
    assert "e.motivo_consulta" in create_view_sql
    assert "e.diagnostico_general" in create_view_sql
    assert "e.diagnostico_especialista" in create_view_sql
    assert "e.especialidad_requerida" in create_view_sql

    # Columnas del Paciente
    assert "p.id AS paciente_id" in create_view_sql
    assert "p.numero_documento AS paciente_numero_documento" in create_view_sql
    assert "p.historia_clinica AS paciente_historia_clinica" in create_view_sql
    assert "TRIM(CONCAT(p.nombres, ' ', p.apellidos)) AS paciente_nombre_completo" in create_view_sql
    assert "EXTRACT(YEAR FROM age(CURRENT_DATE, p.fecha_nacimiento))::INT" in create_view_sql
    assert "AS paciente_edad" in create_view_sql
    assert "p.genero AS paciente_genero" in create_view_sql
    assert "p.numero_telefono AS paciente_numero_telefono" in create_view_sql

    # Profesionales Asignados (Operador, Médico General y Especialista)
    assert "TRIM(CONCAT(op.nombres, ' ', op.apellidos)) AS operador_ingreso_nombre" in create_view_sql
    assert "TRIM(CONCAT(mg.nombres, ' ', mg.apellidos)) AS medico_general_nombre" in create_view_sql
    assert "mg.especialidad_medica AS medico_general_especialidad" in create_view_sql
    assert "TRIM(CONCAT(me.nombres, ' ', me.apellidos)) AS medico_especialista_nombre" in create_view_sql
    assert "me.especialidad_medica AS medico_especialista_especialidad" in create_view_sql

    # Relaciones LEFT JOIN
    assert "LEFT JOIN pacientes p ON e.paciente_id = p.id" in create_view_sql
    assert "LEFT JOIN usuarios op ON e.operador_ingreso_id = op.id" in create_view_sql
    assert "LEFT JOIN usuarios mg ON e.medico_general_id = mg.id" in create_view_sql
    assert "LEFT JOIN usuarios me ON e.medico_especialista_id = me.id" in create_view_sql

    # Downgrade
    assert "DROP VIEW IF EXISTS v_episodios_detalle CASCADE;" in DOWNGRADE_STATEMENTS[0]
