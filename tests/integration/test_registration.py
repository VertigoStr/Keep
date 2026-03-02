"""Integration tests for user registration flow."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.integration
class TestRegistrationFlow:
    """Integration tests for registration flow."""

    @pytest.mark.asyncio
    async def test_complete_registration_flow(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test complete registration flow from request to database."""
        # Register user
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == sample_user_data["email"].lower()
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_registration_creates_user_in_db(self, client: AsyncClient, sample_user_data: dict, db_session: AsyncSession) -> None:
        """Test that registration creates user in database."""
        from src.models.user import User
        from sqlalchemy import select
        
        # Register user
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Check user exists in database
        result = await db_session.execute(
            select(User).where(User.email == sample_user_data["email"].lower())
        )
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.email == sample_user_data["email"].lower()
        assert user.password_hash is not None
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_registration_password_is_hashed(self, client: AsyncClient, sample_user_data: dict, db_session: AsyncSession) -> None:
        """Test that password is hashed in database."""
        from src.models.user import User
        from sqlalchemy import select
        
        # Register user
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Get user from database
        result = await db_session.execute(
            select(User).where(User.email == sample_user_data["email"].lower())
        )
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.password_hash != sample_user_data["password"]
        assert user.password_hash.startswith("$2b$")  # bcrypt hash prefix

    @pytest.mark.asyncio
    async def test_registration_email_case_insensitive(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Test that email is stored in lowercase."""
        from src.models.user import User
        from sqlalchemy import select
        
        # Register with uppercase email
        data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        await client.post("/api/v1/auth/register", json=data)
        
        # Check email is lowercase in database
        result = await db_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.email == "test@example.com"

    @pytest.mark.asyncio
    async def test_duplicate_registration_fails(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test that duplicate registration fails."""
        # First registration
        response1 = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response1.status_code == 201
        
        # Second registration with same email
        response2 = await client.post("/api/v1/auth/register", json=sample_user_data)
        assert response2.status_code == 409

    @pytest.mark.asyncio
    async def test_registration_with_trimmed_email(self, client: AsyncClient, db_session: AsyncSession) -> None:
        """Test that email is trimmed of whitespace."""
        from src.models.user import User
        from sqlalchemy import select
        
        # Register with email containing whitespace
        data = {
            "email": "  test@example.com  ",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        await client.post("/api/v1/auth/register", json=data)
        
        # Check email is trimmed in database
        result = await db_session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one_or_none()
        
        assert user is not None
        assert user.email == "test@example.com"