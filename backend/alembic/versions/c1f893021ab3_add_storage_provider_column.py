"""add_storage_provider_column

Revision ID: c1f893021ab3
Revises: 6bf254b9874e
Create Date: 2026-09-24 21:12:00

"""
from collections.abc import Sequence

from alembic import op

revision: str = 'c1f893021ab3'
down_revision: str | Sequence[str] | None = '6bf254b9874e'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Agrega la columna storage_provider a documentos_triaje."""
    op.execute("""
    ALTER TABLE documentos_triaje 
    ADD COLUMN IF NOT EXISTS storage_provider VARCHAR(50) NOT NULL DEFAULT 'LOCAL';
    """)


def downgrade() -> None:
    """Elimina la columna storage_provider."""
    op.execute("ALTER TABLE documentos_triaje DROP COLUMN IF EXISTS storage_provider;")
