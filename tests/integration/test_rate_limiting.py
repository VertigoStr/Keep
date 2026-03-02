"""Integration tests for rate limiting."""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestRateLimiting:
    """Integration tests for rate limiting on login endpoint."""

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_after_3_attempts(self, client: AsyncClient, sample_login_data: dict) -> None:
        """Test that rate limit blocks after 3 failed login attempts."""
        # Make 3 failed login attempts
        for i in range(3):
            response = await client.post("/api/v1/auth/login", json=sample_login_data)
            assert response.status_code in [401, 429], f"Attempt {i+1} should fail"

        # 4th attempt should be rate limited
        response = await client.post("/api/v1/auth/login", json=sample_login_data)
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "too_many_attempts"

    @pytest.mark.asyncio
    async def test_rate_limit_per_email(self, client: AsyncClient) -> None:
        """Test that rate limit is per email address."""
        # Make 3 failed attempts for first email
        for _ in range(3):
            await client.post("/api/v1/auth/login", json={"email": "user1@example.com", "password": "wrong"})

        # First email should be rate limited
        response1 = await client.post("/api/v1/auth/login", json={"email": "user1@example.com", "password": "wrong"})
        assert response1.status_code == 429

        # Second email should still be allowed
        response2 = await client.post("/api/v1/auth/login", json={"email": "user2@example.com", "password": "wrong"})
        assert response2.status_code == 401

    @pytest.mark.asyncio
    async def test_rate_limit_includes_retry_after_header(self, client: AsyncClient, sample_login_data: dict) -> None:
        """Test that rate limited response includes Retry-After header."""
        # Make 3 failed attempts
        for _ in range(3):
            await client.post("/api/v1/auth/login", json=sample_login_data)

        # 4th attempt should be rate limited
        response = await client.post("/api/v1/auth/login", json=sample_login_data)
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    @pytest.mark.asyncio
    async def test_successful_login_resets_rate_limit(self, client: AsyncClient, sample_user_data: dict, sample_login_data: dict) -> None:
        """Test that successful login doesn't count towards rate limit."""
        # Register user
        await client.post("/api/v1/auth/register", json=sample_user_data)

        # Make 2 failed attempts
        for _ in range(2):
            await client.post("/api/v1/auth/login", json={"email": sample_user_data["email"], "password": "wrong"})

        # Successful login
        await client.post("/api/v1/auth/login", json=sample_login_data)

        # Should still be able to make more attempts (not rate limited)
        response = await client.post("/api/v1/auth/login", json={"email": sample_user_data["email"], "password": "wrong"})
        assert response.status_code == 401  # Not rate limited, just wrong password