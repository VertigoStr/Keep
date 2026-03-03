"""Task API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.task_service import TaskService
from src.utils.security import get_current_user
from src.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
    TaskDeleteResponse,
)

router = APIRouter()


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation error"},
        401: {"description": "Authentication required"},
    },
)
async def create_task(
    task_data: TaskCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new task for the authenticated user.

    Args:
        task_data: Task creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created task response

    Raises:
        ValidationError: If request data is invalid
        UnauthorizedError: If not authenticated
    """
    task_service = TaskService(db)
    return await task_service.create_task(
        user_id=current_user["sub"],
        task_data=task_data,
    )


@router.get(
    "/tasks",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authentication required"},
    },
)
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """Get all tasks for the authenticated user.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of tasks for the user

    Raises:
        UnauthorizedError: If not authenticated
    """
    task_service = TaskService(db)
    return await task_service.get_user_tasks(user_id=current_user["sub"])


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Not task owner"},
        404: {"description": "Task not found"},
    },
)
async def get_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Get a specific task by ID.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Task response

    Raises:
        UnauthorizedError: If not authenticated
        ForbiddenError: If not task owner
        NotFoundError: If task not found
    """
    task_service = TaskService(db)
    return await task_service.get_task_by_id(
        task_id=task_id,
        user_id=current_user["sub"],
    )


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Validation error"},
        401: {"description": "Authentication required"},
        403: {"description": "Not task owner"},
        404: {"description": "Task not found"},
    },
)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a specific task.

    Args:
        task_id: Task ID
        task_data: Task update data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated task response

    Raises:
        ValidationError: If request data is invalid
        UnauthorizedError: If not authenticated
        ForbiddenError: If not task owner
        NotFoundError: If task not found
    """
    task_service = TaskService(db)
    return await task_service.update_task_status(
        task_id=task_id,
        user_id=current_user["sub"],
        task_data=task_data,
    )


@router.delete(
    "/tasks/{task_id}",
    response_model=TaskDeleteResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Not task owner"},
        404: {"description": "Task not found"},
    },
)
async def delete_task(
    task_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskDeleteResponse:
    """Delete a specific task.

    Args:
        task_id: Task ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Deletion confirmation

    Raises:
        UnauthorizedError: If not authenticated
        ForbiddenError: If not task owner
        NotFoundError: If task not found
    """
    task_service = TaskService(db)
    await task_service.delete_task(
        task_id=task_id,
        user_id=current_user["sub"],
    )
    return TaskDeleteResponse()


__all__ = ["router"]