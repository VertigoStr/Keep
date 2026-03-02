"""User SQLAlchemy model."""

from sqlalchemy import Column, String
from src.models import BaseModel


class User(BaseModel):
    """User model representing a registered user."""

    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, email={self.email})>"


__all__ = ["User"]