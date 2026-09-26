"""Pruebas unitarias de persistencia segura de sesiones."""

from app.repositories.session_repository import token_digest


def test_token_digest_is_deterministic_and_does_not_expose_token():
    token = "mf_session_secret-value"
    digest = token_digest(token)

    assert digest == token_digest(token)
    assert len(digest) == 64
    assert token not in digest
