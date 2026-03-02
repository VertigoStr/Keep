"""Unit tests for JWT security utilities."""

import pytest
from datetime import datetime, timedelta
from src.utils.security import SecurityUtils


@pytest.mark.unit
class TestSecurityUtils:
    """Unit tests for JWT token generation and verification."""

    def test_create_token(self) -> None:
        """Test JWT token creation."""
        utils = SecurityUtils()
        user_id = "test-user-id"
        email = "test@example.com"
        
        token = utils.create_token(user_id, email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid(self) -> None:
        """Test JWT token verification with valid token."""
        utils = SecurityUtils()
        user_id = "test-user-id"
        email = "test@example.com"
        
        token = utils.create_token(user_id, email)
        payload = utils.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["email"] == email

    def test_verify_token_invalid(self) -> None:
        """Test JWT token verification with invalid token."""
        utils = SecurityUtils()
        
        payload = utils.verify_token("invalid_token")
        assert payload is None

    def test_verify_token_expired(self) -> None:
        """Test JWT token verification with expired token."""
        utils = SecurityUtils()
        
        # Create token with very short expiration
        token = utils.create_token("test-user-id", "test@example.com", expires_delta=timedelta(seconds=-1))
        
        payload = utils.verify_token(token)
        assert payload is None

    def test_hash_token(self) -> None:
        """Test token hashing."""
        utils = SecurityUtils()
        token = "test_token_value"
        
        hash1 = utils.hash_token(token)
        hash2 = utils.hash_token(token)
        
        assert hash1 == hash2  # Same input produces same hash
        assert hash1 != token  # Hash is different from original

    def test_hash_token_different_inputs(self) -> None:
        """Test token hashing with different inputs."""
        utils = SecurityUtils()
        
        hash1 = utils.hash_token("token1")
        hash2 = utils.hash_token("token2")
        
        assert hash1 != hash2

    def test_create_token_with_custom_expiration(self) -> None:
        """Test JWT token creation with custom expiration."""
        utils = SecurityUtils()
        user_id = "test-user-id"
        email = "test@example.com"
        expires_delta = timedelta(hours=2)
        
        token = utils.create_token(user_id, email, expires_delta=expires_delta)
        payload = utils.verify_token(token)
        
        assert payload is not None
        # Check expiration time is approximately 2 hours from now
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        diff = exp - now
        assert timedelta(hours=1, minutes=50) <= diff <= timedelta(hours=2, minutes=10)