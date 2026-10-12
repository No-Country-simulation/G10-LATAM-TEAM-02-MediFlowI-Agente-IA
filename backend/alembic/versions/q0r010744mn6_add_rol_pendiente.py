"""add_rol_pendiente

Revision ID: q0r010744mn6
Revises: p9q909633lm5
Create Date: 2026-10-12 12:00:00

Agrega el rol PENDIENTE al enum rol_enum para dar soporte a solicitudes
de acceso de nuevos usuarios a la espera de asignación de rol por el administrador.
"""

from typing import Sequence, Union
from alembic import op

revision: str = "q0r010744mn6"
down_revision: Union[str, Sequence[str], None] = "p9q909633lm5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UPGRADE_STATEMENTS = [
    "ALTER TYPE rol_enum ADD VALUE IF NOT EXISTS 'PENDIENTE';",
]


def upgrade() -> None:
    for stmt in UPGRADE_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    # PostgreSQL no permite remover valores de un ENUM de manera directa sin recrearlo.
    pass
