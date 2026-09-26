"""add_persistent_user_sessions

Revision ID: m6n606300ij2
Revises: l5m505299hi1
"""

from alembic import op


revision = "m6n606300ij2"
down_revision = "l5m505299hi1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """CREATE TABLE sesiones_usuario (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            token_hash CHAR(64) UNIQUE NOT NULL,
            usuario_id UUID NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
            expires_at TIMESTAMPTZ NOT NULL,
            revoked_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );"""
    )
    op.execute(
        "CREATE INDEX ix_sesiones_usuario_usuario_id ON sesiones_usuario (usuario_id);"
    )
    op.execute(
        "CREATE INDEX ix_sesiones_usuario_expires_at ON sesiones_usuario (expires_at);"
    )
    op.execute(
        "COMMENT ON TABLE sesiones_usuario IS 'Sesiones autenticadas revocables y compartidas entre réplicas de MediFlow.';"
    )
    op.execute(
        "COMMENT ON COLUMN sesiones_usuario.id IS 'Identificador UUID de la sesión.';"
    )
    op.execute(
        "COMMENT ON COLUMN sesiones_usuario.token_hash IS 'Hash SHA-256 del token Bearer; el token original nunca se almacena.';"
    )
    op.execute(
        "COMMENT ON COLUMN sesiones_usuario.usuario_id IS 'Usuario propietario de la sesión.';"
    )
    op.execute(
        "COMMENT ON COLUMN sesiones_usuario.expires_at IS 'Fecha y hora de expiración de la sesión.';"
    )
    op.execute(
        "COMMENT ON COLUMN sesiones_usuario.revoked_at IS 'Fecha de revocación; NULL mientras la sesión esté activa.';"
    )
    op.execute(
        "COMMENT ON COLUMN sesiones_usuario.created_at IS 'Fecha y hora de creación de la sesión.';"
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS sesiones_usuario;")
