"""Pydantic schemas for authentication requests and responses."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserResponse(BaseModel):
    """User response schema."""

    id: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    """Registration request schema."""

    email: EmailStr = Field(..., max_length=255, description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    password_confirm: str = Field(..., description="Password confirmation")

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        """Validate password meets complexity requirements."""
        from src.utils.validators import validate_password_complexity
        
        if not validate_password_complexity(v):
            raise ValueError(
                "Password must be at least 8 characters, "
                "contain at least 1 uppercase letter, 1 digit, and 1 special character"
            )
        return v

    @field_validator('password_confirm')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Validate password confirmation matches password."""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError("Passwords do not match")
        return v


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class LoginResponse(BaseModel):
    """Login response schema."""

    user: UserResponse


class LogoutResponse(BaseModel):
    """Logout response schema."""

    message: str = "Logged out successfully"


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str
    message: str
    details: Optional[dict] = None


__all__ = [
    "UserResponse",
    "RegisterRequest",
    "LoginRequest",
    "LoginResponse",
    "LogoutResponse",
    "ErrorResponse"
]