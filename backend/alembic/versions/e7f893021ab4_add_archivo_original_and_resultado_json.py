"""add_archivo_original_and_resultado_json

Revision ID: e7f893021ab4
Revises: c1f893021ab3
Create Date: 2026-09-24 21:28:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'e7f893021ab4'
down_revision: Union[str, Sequence[str], None] = 'c1f893021ab3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega las columnas archivo_original y resultado_json a documentos_triaje."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    ADD COLUMN IF NOT EXISTS archivo_original VARCHAR(1000),
    ADD COLUMN IF NOT EXISTS resultado_json VARCHAR(1000);
    """)


def downgrade() -> None:
    """Elimina las columnas archivo_original y resultado_json."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    DROP COLUMN IF EXISTS archivo_original,
    DROP COLUMN IF EXISTS resultado_json;
    """)
