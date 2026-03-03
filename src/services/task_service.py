"""Task service for task business logic."""

import logging
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.task_repository import TaskRepository
from src.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from src.middleware.error_handler import NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize task service with database session."""
        self.session = session
        self.task_repository = TaskRepository(session)

    async def create_task(
        self,
        user_id: str,
        task_data: TaskCreate,
    ) -> TaskResponse:
        """Create a new task for the user.

        Args:
            user_id: ID of the user creating the task
            task_data: Task creation data

        Returns:
            Created task response

        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Creating task for user {user_id}: {task_data.title}")

        task = await self.task_repository.create_task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            status=task_data.status,
        )

        logger.info(f"Task created successfully: {task.id}")
        return TaskResponse.model_validate(task)

    async def get_user_tasks(self, user_id: str) -> TaskListResponse:
        """Get all tasks for the authenticated user.

        Args:
            user_id: ID of the user

        Returns:
            List of tasks for the user
        """
        logger.info(f"Retrieving tasks for user {user_id}")

        tasks = await self.task_repository.get_user_tasks(user_id)

        logger.info(f"Found {len(tasks)} tasks for user {user_id}")
        return TaskListResponse(
            tasks=[TaskResponse.model_validate(task) for task in tasks]
        )

    async def get_task_by_id(
        self,
        task_id: str,
        user_id: str,
    ) -> TaskResponse:
        """Get a specific task by ID.

        Args:
            task_id: Task ID
            user_id: ID of the user requesting the task

        Returns:
            Task response

        Raises:
            NotFoundError: If task not found
            ForbiddenError: If user is not the task owner
        """
        logger.info(f"Retrieving task {task_id} for user {user_id}")

        # Check if task exists and user is owner
        if not await self.task_repository.is_task_owner(task_id, user_id):
            if not await self.task_repository.task_exists(task_id):
                raise NotFoundError("Task not found")
            raise ForbiddenError("You do not have permission to access this task")

        task = await self.task_repository.get_task_by_id(task_id)
        return TaskResponse.model_validate(task)

    async def update_task_status(
        self,
        task_id: str,
        user_id: str,
        task_data: TaskUpdate,
    ) -> TaskResponse:
        """Update a task.

        Args:
            task_id: Task ID
            user_id: ID of the user updating the task
            task_data: Task update data

        Returns:
            Updated task response

        Raises:
            NotFoundError: If task not found
            ForbiddenError: If user is not the task owner
        """
        logger.info(f"Updating task {task_id} for user {user_id}")

        # Check ownership
        if not await self.task_repository.is_task_owner(task_id, user_id):
            if not await self.task_repository.task_exists(task_id):
                raise NotFoundError("Task not found")
            raise ForbiddenError("You do not have permission to modify this task")

        # Update task
        task = await self.task_repository.update_task(
            task_id=task_id,
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            status=task_data.status,
        )

        logger.info(f"Task {task_id} updated successfully")
        return TaskResponse.model_validate(task)

    async def delete_task(
        self,
        task_id: str,
        user_id: str,
    ) -> None:
        """Delete a task.

        Args:
            task_id: Task ID
            user_id: ID of the user deleting the task

        Raises:
            NotFoundError: If task not found
            ForbiddenError: If user is not the task owner
        """
        logger.info(f"Deleting task {task_id} for user {user_id}")

        # Check ownership
        if not await self.task_repository.is_task_owner(task_id, user_id):
            if not await self.task_repository.task_exists(task_id):
                raise NotFoundError("Task not found")
            raise ForbiddenError("You do not have permission to delete this task")

        # Delete task
        await self.task_repository.delete_task(task_id)

        logger.info(f"Task {task_id} deleted successfully")


__all__ = ["TaskService"]