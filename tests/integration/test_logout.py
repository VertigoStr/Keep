"""Integration tests for logout flow."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestLogoutFlow:
    """Integration tests for logout flow."""

    @pytest.mark.asyncio
    async def test_successful_logout(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test successful logout."""
        # Register and login
        await client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        # Get session token
        session_token = login_response.cookies.get("session_token")
        assert session_token is not None
        
        # Logout
        logout_response = await client.post(
            "/api/v1/auth/logout",
            cookies={"session_token": session_token}
        )
        
        assert logout_response.status_code == 200
        data = logout_response.json()
        assert data["message"] == "Logged out successfully"
        
        # Check cookie is cleared
        cookies = logout_response.cookies
        assert cookies.get("session_token") == "" or cookies.get("session_token") is None

    @pytest.mark.asyncio
    async def test_logout_without_session(self, client: AsyncClient) -> None:
        """Test logout without active session."""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "unauthorized"

    @pytest.mark.asyncio
    async def test_logout_with_invalid_token(self, client: AsyncClient) -> None:
        """Test logout with invalid token."""
        response = await client.post(
            "/api/v1/auth/logout",
            cookies={"session_token": "invalid_token"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "unauthorized"

    @pytest.mark.asyncio
    async def test_logout_deletes_session(self, client: AsyncClient, sample_user_data: dict, db_session: AsyncSession) -> None:
        """Test that logout deletes session from database."""
        from src.models.session import Session
        from sqlalchemy import select
        
        # Register and login
        await client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        # Get session token
        session_token = login_response.cookies.get("session_token")
        
        # Check session exists
        result = await db_session.execute(select(Session))
        sessions = result.scalars().all()
        assert len(sessions) == 1
        
        # Logout
        await client.post(
            "/api/v1/auth/logout",
            cookies={"session_token": session_token}
        )
        
        # Check session is deleted
        result = await db_session.execute(select(Session))
        sessions = result.scalars().all()
        assert len(sessions) == 0

    @pytest.mark.asyncio
    async def test_logout_prevents_further_access(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test that logout prevents further authenticated access."""
        # Register and login
        await client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        # Get session token
        session_token = login_response.cookies.get("session_token")
        
        # Logout
        await client.post(
            "/api/v1/auth/logout",
            cookies={"session_token": session_token}
        )
        
        # Try to access protected endpoint with old token
        response = await client.get(
            "/api/v1/auth/me",
            cookies={"session_token": session_token}
        )
        
        assert response.status_code == 401