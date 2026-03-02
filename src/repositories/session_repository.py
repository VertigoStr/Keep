"""Session repository for data access operations."""

from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.session import Session


class SessionRepository:
    """Repository for Session model data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create_session(
        self,
        user_id: str,
        token_hash: str,
        expires_at: datetime
    ) -> Session:
        """Create a new session.

        Args:
            user_id: User ID
            token_hash: Hashed JWT token
            expires_at: Token expiration time

        Returns:
            Created Session instance
        """
        session = Session(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )
        self.session.add(session)
        await self.session.commit()
        await self.session.refresh(session)
        return session

    async def get_session_by_token_hash(self, token_hash: str) -> Optional[Session]:
        """Get session by token hash.

        Args:
            token_hash: Hashed JWT token

        Returns:
            Session instance if found, None otherwise
        """
        result = await self.session.execute(
            select(Session).where(Session.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID.

        Args:
            session_id: Session ID

        Returns:
            True if deleted, False otherwise
        """
        result = await self.session.execute(
            delete(Session).where(Session.id == session_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of deleted sessions
        """
        result = await self.session.execute(
            delete(Session).where(Session.user_id == user_id)
        )
        await self.session.commit()
        return result.rowcount

    async def cleanup_expired_sessions(self) -> int:
        """Delete all expired sessions.

        Returns:
            Number of deleted sessions
        """
        result = await self.session.execute(
            delete(Session).where(Session.expires_at < datetime.utcnow())
        )
        await self.session.commit()
        return result.rowcount


__all__ = ["SessionRepository"]