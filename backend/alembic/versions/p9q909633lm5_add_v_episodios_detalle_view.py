"""add_v_episodios_detalle_view

Revision ID: p9q909633lm5
Revises: o8p808522kl4
Create Date: 2026-10-01 13:00:00

Crea la vista SQL agregada v_episodios_detalle para consultas unificadas del ciclo
de atención médica relacionando episodios_clinicos con pacientes (incluyendo cálculo
dinámico de edad en tiempo real) y usuarios (operador de admisión, médico general y especialista).
"""

from typing import Sequence, Union
from alembic import op

revision: str = "p9q909633lm5"
down_revision: Union[str, Sequence[str], None] = "o8p808522kl4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UPGRADE_STATEMENTS = [
    """CREATE OR REPLACE VIEW v_episodios_detalle AS
    SELECT 
        e.id AS episodio_id,
        e.codigo_episodio,
        e.estado_atencion,
        e.nivel_prioridad,
        e.motivo_consulta,
        e.diagnostico_general,
        e.diagnostico_especialista,
        e.especialidad_requerida,
        e.created_at,
        e.updated_at,
        
        -- Datos del Paciente
        p.id AS paciente_id,
        p.tipo_documento AS paciente_tipo_documento,
        p.numero_documento AS paciente_numero_documento,
        p.historia_clinica AS paciente_historia_clinica,
        p.nombres AS paciente_nombres,
        p.apellidos AS paciente_apellidos,
        TRIM(CONCAT(p.nombres, ' ', p.apellidos)) AS paciente_nombre_completo,
        p.fecha_nacimiento AS paciente_fecha_nacimiento,
        CASE 
            WHEN p.fecha_nacimiento IS NOT NULL THEN EXTRACT(YEAR FROM age(CURRENT_DATE, p.fecha_nacimiento))::INT
            ELSE NULL 
        END AS paciente_edad,
        p.genero AS paciente_genero,
        p.numero_telefono AS paciente_numero_telefono,
        p.correo AS paciente_correo,
        
        -- Operador de Admisión / Ingreso
        op.id AS operador_ingreso_id,
        TRIM(CONCAT(op.nombres, ' ', op.apellidos)) AS operador_ingreso_nombre,
        
        -- Médico General Asignado
        mg.id AS medico_general_id,
        TRIM(CONCAT(mg.nombres, ' ', mg.apellidos)) AS medico_general_nombre,
        mg.especialidad_medica AS medico_general_especialidad,
        
        -- Médico Especialista Asignado
        me.id AS medico_especialista_id,
        TRIM(CONCAT(me.nombres, ' ', me.apellidos)) AS medico_especialista_nombre,
        me.especialidad_medica AS medico_especialista_especialidad

    FROM episodios_clinicos e
    LEFT JOIN pacientes p ON e.paciente_id = p.id
    LEFT JOIN usuarios op ON e.operador_ingreso_id = op.id
    LEFT JOIN usuarios mg ON e.medico_general_id = mg.id
    LEFT JOIN usuarios me ON e.medico_especialista_id = me.id;""",

    "COMMENT ON VIEW v_episodios_detalle IS 'Vista agregada de consulta clínica: relaciona episodios, datos de pacientes con edad dinámica y profesionales asignados.';"
]

DOWNGRADE_STATEMENTS = [
    "DROP VIEW IF EXISTS v_episodios_detalle CASCADE;"
]


def upgrade() -> None:
    for stmt in UPGRADE_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DOWNGRADE_STATEMENTS:
        op.execute(stmt)
