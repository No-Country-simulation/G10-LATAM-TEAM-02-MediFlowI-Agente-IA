"""add_document_statuses

Revision ID: j3k303277fg9
Revises: i2j302266ef8
Create Date: 2026-09-25 15:00:00
"""

from typing import Sequence, Union

from alembic import op


revision: str = "j3k303277fg9"
down_revision: Union[str, Sequence[str], None] = "i2j302266ef8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Agrega valores de enum en una transacción propia antes de utilizarlos."""
    op.execute("ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'recibido' BEFORE 'procesado';")
    op.execute("ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'procesando' BEFORE 'procesado';")
    op.execute("ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'rechazado' BEFORE 'error';")
    op.execute("ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'no_soportado' BEFORE 'error';")


def downgrade() -> None:
    """PostgreSQL no permite retirar valores de un ENUM de forma segura."""
    pass
