"""Rate limiting service for brute force protection."""

from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.failed_login_repository import FailedLoginAttemptRepository


class RateLimitService:
    """Service for rate limiting failed login attempts."""

    MAX_ATTEMPTS = 3
    TIME_WINDOW_MINUTES = 15

    def __init__(self, session: AsyncSession) -> None:
        """Initialize rate limit service with database session."""
        self.session = session
        self.failed_login_repo = FailedLoginAttemptRepository(session)

    async def check_rate_limit(self, email: str, ip_address: str, user_agent: str = None) -> bool:
        """Check if login attempt is allowed based on rate limit.

        Args:
            email: Email address being used for login
            ip_address: Client IP address
            user_agent: Client user agent string

        Returns:
            True if allowed, False if rate limited
        """
        # Count recent attempts
        recent_count = await self.failed_login_repo.count_recent_attempts(
            email,
            self.TIME_WINDOW_MINUTES
        )

        # Check if rate limit exceeded
        if recent_count >= self.MAX_ATTEMPTS:
            return False

        # Record this attempt
        await self.failed_login_repo.create_attempt(email, ip_address, user_agent)
        return True

    async def count_recent_attempts(self, email: str, minutes: int = 15) -> int:
        """Count recent failed login attempts.

        Args:
            email: Email address to check
            minutes: Number of minutes to look back

        Returns:
            Count of recent attempts
        """
        return await self.failed_login_repo.count_recent_attempts(email, minutes)

    async def cleanup_old_attempts(self, hours: int = 24) -> int:
        """Clean up old failed login attempts.

        Args:
            hours: Number of hours after which to delete attempts

        Returns:
            Number of deleted records
        """
        return await self.failed_login_repo.cleanup_old_attempts(hours)


__all__ = ["RateLimitService"]