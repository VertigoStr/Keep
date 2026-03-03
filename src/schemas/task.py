"""Task Pydantic schemas for request/response validation."""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from src.models.task import TaskStatus


class TaskBase(BaseModel):
    """Base task schema with common fields."""

    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str = Field(
        default="",
        max_length=5000,
        description="Task description (0-5000 characters)"
    )
    due_date: date = Field(..., description="Due date in YYYY-MM-DD format")
    status: str = Field(
        default=TaskStatus.TODO,
        description="Task status from predefined list"
    )

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is one of the predefined values."""
        valid_statuses = [status.value for status in TaskStatus]
        if v not in valid_statuses:
            raise ValueError(
                f"Invalid status value. Must be one of: {', '.join(valid_statuses)}"
            )
        return v


class TaskCreate(TaskBase):
    """Schema for creating a new task."""

    pass


class TaskUpdate(BaseModel):
    """Schema for updating an existing task."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    due_date: Optional[date] = None
    status: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        """Validate that status is one of the predefined values if provided."""
        if v is not None:
            valid_statuses = [status.value for status in TaskStatus]
            if v not in valid_statuses:
                raise ValueError(
                    f"Invalid status value. Must be one of: {', '.join(valid_statuses)}"
                )
        return v


class TaskResponse(TaskBase):
    """Schema for task response."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class TaskListResponse(BaseModel):
    """Schema for task list response."""

    tasks: list[TaskResponse]


class TaskDeleteResponse(BaseModel):
    """Schema for task deletion response."""

    message: str = "Task deleted successfully"


__all__ = [
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskListResponse",
    "TaskDeleteResponse",
]