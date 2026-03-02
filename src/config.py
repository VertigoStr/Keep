"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/trello",
        description="PostgreSQL database connection URL"
    )

    # JWT
    jwt_secret: str = Field(
        default="your-secret-key-here",
        description="Secret key for JWT token signing"
    )
    jwt_expiration_seconds: int = Field(
        default=86400,
        description="JWT token expiration time in seconds (24 hours)"
    )

    # Bcrypt
    bcrypt_rounds: int = Field(
        default=12,
        description="Bcrypt work factor for password hashing"
    )

    # Application
    app_name: str = Field(
        default="Trello Auth",
        description="Application name"
    )
    app_env: str = Field(
        default="development",
        description="Application environment (development/production)"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode flag"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


__all__ = ["Settings", "get_settings"]