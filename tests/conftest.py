"""Pytest configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import get_db
from src.models import Base
from src.models.user import User
from src.models.session import Session
from src.models.failed_login import FailedLoginAttempt
from src.models.task import Task
from src.models.board import Board
from src.models.column import Column
from src.config import get_settings

settings = get_settings()

# Test database URL (in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
test_async_session_factory = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with test_async_session_factory() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database session override."""
    
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!"
    }


@pytest.fixture
def sample_login_data() -> dict:
    """Sample login data for testing."""
    return {
        "email": "test@example.com",
        "password": "SecurePass123!"
    }


@pytest.fixture
async def auth_headers(client: AsyncClient, sample_user_data: dict) -> dict:
    """Create authenticated user and return auth headers."""
    # Register user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    
    # Login to get token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]
    
    return {"Cookie": f"session_token={token}"}