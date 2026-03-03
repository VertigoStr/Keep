"""Task repository for data access operations."""

from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from src.models.task import Task


class TaskRepository:
    """Repository for Task model data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: str,
        due_date: date,
        status: str,
    ) -> Task:
        """Create a new task.

        Args:
            user_id: ID of the user who owns the task
            title: Task title
            description: Task description
            due_date: Task due date
            status: Task status

        Returns:
            Created Task instance
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task instance if found, None otherwise
        """
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_user_tasks(self, user_id: str) -> list[Task]:
        """Get all tasks for a specific user.

        Args:
            user_id: User ID

        Returns:
            List of Task instances
        """
        result = await self.session.execute(
            select(Task).where(Task.user_id == user_id)
        )
        return list(result.scalars().all())

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[date] = None,
        status: Optional[str] = None,
    ) -> Optional[Task]:
        """Update an existing task.

        Args:
            task_id: Task ID
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            status: New status (optional)

        Returns:
            Updated Task instance if found, None otherwise
        """
        task = await self.get_task_by_id(task_id)
        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if status is not None:
            task.status = status

        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: Task ID

        Returns:
            True if task was deleted, False if not found
        """
        task = await self.get_task_by_id(task_id)
        if not task:
            return False

        await self.session.delete(task)
        await self.session.commit()
        return True

    async def task_exists(self, task_id: str) -> bool:
        """Check if task exists.

        Args:
            task_id: Task ID

        Returns:
            True if task exists, False otherwise
        """
        result = await self.session.execute(
            select(Task).where(Task.id == task_id)
        )
        return result.scalar_one_or_none() is not None

    async def is_task_owner(self, task_id: str, user_id: str) -> bool:
        """Check if user is the owner of the task.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            True if user owns the task, False otherwise
        """
        result = await self.session.execute(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        )
        return result.scalar_one_or_none() is not None


__all__ = ["TaskRepository"]