"""Authentication service for user registration and login."""

from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.user_repository import UserRepository
from src.repositories.session_repository import SessionRepository
from src.services.password_service import PasswordService
from src.utils.security import SecurityUtils
from src.middleware.error_handler import EmailExistsError, InvalidCredentialsError
from src.models.user import User
from src.models.session import Session


class AuthService:
    """Service for authentication operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize auth service with database session."""
        self.session = session
        self.user_repository = UserRepository(session)
        self.session_repository = SessionRepository(session)
        self.password_service = PasswordService()
        self.security_utils = SecurityUtils()

    async def register_user(self, email: str, password: str) -> User:
        """Register a new user.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            Created User instance

        Raises:
            EmailExistsError: If email already exists
        """
        # Check if email already exists
        if await self.user_repository.email_exists(email):
            raise EmailExistsError()

        # Hash password
        password_hash = self.password_service.hash_password(password)

        # Create user
        user = await self.user_repository.create_user(email, password_hash)
        return user

    async def login_user(self, email: str, password: str) -> tuple[User, str]:
        """Authenticate a user and create a session.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            Tuple of (User instance, JWT token)

        Raises:
            InvalidCredentialsError: If email or password is invalid
        """
        # Get user by email
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        # Verify password
        if not self.password_service.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        # Create JWT token
        token = self.security_utils.create_token(user.id, user.email)

        # Create session
        token_hash = self.security_utils.hash_token(token)
        expires_at = datetime.utcnow() + timedelta(seconds=self.security_utils.expiration_seconds)
        await self.session_repository.create_session(user.id, token_hash, expires_at)

        return user, token

    async def logout_user(self, token: str) -> None:
        """Logout a user by deleting their session.

        Args:
            token: JWT token

        Raises:
            UnauthorizedError: If session not found
        """
        token_hash = self.security_utils.hash_token(token)
        session = await self.session_repository.get_session_by_token_hash(token_hash)
        
        if not session:
            raise UnauthorizedError()
        
        await self.session_repository.delete_session(session.id)


__all__ = ["AuthService"]