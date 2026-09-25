"""rotate_weak_seed_credentials

Revision ID: n7o707411jk3
Revises: m6n606300ij2

Rota exclusivamente las credenciales iniciales que todavía conservan sus
hashes públicos originales. Las contraseñas modificadas por usuarios no se
sobrescriben. Las sesiones activas de las cuentas rotadas quedan revocadas.
"""

from alembic import op

revision = "n7o707411jk3"
down_revision = "m6n606300ij2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        WITH credenciales(
            documento_identidad, hash_anterior, hash_nuevo, salt_nuevo
        ) AS (
            VALUES
                (
                    '12345678',
                    '3cafb24391f84a713103a1dce118e10cd75e702c30f6c56e4f995ad2de4a6888',
                    '8d38cd6124ba2025c874ebcd1bbc0dca74f22857278cdd44fa0e753a58b97590',
                    '67a3cad816a7eb3e252de216d387fe7c'
                ),
                (
                    '87654321',
                    '133087da2849740f018584f58f44cfbf94aefd7737f38e9f676011ad89f867cc',
                    '09a31f85614c4c525df3428843b2cf386f7f4d41ac9b09d21e95d58adbbd033c',
                    '5cf19a850887ba4db6bec0c72c1f67c9'
                ),
                (
                    '11223344',
                    'ac6880db7dfff50573a3c37c60fef5d4571dbee034bed2fd45267fa54f971739',
                    '94a335594b12a5e97cedcf3a7cf502ccfb7e5d9d6ff4be3f655f6fa104c2d383',
                    '905e5082e25894f053d029f08b7c581f'
                ),
                (
                    '44332211',
                    '80a7637fb13f7f41f1d449c4ecf20b99b00cf7f059259df78e439b8e6d44acd7',
                    '3947696d8a522c08ceaedca49c8d42f9ac20a1f69289fb2ffc6e421b4599f76d',
                    '1523c6a5975c58ade4a19d57a98c328b'
                )
        ),
        usuarios_rotados AS (
            UPDATE usuarios AS usuario
               SET password_hash = credencial.hash_nuevo,
                   salt = credencial.salt_nuevo,
                   updated_at = NOW()
              FROM credenciales AS credencial
             WHERE usuario.documento_identidad = credencial.documento_identidad
               AND usuario.password_hash = credencial.hash_anterior
            RETURNING usuario.id
        )
        UPDATE sesiones_usuario
           SET revoked_at = NOW()
         WHERE usuario_id IN (SELECT id FROM usuarios_rotados)
           AND revoked_at IS NULL;
        """
    )


def downgrade() -> None:
    """No restaura contraseñas débiles ni reactiva sesiones por seguridad."""
