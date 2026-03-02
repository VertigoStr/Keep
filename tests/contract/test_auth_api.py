"""Contract tests for authentication API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.contract
class TestAuthAPIContract:
    """Contract tests for authentication API."""

    @pytest.mark.asyncio
    async def test_register_contract_success(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test successful registration contract."""
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == sample_user_data["email"]
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_contract_passwords_dont_match(self, client: AsyncClient) -> None:
        """Test registration with non-matching passwords."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!"
        }
        response = await client.post("/api/v1/auth/register", json=data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "validation_error"
        assert "Passwords do not match" in data["message"]

    @pytest.mark.asyncio
    async def test_register_contract_invalid_email(self, client: AsyncClient) -> None:
        """Test registration with invalid email format."""
        data = {
            "email": "invalid-email",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!"
        }
        response = await client.post("/api/v1/auth/register", json=data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "validation_error"

    @pytest.mark.asyncio
    async def test_register_contract_weak_password(self, client: AsyncClient) -> None:
        """Test registration with weak password."""
        data = {
            "email": "test@example.com",
            "password": "weak",
            "password_confirm": "weak"
        }
        response = await client.post("/api/v1/auth/register", json=data)
        
        assert response.status_code == 400
        data = response.json()
        assert data["error"] == "validation_error"

    @pytest.mark.asyncio
    async def test_register_contract_email_exists(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test registration with existing email."""
        # First registration
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Second registration with same email
        response = await client.post("/api/v1/auth/register", json=sample_user_data)
        
        assert response.status_code == 409
        data = response.json()
        assert data["error"] == "email_exists"

    @pytest.mark.asyncio
    async def test_register_contract_missing_fields(self, client: AsyncClient) -> None:
        """Test registration with missing fields."""
        data = {
            "email": "test@example.com"
        }
        response = await client.post("/api/v1/auth/register", json=data)
        
        assert response.status_code == 422  # FastAPI validation error

    @pytest.mark.asyncio
    async def test_login_contract_success(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test successful login contract."""
        # Register user first
        await client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Login
        login_data = {
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == sample_user_data["email"]
        assert "id" in data["user"]
        
        # Check for session cookie
        cookies = response.cookies
        assert "session_token" in cookies

    @pytest.mark.asyncio
    async def test_login_contract_invalid_credentials(self, client: AsyncClient) -> None:
        """Test login with invalid credentials."""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPass123!"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "invalid_credentials"

    @pytest.mark.asyncio
    async def test_login_contract_rate_limited(self, client: AsyncClient) -> None:
        """Test login rate limiting."""
        login_data = {
            "email": "test@example.com",
            "password": "WrongPass123!"
        }
        
        # Make 3 failed attempts
        for _ in range(3):
            await client.post("/api/v1/auth/login", json=login_data)
        
        # 4th attempt should be rate limited
        response = await client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "too_many_attempts"
        assert "Retry-After" in response.headers

    @pytest.mark.asyncio
    async def test_logout_contract_success(self, client: AsyncClient, sample_user_data: dict) -> None:
        """Test successful logout contract."""
        # Register and login
        await client.post("/api/v1/auth/register", json=sample_user_data)
        login_response = await client.post("/api/v1/auth/login", json={
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        })
        
        # Get session token
        session_token = login_response.cookies.get("session_token")
        
        # Logout
        response = await client.post(
            "/api/v1/auth/logout",
            cookies={"session_token": session_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Logged out successfully"
        
        # Check cookie is cleared
        cookies = response.cookies
        assert cookies.get("session_token") == "" or cookies.get("session_token") is None

    @pytest.mark.asyncio
    async def test_logout_contract_unauthorized(self, client: AsyncClient) -> None:
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401
        data = response.json()
        assert data["error"] == "unauthorized"