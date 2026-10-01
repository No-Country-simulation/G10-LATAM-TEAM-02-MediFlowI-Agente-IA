"""implement_unified_db_proposal

Revision ID: o8p808522kl4
Revises: n7o707411jk3
Create Date: 2026-09-30 20:00:00

Implementa la propuesta aprobada de diseño de base de datos hospitalaria:
- Añade especialidad_medica a usuarios y amplía rol_enum con COORDINADOR.
- Ficha de pacientes con genero_enum ('FEMENINO', 'MASCULINO'), numero_telefono
  y cálculo dinámico de edad (sin columna estática redundante).
- Tabla episodios_clinicos para el flujo: Admisión -> Médico General -> Especialista.
- Tabla auditorias_coordinacion para el módulo Human-in-the-Loop.
- Tabla trazabilidad_eventos para bitácora inmutable de ciclo de vida.
- Agrega Farmacia_Hospitalaria a destino_enum y fija default 'Admision' en canal_origen.
"""

from alembic import op

revision = "o8p808522kl4"
down_revision = "n7o707411jk3"
branch_labels = None
depends_on = None

UPGRADE_STATEMENTS = [
    # ── 1. Roles y usuarios ──────────────────────────────────────────────────
    "ALTER TYPE rol_enum ADD VALUE IF NOT EXISTS 'COORDINADOR';",
    "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS especialidad_medica VARCHAR(100);",
    "COMMENT ON COLUMN usuarios.especialidad_medica IS 'Especialidad clínica del usuario (Medicina General, Cardiología, etc.).';",

    # ── 2. Pacientes: teléfono, género y vista dinámica de edad ───────────────
    "ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS numero_telefono VARCHAR(50);",
    "UPDATE pacientes SET numero_telefono = telefono WHERE numero_telefono IS NULL AND telefono IS NOT NULL;",
    "ALTER TABLE pacientes ADD COLUMN IF NOT EXISTS genero VARCHAR(20);",
    "UPDATE pacientes SET genero = CASE WHEN sexo IN ('M', 'MASCULINO') THEN 'MASCULINO' WHEN sexo IN ('F', 'FEMENINO') THEN 'FEMENINO' ELSE genero END WHERE genero IS NULL;",
    "DO $$ BEGIN CREATE TYPE genero_enum AS ENUM ('FEMENINO', 'MASCULINO'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "COMMENT ON COLUMN pacientes.numero_telefono IS 'Número de teléfono principal de contacto del paciente.';",
    "COMMENT ON COLUMN pacientes.genero IS 'Género clínico del paciente (FEMENINO, MASCULINO).';",

    # ── 3. Episodios clínicos (Flujo de atención escalable) ────────────────────
    """CREATE TABLE IF NOT EXISTS episodios_clinicos (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        codigo_episodio VARCHAR(50) UNIQUE NOT NULL,
        paciente_id UUID REFERENCES pacientes(id) ON DELETE SET NULL,
        operador_ingreso_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
        medico_general_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
        medico_especialista_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
        especialidad_requerida VARCHAR(100),
        estado_atencion VARCHAR(50) NOT NULL DEFAULT 'ingresado',
        nivel_prioridad VARCHAR(20) NOT NULL DEFAULT 'Rutina',
        motivo_consulta TEXT,
        diagnostico_general TEXT,
        diagnostico_especialista TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",
    "CREATE INDEX IF NOT EXISTS idx_episodios_paciente ON episodios_clinicos(paciente_id);",
    "CREATE INDEX IF NOT EXISTS idx_episodios_codigo ON episodios_clinicos(codigo_episodio);",
    "COMMENT ON TABLE episodios_clinicos IS 'Ciclo de vida clínico: Recepción/Admisión -> Médico General -> Especialista';",

    # ── 4. Documentos de triaje: episodio_id, farmacia y default Admisión ─────
    "ALTER TABLE documentos_triaje ADD COLUMN IF NOT EXISTS episodio_id UUID REFERENCES episodios_clinicos(id) ON DELETE SET NULL;",
    "ALTER TABLE documentos_triaje ALTER COLUMN canal_origen SET DEFAULT 'Admision';",
    "ALTER TYPE destino_enum ADD VALUE IF NOT EXISTS 'Farmacia_Hospitalaria';",
    "CREATE INDEX IF NOT EXISTS idx_dt_episodio ON documentos_triaje(episodio_id);",

    # ── 5. Auditorías de coordinación (Human-in-the-Loop) ──────────────────────
    """CREATE TABLE IF NOT EXISTS auditorias_coordinacion (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        episodio_id UUID REFERENCES episodios_clinicos(id) ON DELETE CASCADE,
        documento_id UUID REFERENCES documentos_triaje(id) ON DELETE CASCADE,
        coordinador_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
        decision VARCHAR(30) NOT NULL,
        nueva_prioridad VARCHAR(20),
        nueva_especialidad VARCHAR(100),
        nuevo_medico_asignado_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
        justificacion_clinica TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",
    "CREATE INDEX IF NOT EXISTS idx_auditorias_coord_doc ON auditorias_coordinacion(documento_id);",
    "COMMENT ON TABLE auditorias_coordinacion IS 'Decisiones tomadas por el Coordinador en casos ambiguos o derivaciones (HITL).';",

    # ── 6. Trazabilidad de eventos ────────────────────────────────────────────
    """CREATE TABLE IF NOT EXISTS trazabilidad_eventos (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        episodio_id UUID REFERENCES episodios_clinicos(id) ON DELETE CASCADE,
        documento_id UUID REFERENCES documentos_triaje(id) ON DELETE CASCADE,
        usuario_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
        evento VARCHAR(50) NOT NULL,
        descripcion TEXT NOT NULL,
        metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",
    "CREATE INDEX IF NOT EXISTS idx_trazabilidad_episodio ON trazabilidad_eventos(episodio_id);",
    "CREATE INDEX IF NOT EXISTS idx_trazabilidad_documento ON trazabilidad_eventos(documento_id);",
    "COMMENT ON TABLE trazabilidad_eventos IS 'Bitácora inmutable de eventos hospitalarios y trazabilidad del triaje.';"
]


def upgrade() -> None:
    for stmt in UPGRADE_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS trazabilidad_eventos CASCADE;")
    op.execute("DROP TABLE IF EXISTS auditorias_coordinacion CASCADE;")
    op.execute("ALTER TABLE documentos_triaje DROP COLUMN IF EXISTS episodio_id;")
    op.execute("DROP TABLE IF EXISTS episodios_clinicos CASCADE;")
    op.execute("ALTER TABLE pacientes DROP COLUMN IF EXISTS genero;")
    op.execute("ALTER TABLE pacientes DROP COLUMN IF EXISTS numero_telefono;")
    op.execute("ALTER TABLE usuarios DROP COLUMN IF EXISTS especialidad_medica;")
