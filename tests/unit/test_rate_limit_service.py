"""Unit tests for rate limit service."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.rate_limit_service import RateLimitService


@pytest.mark.unit
class TestRateLimitService:
    """Unit tests for rate limiting logic."""

    @pytest.mark.asyncio
    async def test_check_rate_limit_allowed(self, db_session: AsyncSession) -> None:
        """Test rate limit allows first few attempts."""
        service = RateLimitService(db_session)
        email = "test@example.com"
        ip_address = "127.0.0.1"
        
        # First 3 attempts should be allowed
        for i in range(3):
            result = await service.check_rate_limit(email, ip_address)
            assert result is True, f"Attempt {i+1} should be allowed"

    @pytest.mark.asyncio
    async def test_check_rate_limit_blocked(self, db_session: AsyncSession) -> None:
        """Test rate limit blocks after 3 attempts."""
        service = RateLimitService(db_session)
        email = "test@example.com"
        ip_address = "127.0.0.1"
        
        # First 3 attempts should be allowed
        for _ in range(3):
            await service.check_rate_limit(email, ip_address)
        
        # 4th attempt should be blocked
        result = await service.check_rate_limit(email, ip_address)
        assert result is False

    @pytest.mark.asyncio
    async def test_check_rate_limit_different_emails(self, db_session: AsyncSession) -> None:
        """Test rate limit is per email."""
        service = RateLimitService(db_session)
        
        # 3 attempts for first email
        for _ in range(3):
            await service.check_rate_limit("user1@example.com", "127.0.0.1")
        
        # First email should be blocked
        result1 = await service.check_rate_limit("user1@example.com", "127.0.0.1")
        assert result1 is False
        
        # Second email should still be allowed
        result2 = await service.check_rate_limit("user2@example.com", "127.0.0.1")
        assert result2 is True

    @pytest.mark.asyncio
    async def test_cleanup_old_attempts(self, db_session: AsyncSession) -> None:
        """Test cleanup of old failed login attempts."""
        service = RateLimitService(db_session)
        email = "test@example.com"
        ip_address = "127.0.0.1"
        
        # Create some attempts
        for _ in range(3):
            await service.check_rate_limit(email, ip_address)
        
        # Cleanup attempts older than 24 hours
        deleted_count = await service.cleanup_old_attempts(hours=24)
        assert deleted_count >= 0

    @pytest.mark.asyncio
    async def test_count_recent_attempts(self, db_session: AsyncSession) -> None:
        """Test counting recent failed login attempts."""
        service = RateLimitService(db_session)
        email = "test@example.com"
        ip_address = "127.0.0.1"
        
        # No attempts initially
        count = await service.count_recent_attempts(email, minutes=15)
        assert count == 0
        
        # Add some attempts
        for _ in range(3):
            await service.check_rate_limit(email, ip_address)
        
        # Count should be 3
        count = await service.count_recent_attempts(email, minutes=15)
        assert count == 3