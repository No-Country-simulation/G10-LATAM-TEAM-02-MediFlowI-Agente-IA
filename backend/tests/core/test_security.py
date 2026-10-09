import pytest
from app.core.security import hash_password, verify_password

def test_hash_password_generates_different_hashes_for_same_password():
    password = "MySecurePassword123!"
    hash1, salt1 = hash_password(password)
    hash2, salt2 = hash_password(password)
    
    assert hash1 != hash2
    assert hash1.startswith("$2b$") or hash1.startswith("$2a$")
    assert len(hash1) == 60
    assert len(salt1) > 0

def test_verify_password_correct():
    password = "MySecurePassword123!"
    hashed, salt = hash_password(password)
    
    assert verify_password(password, hashed, salt) is True

def test_verify_password_incorrect():
    password = "MySecurePassword123!"
    wrong_password = "WrongPassword123!"
    hashed, salt = hash_password(password)
    
    assert verify_password(wrong_password, hashed, salt) is False
