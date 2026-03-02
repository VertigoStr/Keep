"""FailedLoginAttempt SQLAlchemy model."""

from sqlalchemy import Column, String, DateTime
from datetime import datetime
from src.models import BaseModel


class FailedLoginAttempt(BaseModel):
    """Model representing a failed login attempt."""

    __tablename__ = "failed_login_attempts"

    email = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    user_agent = Column(String(500), nullable=True)

    def __repr__(self) -> str:
        """String representation of FailedLoginAttempt."""
        return f"<FailedLoginAttempt(id={self.id}, email={self.email}, ip={self.ip_address})>"


__all__ = ["FailedLoginAttempt"]