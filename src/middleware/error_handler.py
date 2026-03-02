"""Error handling middleware for FastAPI."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str, error_code: str = "internal_error", status_code: int = 500):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "validation_error", status.HTTP_400_BAD_REQUEST)
        self.details = details


class UnauthorizedError(AppError):
    """Unauthorized error."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, "unauthorized", status.HTTP_401_UNAUTHORIZED)


class InvalidCredentialsError(AppError):
    """Invalid credentials error."""

    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(message, "invalid_credentials", status.HTTP_401_UNAUTHORIZED)


class EmailExistsError(AppError):
    """Email already exists error."""

    def __init__(self, message: str = "User with this email already exists"):
        super().__init__(message, "email_exists", status.HTTP_409_CONFLICT)


class TooManyAttemptsError(AppError):
    """Too many attempts error."""

    def __init__(self, message: str = "Too many failed login attempts. Please try again in 15 minutes."):
        super().__init__(message, "too_many_attempts", status.HTTP_429_TOO_MANY_REQUESTS)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors."""
    logger.error(f"App error: {exc.error_code} - {exc.message}")
    
    response_data = {
        "error": exc.error_code,
        "message": exc.message
    }
    
    if hasattr(exc, "details") and exc.details:
        response_data["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle FastAPI validation errors."""
    logger.error(f"Validation error: {exc.errors()}")
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "validation_error",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Handle database integrity errors."""
    logger.error(f"Integrity error: {str(exc)}")
    
    if "email" in str(exc).lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "email_exists",
                "message": "User with this email already exists"
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "Database error occurred"
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "internal_error",
            "message": "An unexpected error occurred"
        }
    )


__all__ = [
    "AppError",
    "ValidationError",
    "UnauthorizedError",
    "InvalidCredentialsError",
    "EmailExistsError",
    "TooManyAttemptsError",
    "app_error_handler",
    "validation_error_handler",
    "integrity_error_handler",
    "general_exception_handler"
]