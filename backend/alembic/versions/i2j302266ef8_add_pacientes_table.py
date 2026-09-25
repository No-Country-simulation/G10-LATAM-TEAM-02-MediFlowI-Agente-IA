"""add_pacientes_table

Revision ID: i2j302266ef8
Revises: h1i202255de7
Create Date: 2026-09-25 11:00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'i2j302266ef8'
down_revision: Union[str, Sequence[str], None] = 'h1i202255de7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS pacientes (
        id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tipo_documento          VARCHAR(20) NOT NULL DEFAULT 'DNI',
        numero_documento        VARCHAR(30) UNIQUE NOT NULL,
        historia_clinica        VARCHAR(50) UNIQUE,
        nombres                 VARCHAR(250) NOT NULL,
        apellidos               VARCHAR(250) NOT NULL,
        fecha_nacimiento        DATE,
        sexo                    VARCHAR(20),
        telefono                VARCHAR(50),
        correo                  VARCHAR(250),
        created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",

    "COMMENT ON TABLE pacientes IS 'Tabla maestra de pacientes registrados en el sistema MediFlow';",
    "COMMENT ON COLUMN pacientes.id IS 'Identificador único UUID del paciente';",
    "COMMENT ON COLUMN pacientes.tipo_documento IS 'Tipo de documento oficial (DNI, CE, PASAPORTE)';",
    "COMMENT ON COLUMN pacientes.numero_documento IS 'Número único de documento de identidad del paciente';",
    "COMMENT ON COLUMN pacientes.historia_clinica IS 'Número de historia clínica del paciente';",
    "COMMENT ON COLUMN pacientes.nombres IS 'Nombres del paciente';",
    "COMMENT ON COLUMN pacientes.apellidos IS 'Apellidos paterno y materno del paciente';",
    "COMMENT ON COLUMN pacientes.fecha_nacimiento IS 'Fecha de nacimiento del paciente (AAAA-MM-DD)';",
    "COMMENT ON COLUMN pacientes.sexo IS 'Sexo/Género del paciente (M, F, OTRO)';",
    "COMMENT ON COLUMN pacientes.telefono IS 'Teléfono principal de contacto del paciente';",
    "COMMENT ON COLUMN pacientes.correo IS 'Correo electrónico de contacto del paciente';",
    "COMMENT ON COLUMN pacientes.created_at IS 'Fecha y hora de creación del registro';",
    "COMMENT ON COLUMN pacientes.updated_at IS 'Fecha y hora de última actualización del registro';",

    "ALTER TABLE documentos_triaje ADD COLUMN IF NOT EXISTS paciente_id UUID REFERENCES pacientes(id) ON DELETE SET NULL;",
    "COMMENT ON COLUMN documentos_triaje.paciente_id IS 'Identificador FK del paciente asociado en la tabla de pacientes';",

    "CREATE INDEX IF NOT EXISTS idx_pacientes_numero_doc ON pacientes(numero_documento);",
    "CREATE INDEX IF NOT EXISTS idx_pacientes_historia_clinica ON pacientes(historia_clinica);",
    "CREATE INDEX IF NOT EXISTS idx_pacientes_nombres_apellidos ON pacientes(nombres, apellidos);"
]

DOWNGRADE_STATEMENTS = [
    "ALTER TABLE documentos_triaje DROP COLUMN IF EXISTS paciente_id;",
    "DROP TABLE IF EXISTS pacientes CASCADE;"
]


def upgrade() -> None:
    for stmt in UPGRADE_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DOWNGRADE_STATEMENTS:
        op.execute(stmt)
