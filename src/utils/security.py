"""JWT security utilities."""

import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from src.config import get_settings
from src.database import get_db
from src.repositories.session_repository import SessionRepository
from src.middleware.error_handler import UnauthorizedError


class SecurityUtils:
    """Utilities for JWT token generation and verification."""

    def __init__(self) -> None:
        """Initialize security utils with settings."""
        settings = get_settings()
        self.secret_key = settings.jwt_secret
        self.algorithm = "HS256"
        self.expiration_seconds = settings.jwt_expiration_seconds

    def create_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT token.

        Args:
            user_id: User ID
            email: User email
            expires_delta: Custom expiration time delta

        Returns:
            JWT token string
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.expiration_seconds)

        to_encode = {
            "sub": user_id,
            "email": email,
            "iat": datetime.utcnow(),
            "exp": expire
        }

        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def hash_token(self, token: str) -> str:
        """Hash a JWT token for storage.

        Args:
            token: JWT token string

        Returns:
            SHA-256 hash of the token
        """
        return hashlib.sha256(token.encode()).hexdigest()


# HTTP Bearer security scheme (optional to allow cookie-based auth)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Dict:
    """Get current authenticated user from JWT token.

    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User payload from JWT token

    Raises:
        UnauthorizedError: If token is invalid or session not found
    """
    # Try to get token from Authorization header first
    token = credentials.credentials if credentials else None
    
    # If no token in header, try cookie
    if not token:
        token = request.cookies.get("session_token")
    
    if not token:
        raise UnauthorizedError()
    
    # Verify token
    security_utils = SecurityUtils()
    payload = security_utils.verify_token(token)
    
    if not payload:
        raise UnauthorizedError()
    
    # Check if session exists
    session_repo = SessionRepository(db)
    token_hash = security_utils.hash_token(token)
    session = await session_repo.get_session_by_token_hash(token_hash)
    
    if not session:
        raise UnauthorizedError()
    
    return payload


async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> str:
    """Get current authenticated user ID from JWT token.

    Args:
        request: FastAPI request object
        credentials: HTTP Bearer credentials
        db: Database session

    Returns:
        User ID string

    Raises:
        UnauthorizedError: If token is invalid or session not found
    """
    payload = await get_current_user(request, credentials, db)
    return payload["sub"]


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Optional[Dict]:
    """Get current user if authenticated, None otherwise.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User payload from JWT token if authenticated, None otherwise
    """
    try:
        return await get_current_user(request, db=db)
    except UnauthorizedError:
        return None


__all__ = ["SecurityUtils", "get_current_user", "get_current_user_id", "get_optional_user"]