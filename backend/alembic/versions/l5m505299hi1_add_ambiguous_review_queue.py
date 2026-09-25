"""add_ambiguous_review_queue

Revision ID: l5m505299hi1
Revises: k4l404288gh0
"""

from alembic import op


revision = "l5m505299hi1"
down_revision = "k4l404288gh0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE destino_enum ADD VALUE IF NOT EXISTS 'Cola_Revision_Ambigua';")
    op.execute(
        "COMMENT ON TYPE destino_enum IS "
        "'Colas operativas: emergencia, rutina, auditoría humana y revisión ambigua.';"
    )


def downgrade() -> None:
    # PostgreSQL no permite eliminar valores individuales de un ENUM sin recrearlo.
    pass
