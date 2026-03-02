"""Session service for session management and cleanup."""

from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.session_repository import SessionRepository


class SessionService:
    """Service for session management."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize session service with database session."""
        self.session = session
        self.session_repository = SessionRepository(session)

    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions.

        Returns:
            Number of deleted sessions
        """
        return await self.session_repository.cleanup_expired_sessions()


__all__ = ["SessionService"]