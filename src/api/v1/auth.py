"""Authentication API endpoints."""

from datetime import datetime
from fastapi import APIRouter, Depends, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.auth_service import AuthService
from src.services.rate_limit_service import RateLimitService
from src.utils.security import get_current_user
from src.middleware.error_handler import TooManyAttemptsError, InvalidCredentialsError, UnauthorizedError
from src.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    LoginResponse,
    LogoutResponse,
    ErrorResponse
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        409: {"model": ErrorResponse, "description": "Email already exists"}
    }
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Register a new user account.

    Args:
        request: Registration request with email and password
        db: Database session

    Returns:
        Created user information

    Raises:
        ValidationError: If password doesn't meet requirements or passwords don't match
        EmailExistsError: If email already exists
    """
    auth_service = AuthService(db)
    user = await auth_service.register_user(
        email=request.email,
        password=request.password
    )
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Too many attempts"}
    }
)
async def login(
    request: Request,
    response: Response,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> LoginResponse:
    """Authenticate a user and create a session.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        login_data: Login request with email and password
        db: Database session

    Returns:
        Login response with user information

    Raises:
        ValidationError: If request data is invalid
        InvalidCredentialsError: If email or password is invalid
        TooManyAttemptsError: If rate limit exceeded
    """
    # Get client IP
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent")

    # Check rate limit
    rate_limit_service = RateLimitService(db)
    if not await rate_limit_service.check_rate_limit(login_data.email, client_ip, user_agent):
        raise TooManyAttemptsError()

    # Authenticate user
    auth_service = AuthService(db)
    try:
        user, token = await auth_service.login_user(login_data.email, login_data.password)
    except InvalidCredentialsError:
        # Rate limit check already recorded the attempt
        raise

    # Set HTTP-only cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="strict",
        max_age=86400  # 24 hours
    )

    return LoginResponse(user=UserResponse.model_validate(user))


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def logout(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> LogoutResponse:
    """Logout the current user and terminate their session.

    Args:
        request: FastAPI request object
        response: FastAPI response object
        current_user: Current authenticated user
        db: Database session

    Returns:
        Logout response

    Raises:
        UnauthorizedError: If not authenticated
    """
    # Get token from cookie
    token = request.cookies.get("session_token")
    
    if token:
        # Delete session
        auth_service = AuthService(db)
        await auth_service.logout_user(token)
    
    # Clear cookie
    response.delete_cookie(
        key="session_token",
        httponly=True,
        samesite="strict"
    )
    
    return LogoutResponse()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"}
    }
)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
) -> UserResponse:
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        User information
    """
    return UserResponse(
        id=current_user["sub"],
        email=current_user["email"],
        created_at=datetime.fromtimestamp(current_user.get("iat", 0))
    )


__all__ = ["router"]