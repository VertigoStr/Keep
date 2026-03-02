"""Unit tests for password service."""

import pytest
from src.services.password_service import PasswordService


@pytest.mark.unit
class TestPasswordService:
    """Unit tests for password hashing and verification."""

    def test_hash_password(self) -> None:
        """Test password hashing produces different hashes for same password."""
        password = "SecurePass123!"
        service = PasswordService()
        
        hash1 = service.hash_password(password)
        hash2 = service.hash_password(password)
        
        assert hash1 != hash2  # Different salts produce different hashes
        assert len(hash1) > 0
        assert len(hash2) > 0

    def test_verify_password_correct(self) -> None:
        """Test password verification with correct password."""
        password = "SecurePass123!"
        service = PasswordService()
        
        hashed = service.hash_password(password)
        result = service.verify_password(password, hashed)
        
        assert result is True

    def test_verify_password_incorrect(self) -> None:
        """Test password verification with incorrect password."""
        password = "SecurePass123!"
        wrong_password = "WrongPass123!"
        service = PasswordService()
        
        hashed = service.hash_password(password)
        result = service.verify_password(wrong_password, hashed)
        
        assert result is False

    def test_verify_password_empty(self) -> None:
        """Test password verification with empty password."""
        password = "SecurePass123!"
        service = PasswordService()
        
        hashed = service.hash_password(password)
        result = service.verify_password("", hashed)
        
        assert result is False

    def test_hash_password_empty(self) -> None:
        """Test hashing empty password."""
        password = ""
        service = PasswordService()
        
        hashed = service.hash_password(password)
        assert len(hashed) > 0

    def test_hash_password_special_chars(self) -> None:
        """Test hashing password with special characters."""
        password = "P@$$w0rd!#$%^&*()"
        service = PasswordService()
        
        hashed = service.hash_password(password)
        result = service.verify_password(password, hashed)
        
        assert result is True

    def test_verify_password_with_invalid_hash(self) -> None:
        """Test password verification with invalid hash."""
        password = "SecurePass123!"
        invalid_hash = "invalid_hash"
        service = PasswordService()
        
        result = service.verify_password(password, invalid_hash)
        
        assert result is False