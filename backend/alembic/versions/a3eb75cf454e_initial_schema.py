"""initial_schema

Revision ID: a3eb75cf454e
Revises: 
Create Date: 2026-09-24 20:43:53.396004

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3eb75cf454e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UPGRADE_STATEMENTS = [
    'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
    'CREATE EXTENSION IF NOT EXISTS "pg_trgm";',
    'CREATE EXTENSION IF NOT EXISTS "unaccent";',

    "DO $$ BEGIN CREATE TYPE tipo_archivo_enum AS ENUM ('PDF', 'IMAGEN', 'TEXTO', 'JSON'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "DO $$ BEGIN CREATE TYPE nivel_prioridad_enum AS ENUM ('Urgente', 'Rutina', 'Ambiguo'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "DO $$ BEGIN CREATE TYPE status_documento_enum AS ENUM ('procesado', 'error', 'pendiente_auditoria'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "DO $$ BEGIN CREATE TYPE destino_enum AS ENUM ('Cola_Emergencia_Medica', 'Cola_Rutina', 'Cola_Auditoria_Humana'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "DO $$ BEGIN CREATE TYPE status_oci_enum AS ENUM ('exito', 'error', 'pendiente'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "DO $$ BEGIN CREATE TYPE decision_auditoria_enum AS ENUM ('aprobar', 'rechazar', 'reclasificar'); EXCEPTION WHEN duplicate_object THEN null; END $$;",

    """CREATE TABLE IF NOT EXISTS documentos_triaje (
        id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        documento_id                VARCHAR(255) UNIQUE NOT NULL,
        tipo_archivo                tipo_archivo_enum NOT NULL,
        canal_origen                VARCHAR(255) NOT NULL DEFAULT '',
        status                      status_documento_enum NOT NULL DEFAULT 'pendiente_auditoria',
        texto_extraido              TEXT,
        tipo_documento              VARCHAR(255),
        especialidad                VARCHAR(255),
        nivel_prioridad             nivel_prioridad_enum,
        score_confianza             FLOAT CHECK (score_confianza >= 0 AND score_confianza <= 1),
        paciente_nombre             VARCHAR(500),
        paciente_edad               SMALLINT CHECK (paciente_edad > 0 AND paciente_edad < 150),
        paciente_id_externo         VARCHAR(255),
        medico_nombre               VARCHAR(500),
        medico_matricula            VARCHAR(100),
        estudio_realizado           TEXT,
        diagnostico_principal       TEXT,
        cie10_sugerido              VARCHAR(20),
        hallazgos_clave             JSONB DEFAULT '[]'::JSONB,
        destino_principal           destino_enum,
        requiere_auditoria_humana   BOOLEAN NOT NULL DEFAULT FALSE,
        justificacion_enrutamiento  TEXT,
        notificacion_generada       JSONB,
        oci_bucket                  VARCHAR(255),
        oci_ruta_objeto             VARCHAR(1000),
        oci_status                  status_oci_enum DEFAULT 'pendiente',
        nodos_ejecutados            JSONB DEFAULT '[]'::JSONB,
        tiempo_procesamiento_ms     INTEGER,
        metadata                    JSONB DEFAULT '{}'::JSONB,
        error_mensaje               TEXT,
        created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",

    """CREATE TABLE IF NOT EXISTS auditorias_hitl (
        id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        documento_triaje_id         UUID NOT NULL REFERENCES documentos_triaje(id) ON DELETE CASCADE,
        documento_id                VARCHAR(255) NOT NULL,
        decision                    decision_auditoria_enum NOT NULL,
        auditor_id                  VARCHAR(255) NOT NULL,
        comentario                  TEXT,
        nueva_nivel_prioridad       nivel_prioridad_enum,
        nuevo_destino               destino_enum,
        nuevo_tipo_documento        VARCHAR(255),
        created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",

    """CREATE TABLE IF NOT EXISTS notificaciones (
        id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        documento_triaje_id         UUID NOT NULL REFERENCES documentos_triaje(id) ON DELETE CASCADE,
        documento_id                VARCHAR(255) NOT NULL,
        canal                       VARCHAR(255) NOT NULL,
        mensaje                     TEXT NOT NULL,
        enviada                     BOOLEAN NOT NULL DEFAULT FALSE,
        error_envio                 TEXT,
        created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        enviada_at                  TIMESTAMPTZ
    );""",

    """CREATE TABLE IF NOT EXISTS cola_procesamiento (
        id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        documento_id                VARCHAR(255) UNIQUE NOT NULL,
        destino                     destino_enum NOT NULL,
        nivel_prioridad             nivel_prioridad_enum,
        score_confianza             FLOAT,
        status                      status_documento_enum NOT NULL DEFAULT 'pendiente_auditoria',
        asignado_a                  VARCHAR(255),
        asignado_at                 TIMESTAMPTZ,
        resuelto_at                 TIMESTAMPTZ,
        created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",

    'CREATE INDEX IF NOT EXISTS idx_dt_documento_id ON documentos_triaje(documento_id);',
    'CREATE INDEX IF NOT EXISTS idx_dt_status ON documentos_triaje(status);',
    'CREATE INDEX IF NOT EXISTS idx_dt_nivel_prioridad ON documentos_triaje(nivel_prioridad);',
    'CREATE INDEX IF NOT EXISTS idx_dt_destino ON documentos_triaje(destino_principal);',
    'CREATE INDEX IF NOT EXISTS idx_dt_requiere_auditoria ON documentos_triaje(requiere_auditoria_humana) WHERE requiere_auditoria_humana = TRUE;',
    'CREATE INDEX IF NOT EXISTS idx_dt_created_at ON documentos_triaje(created_at DESC);',
    'CREATE INDEX IF NOT EXISTS idx_dt_canal_origen ON documentos_triaje(canal_origen);',
    'CREATE INDEX IF NOT EXISTS idx_dt_diagnostico_trgm ON documentos_triaje USING GIN (diagnostico_principal gin_trgm_ops);',
    'CREATE INDEX IF NOT EXISTS idx_dt_paciente_trgm ON documentos_triaje USING GIN (paciente_nombre gin_trgm_ops);',

    'CREATE INDEX IF NOT EXISTS idx_ahitl_documento_id ON auditorias_hitl(documento_id);',
    'CREATE INDEX IF NOT EXISTS idx_ahitl_auditor ON auditorias_hitl(auditor_id);',
    'CREATE INDEX IF NOT EXISTS idx_ahitl_created_at ON auditorias_hitl(created_at DESC);',

    'CREATE INDEX IF NOT EXISTS idx_notif_enviada ON notificaciones(enviada) WHERE enviada = FALSE;',
    'CREATE INDEX IF NOT EXISTS idx_notif_documento_id ON notificaciones(documento_id);',

    'CREATE INDEX IF NOT EXISTS idx_cola_destino_status ON cola_procesamiento(destino, status);',

    """CREATE OR REPLACE FUNCTION trigger_set_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = NOW();
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;""",

    'DROP TRIGGER IF EXISTS set_updated_at_documentos_triaje ON documentos_triaje;',
    """CREATE TRIGGER set_updated_at_documentos_triaje
        BEFORE UPDATE ON documentos_triaje
        FOR EACH ROW
        EXECUTE FUNCTION trigger_set_updated_at();""",

    """CREATE OR REPLACE FUNCTION sincronizar_cola()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.destino_principal IS NOT NULL THEN
            INSERT INTO cola_procesamiento (
                documento_id, destino, nivel_prioridad, score_confianza, status
            )
            VALUES (
                NEW.documento_id, NEW.destino_principal, NEW.nivel_prioridad, NEW.score_confianza, NEW.status
            )
            ON CONFLICT (documento_id) DO UPDATE SET
                destino          = EXCLUDED.destino,
                nivel_prioridad  = EXCLUDED.nivel_prioridad,
                score_confianza  = EXCLUDED.score_confianza,
                status           = EXCLUDED.status;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;""",

    'DROP TRIGGER IF EXISTS trigger_sincronizar_cola ON documentos_triaje;',
    """CREATE TRIGGER trigger_sincronizar_cola
        AFTER INSERT OR UPDATE ON documentos_triaje
        FOR EACH ROW
        EXECUTE FUNCTION sincronizar_cola();""",

    """CREATE OR REPLACE VIEW v_urgentes_pendientes AS
    SELECT dt.documento_id, dt.tipo_documento, dt.paciente_nombre, dt.diagnostico_principal, dt.score_confianza, dt.canal_origen, dt.created_at, dt.tiempo_procesamiento_ms
    FROM documentos_triaje dt
    WHERE dt.nivel_prioridad = 'Urgente' AND dt.status = 'procesado'
    ORDER BY dt.created_at DESC;""",

    """CREATE OR REPLACE VIEW v_auditoria_pendiente AS
    SELECT dt.documento_id, dt.tipo_documento, dt.paciente_nombre, dt.diagnostico_principal, dt.score_confianza, dt.nivel_prioridad, dt.justificacion_enrutamiento, dt.error_mensaje, dt.created_at
    FROM documentos_triaje dt
    WHERE dt.requiere_auditoria_humana = TRUE AND dt.status = 'pendiente_auditoria'
    ORDER BY dt.created_at ASC;""",

    """CREATE OR REPLACE VIEW v_estadisticas_hoy AS
    SELECT
        COUNT(*) FILTER (WHERE status = 'procesado')               AS procesados_ok,
        COUNT(*) FILTER (WHERE status = 'pendiente_auditoria')     AS en_auditoria,
        COUNT(*) FILTER (WHERE status = 'error')                   AS errores,
        COUNT(*) FILTER (WHERE nivel_prioridad = 'Urgente')        AS urgentes,
        COUNT(*) FILTER (WHERE nivel_prioridad = 'Rutina')         AS rutina,
        COUNT(*) FILTER (WHERE nivel_prioridad = 'Ambiguo')        AS ambiguos,
        ROUND(AVG(score_confianza)::NUMERIC, 3)                    AS score_promedio,
        ROUND(AVG(tiempo_procesamiento_ms)::NUMERIC, 0)            AS tiempo_ms_promedio,
        COUNT(*)                                                   AS total
    FROM documentos_triaje
    WHERE created_at >= CURRENT_DATE;""",

    """INSERT INTO documentos_triaje (
        documento_id, tipo_archivo, canal_origen, status,
        texto_extraido, tipo_documento, nivel_prioridad, score_confianza,
        paciente_nombre, paciente_edad, diagnostico_principal, cie10_sugerido,
        hallazgos_clave, destino_principal, requiere_auditoria_humana,
        justificacion_enrutamiento, tiempo_procesamiento_ms
    ) VALUES
    ('DOC-SEED-2026-0001', 'TEXTO', 'Consulta_Externa', 'procesado', 'LABORATORIO CENTRAL. Paciente: Ana García, 35 años. Hemograma completo.', 'Analítica de Laboratorio', 'Rutina', 0.92, 'Ana García', 35, 'Hemograma normal', NULL, '["Resultados normales"]', 'Cola_Rutina', FALSE, 'Documento procesado con alta confianza.', 850),
    ('DOC-SEED-2026-8942', 'TEXTO', 'Guardia_Emergencias', 'procesado', 'HOSPITAL SANTA LUCIA. Paciente: Carlos Eduardo Mendes, 52 años. TEP agudo detectado.', 'Informe de Estudio por Imagenes', 'Urgente', 0.99, 'Carlos Eduardo Mendes', 52, 'Tromboembolismo Pulmonar Agudo (TEP)', 'I26.9', '["Defecto de llenado en arteria pulmonar compatible con TEP agudo"]', 'Cola_Emergencia_Medica', FALSE, 'Hallazgo crítico de alta gravedad.', 1240),
    ('DOC-SEED-2026-9999', 'TEXTO', 'Admision', 'pendiente_auditoria', '... texto ilegible ... px ... 45 ... mgr ???', 'Desconocido', 'Ambiguo', 0.22, NULL, NULL, NULL, NULL, '[]', 'Cola_Auditoria_Humana', TRUE, 'Score de confianza bajo (0.22).', 320)
    ON CONFLICT (documento_id) DO NOTHING;"""
]

DOWNGRADE_STATEMENTS = [
    "DROP VIEW IF EXISTS v_estadisticas_hoy CASCADE;",
    "DROP VIEW IF EXISTS v_auditoria_pendiente CASCADE;",
    "DROP VIEW IF EXISTS v_urgentes_pendientes CASCADE;",
    "DROP TABLE IF EXISTS cola_procesamiento CASCADE;",
    "DROP TABLE IF EXISTS notificaciones CASCADE;",
    "DROP TABLE IF EXISTS auditorias_hitl CASCADE;",
    "DROP TABLE IF EXISTS documentos_triaje CASCADE;",
    "DROP TYPE IF EXISTS decision_auditoria_enum CASCADE;",
    "DROP TYPE IF EXISTS status_oci_enum CASCADE;",
    "DROP TYPE IF EXISTS destino_enum CASCADE;",
    "DROP TYPE IF EXISTS status_documento_enum CASCADE;",
    "DROP TYPE IF EXISTS nivel_prioridad_enum CASCADE;",
    "DROP TYPE IF EXISTS tipo_archivo_enum CASCADE;",
]


def upgrade() -> None:
    """Crea la estructura completa de base de datos desde cero usando Alembic."""
    for stmt in UPGRADE_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    """Elimina las vistas, triggers, tablas y tipos creados."""
    for stmt in DOWNGRADE_STATEMENTS:
        op.execute(stmt)
