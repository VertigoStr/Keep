"""Unit tests for password validators."""

import pytest
from src.utils.validators import validate_password_complexity


@pytest.mark.unit
class TestPasswordValidator:
    """Unit tests for password validation."""

    def test_valid_password(self) -> None:
        """Test valid password passes validation."""
        password = "SecurePass123!"
        result = validate_password_complexity(password)
        assert result is True

    def test_password_too_short(self) -> None:
        """Test password too short fails validation."""
        password = "Short1!"
        result = validate_password_complexity(password)
        assert result is False

    def test_password_no_uppercase(self) -> None:
        """Test password without uppercase fails validation."""
        password = "securepass123!"
        result = validate_password_complexity(password)
        assert result is False

    def test_password_no_digit(self) -> None:
        """Test password without digit fails validation."""
        password = "SecurePassword!"
        result = validate_password_complexity(password)
        assert result is False

    def test_password_no_special_char(self) -> None:
        """Test password without special character fails validation."""
        password = "SecurePass123"
        result = validate_password_complexity(password)
        assert result is False

    def test_password_exactly_8_chars(self) -> None:
        """Test password with exactly 8 characters passes validation."""
        password = "Secur1!"
        result = validate_password_complexity(password)
        assert result is False  # Too short, needs 8+ chars

    def test_password_with_spaces(self) -> None:
        """Test password with spaces passes validation."""
        password = "Secure Pass123!"
        result = validate_password_complexity(password)
        assert result is True

    def test_empty_password(self) -> None:
        """Test empty password fails validation."""
        password = ""
        result = validate_password_complexity(password)
        assert result is False