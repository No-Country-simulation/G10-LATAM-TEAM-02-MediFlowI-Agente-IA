"""add_document_traceability

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


UPGRADE_STATEMENTS = [
    "ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'recibido' BEFORE 'procesado';",
    "ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'procesando' BEFORE 'procesado';",
    "ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'rechazado' BEFORE 'error';",
    "ALTER TYPE status_documento_enum ADD VALUE IF NOT EXISTS 'no_soportado' BEFORE 'error';",
    "ALTER TABLE documentos_triaje ALTER COLUMN status SET DEFAULT 'recibido';",
    "ALTER TABLE cola_procesamiento ALTER COLUMN status SET DEFAULT 'recibido';",
    "ALTER TABLE documentos_triaje ADD COLUMN IF NOT EXISTS usuario_registro_id UUID REFERENCES usuarios(id);",
    "CREATE INDEX IF NOT EXISTS idx_dt_usuario_registro ON documentos_triaje(usuario_registro_id);",
    """DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM auditorias_hitl
            WHERE auditor_id IS NOT NULL
              AND auditor_id !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        ) THEN
            RAISE EXCEPTION 'No se puede migrar auditorias_hitl.auditor_id: existen identidades no UUID';
        END IF;
    END $$;""",
    "ALTER TABLE auditorias_hitl ALTER COLUMN auditor_id TYPE UUID USING auditor_id::UUID;",
    "ALTER TABLE auditorias_hitl ADD CONSTRAINT fk_ahitl_auditor_usuario FOREIGN KEY (auditor_id) REFERENCES usuarios(id);",
    """DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM cola_procesamiento
            WHERE asignado_a IS NOT NULL
              AND asignado_a !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        ) THEN
            RAISE EXCEPTION 'No se puede migrar cola_procesamiento.asignado_a: existen identidades no UUID';
        END IF;
    END $$;""",
    "ALTER TABLE cola_procesamiento ADD COLUMN IF NOT EXISTS asignado_a_usuario_id UUID REFERENCES usuarios(id);",
    "UPDATE cola_procesamiento SET asignado_a_usuario_id = asignado_a::UUID WHERE asignado_a IS NOT NULL;",
    "ALTER TABLE cola_procesamiento DROP COLUMN IF EXISTS asignado_a;",
    "CREATE INDEX IF NOT EXISTS idx_cola_asignado_usuario ON cola_procesamiento(asignado_a_usuario_id);",
    """CREATE TABLE IF NOT EXISTS historial_documento (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        documento_triaje_id UUID NOT NULL REFERENCES documentos_triaje(id) ON DELETE CASCADE,
        usuario_id UUID REFERENCES usuarios(id),
        evento VARCHAR(100) NOT NULL,
        estado_anterior VARCHAR(50),
        estado_nuevo VARCHAR(50),
        descripcion TEXT,
        metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",
    "CREATE INDEX IF NOT EXISTS idx_historial_documento_created ON historial_documento(documento_triaje_id, created_at DESC);",
    "COMMENT ON COLUMN documentos_triaje.usuario_registro_id IS 'Usuario autenticado que registró o cargó el documento.';",
    "COMMENT ON COLUMN auditorias_hitl.auditor_id IS 'UUID del usuario autenticado que tomó la decisión HITL.';",
    "COMMENT ON TABLE cola_procesamiento IS 'Tabla operacional para estado, enrutamiento y asignación de documentos.';",
    "COMMENT ON COLUMN cola_procesamiento.asignado_a_usuario_id IS 'UUID del usuario al que se asignó el documento.';",
    "COMMENT ON TABLE historial_documento IS 'Trazabilidad funcional de eventos y transiciones de cada documento.';",
    "COMMENT ON COLUMN historial_documento.documento_triaje_id IS 'Documento al que pertenece el evento.';",
    "COMMENT ON COLUMN historial_documento.usuario_id IS 'Usuario que originó el evento, si aplica.';",
    "COMMENT ON COLUMN historial_documento.evento IS 'Nombre funcional del evento registrado.';",
    "COMMENT ON COLUMN historial_documento.estado_anterior IS 'Estado del documento antes del evento.';",
    "COMMENT ON COLUMN historial_documento.estado_nuevo IS 'Estado del documento después del evento.';",
    "COMMENT ON COLUMN historial_documento.descripcion IS 'Descripción clínica u operativa del evento.';",
    "COMMENT ON COLUMN historial_documento.metadata IS 'Metadatos estructurados del evento.';",
    "COMMENT ON COLUMN historial_documento.created_at IS 'Fecha y hora de creación del evento.';",
]


DOWNGRADE_STATEMENTS = [
    "DROP TABLE IF EXISTS historial_documento;",
    "ALTER TABLE cola_procesamiento ADD COLUMN IF NOT EXISTS asignado_a VARCHAR(255);",
    "UPDATE cola_procesamiento SET asignado_a = asignado_a_usuario_id::TEXT WHERE asignado_a_usuario_id IS NOT NULL;",
    "ALTER TABLE cola_procesamiento DROP COLUMN IF EXISTS asignado_a_usuario_id;",
    "ALTER TABLE auditorias_hitl DROP CONSTRAINT IF EXISTS fk_ahitl_auditor_usuario;",
    "ALTER TABLE auditorias_hitl ALTER COLUMN auditor_id TYPE VARCHAR(255) USING auditor_id::TEXT;",
    "ALTER TABLE documentos_triaje DROP COLUMN IF EXISTS usuario_registro_id;",
    "ALTER TABLE documentos_triaje ALTER COLUMN status SET DEFAULT 'pendiente_auditoria';",
    "ALTER TABLE cola_procesamiento ALTER COLUMN status SET DEFAULT 'pendiente_auditoria';",
]


def upgrade() -> None:
    for statement in UPGRADE_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    for statement in DOWNGRADE_STATEMENTS:
        op.execute(statement)
