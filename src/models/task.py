"""Task SQLAlchemy model and status enum."""

from enum import Enum
from sqlalchemy import Column, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.models import BaseModel


class TaskStatus(str, Enum):
    """Task status enum with predefined values."""

    TODO = "к выполнению"
    IN_PROGRESS = "в работу"
    HAS_ISSUE = "возникла проблема"
    DONE = "сделано"
    CANCELLED = "отмена"


class Task(BaseModel):
    """Task model representing a user task."""

    __tablename__ = "tasks"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(5000), nullable=False, default="")
    due_date = Column(Date, nullable=False, index=True)
    status = Column(String(50), nullable=False, default=TaskStatus.TODO, index=True)

    # Relationship
    user = relationship("User", backref="tasks")

    def __repr__(self) -> str:
        """String representation of Task."""
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"


__all__ = ["Task", "TaskStatus"]