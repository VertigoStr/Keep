"""Integration tests for authentication flow."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for login flow."""

    @pytest.mark.asyncio
    async def test_successful_login(self, client: AsyncClient, sample_user_data: dict, sample_login_data: dict) -> None:
        """Test successful login with valid credentials."""
        # Register user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        response = await client.post("/api/v1/auth/login", json=sample_login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
        assert "id" in data["user"]
        
        # Check for session cookie
        cookies = response.cookies
        assert "session_token" in cookies

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient, sample_login_data: dict) -> None:
        """Test login with invalid email."""
        response = await client.post("/api/v1/auth/login", json=sample_login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "invalid_credentials"

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test login with invalid password."""
        # Register user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with wrong password
        login_data = {
            "email": sample_user_data["email"],
            "password": "WrongPassword123!"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "invalid_credentials"

    @pytest.mark.asyncio
    async def test_login_creates_session(self, client: AsyncClient, sample_user_data: dict, sample_login_data: dict, db_session: AsyncSession) -> None:
        """Test that login creates a session in database."""
        from src.models.session import Session
        from sqlalchemy import select
        
        # Register and login
        await client.post("/api/v1/auth/register", json=sample_user_data)
        await client.post("/api/v1/auth/login", json=sample_login_data)
        
        # Check session exists in database
        result = await db_session.execute(select(Session))
        sessions = result.scalars().all()
        
        assert len(sessions) == 1
        assert sessions[0].user_id is not None
        assert sessions[0].token_hash is not None
        assert sessions[0].expires_at is not None

    @pytest.mark.asyncio
    async def test_login_case_insensitive_email(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test login with uppercase email."""
        # Register user
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login with uppercase email
        login_data = {
            "email": sample_user_data["email"].upper(),
            "password": sample_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, client: AsyncClient) -> None:
        """Test login with missing fields."""
        response = await client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        
        assert response.status_code == 422  # FastAPI validation error