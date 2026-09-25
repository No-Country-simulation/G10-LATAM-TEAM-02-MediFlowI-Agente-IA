"""add_nombre_original_column

Revision ID: f8g990032bc5
Revises: e7f893021ab4
Create Date: 2026-09-24 21:41:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f8g990032bc5'
down_revision: Union[str, Sequence[str], None] = 'e7f893021ab4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega la columna nombre_original a documentos_triaje."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    ADD COLUMN IF NOT EXISTS nombre_original VARCHAR(500);
    """)


def downgrade() -> None:
    """Elimina la columna nombre_original."""
    op.execute("ALTER TABLE documentos_triaje DROP COLUMN IF EXISTS nombre_original;")
