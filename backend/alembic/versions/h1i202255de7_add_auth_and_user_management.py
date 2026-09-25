"""add_auth_and_user_management

Revision ID: h1i202255de7
Revises: g9h001143cd6
Create Date: 2026-09-25 01:20:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'h1i202255de7'
down_revision: Union[str, Sequence[str], None] = 'g9h001143cd6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_STATEMENTS = [
    "DO $$ BEGIN CREATE TYPE rol_enum AS ENUM ('ADMINISTRADOR', 'OPERADOR', 'AUDITOR', 'SUPERVISOR'); EXCEPTION WHEN duplicate_object THEN null; END $$;",
    "DO $$ BEGIN CREATE TYPE estado_usuario_enum AS ENUM ('ACTIVO', 'INACTIVO'); EXCEPTION WHEN duplicate_object THEN null; END $$;",

    """CREATE TABLE IF NOT EXISTS usuarios (
        id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        documento_identidad     VARCHAR(8) UNIQUE NOT NULL,
        password_hash           VARCHAR(255) NOT NULL,
        salt                    VARCHAR(64) NOT NULL,
        nombres                 VARCHAR(250) NOT NULL,
        apellidos               VARCHAR(250) NOT NULL,
        correo                  VARCHAR(250),
        telefono                VARCHAR(50),
        rol                     rol_enum NOT NULL DEFAULT 'OPERADOR',
        estado                  estado_usuario_enum NOT NULL DEFAULT 'ACTIVO',
        created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );""",

    # Comentarios SQL PostgreSQL
    "COMMENT ON TABLE usuarios IS 'Registro central de usuarios del sistema MediFlow con control de acceso basado en roles (RBAC).';",
    "COMMENT ON COLUMN usuarios.id IS 'Identificador unico UUID del usuario.';",
    "COMMENT ON COLUMN usuarios.documento_identidad IS 'Numero de documento de identidad de 8 cifras (DNI por el momento).';",
    "COMMENT ON COLUMN usuarios.password_hash IS 'Hash PBKDF2-HMAC-SHA256 de la contraseña.';",
    "COMMENT ON COLUMN usuarios.salt IS 'Salt aleatorio utilizado en el hash de la contraseña.';",
    "COMMENT ON COLUMN usuarios.nombres IS 'Nombres del usuario.';",
    "COMMENT ON COLUMN usuarios.apellidos IS 'Apellidos del usuario.';",
    "COMMENT ON COLUMN usuarios.correo IS 'Correo electronico institucional del usuario.';",
    "COMMENT ON COLUMN usuarios.telefono IS 'Telefono de contacto del usuario.';",
    "COMMENT ON COLUMN usuarios.rol IS 'Rol asignado (ADMINISTRADOR, OPERADOR, AUDITOR, SUPERVISOR).';",
    "COMMENT ON COLUMN usuarios.estado IS 'Estado del usuario en el sistema (ACTIVO, INACTIVO).';",

    # Cargar usuarios iniciales por defecto (DNI de 8 cifras)
    """INSERT INTO usuarios (documento_identidad, password_hash, salt, nombres, apellidos, correo, rol, estado)
       VALUES 
       ('12345678', '3cafb24391f84a713103a1dce118e10cd75e702c30f6c56e4f995ad2de4a6888', '1234567890abcdef1234567890abcdef', 'Administrador', 'Sistema', 'admin@mediflow.local', 'ADMINISTRADOR', 'ACTIVO'),
       ('87654321', '133087da2849740f018584f58f44cfbf94aefd7737f38e9f676011ad89f867cc', '1234567890abcdef1234567890abcdef', 'Juan', 'Pérez', 'operador@mediflow.local', 'OPERADOR', 'ACTIVO'),
       ('11223344', 'ac6880db7dfff50573a3c37c60fef5d4571dbee034bed2fd45267fa54f971739', '1234567890abcdef1234567890abcdef', 'Dra. Elena', 'Morales', 'auditor@mediflow.local', 'AUDITOR', 'ACTIVO'),
       ('44332211', '80a7637fb13f7f41f1d449c4ecf20b99b00cf7f059259df78e439b8e6d44acd7', '1234567890abcdef1234567890abcdef', 'Dr. Carlos', 'Ríos', 'supervisor@mediflow.local', 'SUPERVISOR', 'ACTIVO')
       ON CONFLICT (documento_identidad) DO NOTHING;"""
]

DOWNGRADE_STATEMENTS = [
    "DROP TABLE IF EXISTS usuarios CASCADE;",
    "DROP TYPE IF EXISTS estado_usuario_enum;",
    "DROP TYPE IF EXISTS rol_enum;"
]


def upgrade() -> None:
    for stmt in UPGRADE_STATEMENTS:
        op.execute(stmt)


def downgrade() -> None:
    for stmt in DOWNGRADE_STATEMENTS:
        op.execute(stmt)
