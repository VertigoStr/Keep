"""Task-specific validators."""

from datetime import date, datetime
from typing import Optional
from src.models.task import TaskStatus


def validate_task_title(title: str) -> str:
    """Validate task title.

    Args:
        title: Task title to validate

    Returns:
        Validated title

    Raises:
        ValueError: If title is invalid
    """
    if not title or not title.strip():
        raise ValueError("Title is required")
    if len(title) > 255:
        raise ValueError("Title must be at most 255 characters")
    return title.strip()


def validate_task_description(description: Optional[str]) -> str:
    """Validate task description.

    Args:
        description: Task description to validate

    Returns:
        Validated description (empty string if None)

    Raises:
        ValueError: If description is too long
    """
    if description is None:
        return ""
    if len(description) > 5000:
        raise ValueError("Description must be at most 5000 characters")
    return description


def validate_task_due_date(due_date: date) -> date:
    """Validate task due date.

    Args:
        due_date: Due date to validate

    Returns:
        Validated due date

    Raises:
        ValueError: If date is invalid
    """
    if not isinstance(due_date, date):
        raise ValueError("Invalid date format. Use YYYY-MM-DD")
    return due_date


def validate_task_status(status: str) -> str:
    """Validate task status.

    Args:
        status: Status to validate

    Returns:
        Validated status

    Raises:
        ValueError: If status is invalid
    """
    valid_statuses = [s.value for s in TaskStatus]
    if status not in valid_statuses:
        raise ValueError(
            f"Invalid status value. Must be one of: {', '.join(valid_statuses)}"
        )
    return status


def validate_task_update_data(
    title: Optional[str] = None,
    description: Optional[str] = None,
    due_date: Optional[date] = None,
    status: Optional[str] = None,
) -> dict:
    """Validate task update data.

    Args:
        title: Optional title to validate
        description: Optional description to validate
        due_date: Optional due date to validate
        status: Optional status to validate

    Returns:
        Dictionary with validated fields

    Raises:
        ValueError: If any field is invalid
    """
    validated = {}

    if title is not None:
        validated["title"] = validate_task_title(title)

    if description is not None:
        validated["description"] = validate_task_description(description)

    if due_date is not None:
        validated["due_date"] = validate_task_due_date(due_date)

    if status is not None:
        validated["status"] = validate_task_status(status)

    return validated


__all__ = [
    "validate_task_title",
    "validate_task_description",
    "validate_task_due_date",
    "validate_task_status",
    "validate_task_update_data",
]