"""FailedLoginAttempt repository for data access operations."""

from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from src.models.failed_login import FailedLoginAttempt


class FailedLoginAttemptRepository:
    """Repository for FailedLoginAttempt model data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create_attempt(
        self,
        email: str,
        ip_address: str,
        user_agent: Optional[str] = None
    ) -> FailedLoginAttempt:
        """Create a new failed login attempt.

        Args:
            email: Email used in attempt
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            Created FailedLoginAttempt instance
        """
        attempt = FailedLoginAttempt(
            email=email.lower(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.session.add(attempt)
        await self.session.commit()
        await self.session.refresh(attempt)
        return attempt

    async def count_recent_attempts(self, email: str, minutes: int = 15) -> int:
        """Count recent failed login attempts for an email.

        Args:
            email: Email address to check
            minutes: Number of minutes to look back

        Returns:
            Count of recent attempts
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
        
        result = await self.session.execute(
            select(func.count(FailedLoginAttempt.id))
            .where(FailedLoginAttempt.email == email.lower())
            .where(FailedLoginAttempt.timestamp >= cutoff_time)
        )
        return result.scalar() or 0

    async def cleanup_old_attempts(self, hours: int = 24) -> int:
        """Delete old failed login attempts.

        Args:
            hours: Number of hours after which to delete attempts

        Returns:
            Number of deleted records
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        result = await self.session.execute(
            delete(FailedLoginAttempt)
            .where(FailedLoginAttempt.timestamp < cutoff_time)
        )
        await self.session.commit()
        return result.rowcount

    async def delete_attempts_by_email(self, email: str) -> int:
        """Delete all failed login attempts for a specific email.

        Args:
            email: Email address to delete attempts for

        Returns:
            Number of deleted records
        """
        result = await self.session.execute(
            delete(FailedLoginAttempt)
            .where(FailedLoginAttempt.email == email.lower())
        )
        await self.session.commit()
        return result.rowcount


__all__ = ["FailedLoginAttemptRepository"]