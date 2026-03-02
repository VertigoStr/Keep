"""Session SQLAlchemy model."""

from sqlalchemy import Column, String, DateTime, ForeignKey
from src.models import BaseModel


class Session(BaseModel):
    """Model representing a user session."""

    __tablename__ = "sessions"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)

    def __repr__(self) -> str:
        """String representation of Session."""
        return f"<Session(id={self.id}, user_id={self.user_id}, expires_at={self.expires_at})>"


__all__ = ["Session"]