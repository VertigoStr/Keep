"""Password service for hashing and verification."""

import bcrypt
from src.config import get_settings


class PasswordService:
    """Service for password hashing and verification using bcrypt."""

    def __init__(self) -> None:
        """Initialize password service with bcrypt rounds from settings."""
        settings = get_settings()
        self.rounds = settings.bcrypt_rounds

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=self.rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against a hash.

        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches hash, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False


__all__ = ["PasswordService"]