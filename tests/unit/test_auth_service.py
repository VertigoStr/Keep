"""Unit tests for auth service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.auth_service import AuthService
from src.models.user import User
from src.middleware.error_handler import EmailExistsError, InvalidCredentialsError, UnauthorizedError


@pytest.mark.unit
class TestAuthService:
    """Unit tests for authentication service."""

    @pytest.mark.asyncio
    async def test_register_user_success(self) -> None:
        """Test successful user registration."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_user_repo = AsyncMock()
        mock_user_repo.email_exists = AsyncMock(return_value=False)
        mock_user_repo.create_user = AsyncMock(return_value=User(id="1", email="test@example.com", password_hash="hash"))
        
        mock_password_service = MagicMock()
        mock_password_service.hash_password = MagicMock(return_value="hashed_password")
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.user_repository = mock_user_repo
        auth_service.password_service = mock_password_service
        
        # Test
        user = await auth_service.register_user("test@example.com", "password123")
        
        assert user.email == "test@example.com"
        mock_user_repo.email_exists.assert_called_once_with("test@example.com")
        mock_password_service.hash_password.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_register_user_email_exists(self) -> None:
        """Test registration with existing email raises error."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_user_repo = AsyncMock()
        mock_user_repo.email_exists = AsyncMock(return_value=True)
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.user_repository = mock_user_repo
        
        # Test
        with pytest.raises(EmailExistsError):
            await auth_service.register_user("test@example.com", "password123")

    @pytest.mark.asyncio
    async def test_login_user_success(self) -> None:
        """Test successful user login."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_user = User(id="1", email="test@example.com", password_hash="hashed_password")
        mock_user_repo = AsyncMock()
        mock_user_repo.get_user_by_email = AsyncMock(return_value=mock_user)
        
        mock_password_service = MagicMock()
        mock_password_service.verify_password = MagicMock(return_value=True)
        
        mock_session_repo = AsyncMock()
        mock_session_repo.create_session = AsyncMock()
        
        mock_security_utils = MagicMock()
        mock_security_utils.create_token = MagicMock(return_value="jwt_token")
        mock_security_utils.hash_token = MagicMock(return_value="token_hash")
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.user_repository = mock_user_repo
        auth_service.session_repository = mock_session_repo
        auth_service.password_service = mock_password_service
        auth_service.security_utils = mock_security_utils
        
        # Test
        user, token = await auth_service.login_user("test@example.com", "password123")
        
        assert user.email == "test@example.com"
        assert token == "jwt_token"
        mock_password_service.verify_password.assert_called_once_with("password123", "hashed_password")

    @pytest.mark.asyncio
    async def test_login_user_invalid_email(self) -> None:
        """Test login with invalid email raises error."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_user_repo = AsyncMock()
        mock_user_repo.get_user_by_email = AsyncMock(return_value=None)
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.user_repository = mock_user_repo
        
        # Test
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user("nonexistent@example.com", "password123")

    @pytest.mark.asyncio
    async def test_login_user_invalid_password(self) -> None:
        """Test login with invalid password raises error."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_user = User(id="1", email="test@example.com", password_hash="hashed_password")
        mock_user_repo = AsyncMock()
        mock_user_repo.get_user_by_email = AsyncMock(return_value=mock_user)
        
        mock_password_service = MagicMock()
        mock_password_service.verify_password = MagicMock(return_value=False)
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.user_repository = mock_user_repo
        auth_service.password_service = mock_password_service
        
        # Test
        with pytest.raises(InvalidCredentialsError):
            await auth_service.login_user("test@example.com", "wrong_password")

    @pytest.mark.asyncio
    async def test_logout_user_success(self) -> None:
        """Test successful user logout."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_session_obj = MagicMock()
        mock_session_obj.id = "session_id"
        
        mock_session_repo = AsyncMock()
        mock_session_repo.get_session_by_token_hash = AsyncMock(return_value=mock_session_obj)
        mock_session_repo.delete_session = AsyncMock(return_value=True)
        
        mock_security_utils = MagicMock()
        mock_security_utils.hash_token = MagicMock(return_value="token_hash")
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.session_repository = mock_session_repo
        auth_service.security_utils = mock_security_utils
        
        # Test
        await auth_service.logout_user("jwt_token")
        
        mock_session_repo.delete_session.assert_called_once_with("session_id")

    @pytest.mark.asyncio
    async def test_logout_user_no_session(self) -> None:
        """Test logout with no session raises error."""
        # Setup mocks
        mock_session = AsyncMock()
        mock_session_repo = AsyncMock()
        mock_session_repo.get_session_by_token_hash = AsyncMock(return_value=None)
        
        mock_security_utils = MagicMock()
        mock_security_utils.hash_token = MagicMock(return_value="token_hash")
        
        # Create service with mocked dependencies
        auth_service = AuthService.__new__(AuthService)
        auth_service.session = mock_session
        auth_service.session_repository = mock_session_repo
        auth_service.security_utils = mock_security_utils
        
        # Test
        with pytest.raises(UnauthorizedError):
            await auth_service.logout_user("invalid_token")