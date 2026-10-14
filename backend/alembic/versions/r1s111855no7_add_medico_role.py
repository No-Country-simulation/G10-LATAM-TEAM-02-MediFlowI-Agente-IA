"""Añade MEDICO al enum existente para sesiones clínicas y alertas IA-08.

Revision ID: r1s111855no7
Revises: q0r010744mn6
"""

from alembic import op

revision = "r1s111855no7"
down_revision = "q0r010744mn6"
branch_labels = None
depends_on = None

UPGRADE_STATEMENTS = [
    "ALTER TYPE rol_enum ADD VALUE IF NOT EXISTS 'MEDICO';",
    "COMMENT ON TYPE rol_enum IS 'Roles de acceso hospitalario, incluido MEDICO para atención clínica y alertas de guardia.';",
]


def upgrade() -> None:
    for statement in UPGRADE_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    # PostgreSQL no permite quitar un valor ENUM sin recrear el tipo y arriesgar
    # los usuarios existentes. Se conserva MEDICO, igual que COORDINADOR/PENDIENTE.
    pass
