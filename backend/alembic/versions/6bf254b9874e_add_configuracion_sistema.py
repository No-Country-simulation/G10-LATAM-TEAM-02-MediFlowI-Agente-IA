"""add_configuracion_sistema

Revision ID: 6bf254b9874e
Revises: a3eb75cf454e
Create Date: 2026-09-24 20:55:29

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bf254b9874e'
down_revision: Union[str, Sequence[str], None] = 'a3eb75cf454e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crea la tabla configuracion_sistema e inserta el modo de almacenamiento inicial."""
    op.execute("""
    CREATE TABLE IF NOT EXISTS configuracion_sistema (
        clave VARCHAR(100) PRIMARY KEY,
        valor VARCHAR(500) NOT NULL,
        descripcion TEXT,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """)
    op.execute("""
    INSERT INTO configuracion_sistema (clave, valor, descripcion) VALUES
    ('modo_almacenamiento', 'LOCAL', 'Modo de almacenamiento activo: LOCAL u OCI')
    ON CONFLICT (clave) DO NOTHING;
    """)


def downgrade() -> None:
    """Elimina la tabla configuracion_sistema."""
    op.execute("DROP TABLE IF EXISTS configuracion_sistema CASCADE;")
