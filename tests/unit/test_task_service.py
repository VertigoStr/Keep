"""Unit tests for TaskService."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.task_service import TaskService
from src.schemas.task import TaskCreate, TaskUpdate
from src.models.task import TaskStatus
from src.middleware.error_handler import NotFoundError, ForbiddenError


@pytest.mark.asyncio
async def test_create_task(db_session: AsyncSession) -> None:
    """Test creating a new task."""
    service = TaskService(db_session)

    user_id = "test-user-id"
    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    task_response = await service.create_task(user_id, task_data)

    assert task_response.id is not None
    assert task_response.title == "Test Task"
    assert task_response.description == "Test Description"
    assert task_response.due_date == date(2026, 3, 15)
    assert task_response.status == TaskStatus.TODO


@pytest.mark.asyncio
async def test_create_task_with_default_status(db_session: AsyncSession) -> None:
    """Test creating a task with default status."""
    service = TaskService(db_session)

    task_data = TaskCreate(
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
    )

    task_response = await service.create_task("test-user-id", task_data)

    assert task_response.status == TaskStatus.TODO


@pytest.mark.asyncio
async def test_get_user_tasks(db_session: AsyncSession) -> None:
    """Test getting all tasks for a user."""
    service = TaskService(db_session)

    user_id = "test-user-id"

    # Create multiple tasks
    await service.create_task(
        user_id,
        TaskCreate(
            title="Task 1",
            description="Description 1",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )
    await service.create_task(
        user_id,
        TaskCreate(
            title="Task 2",
            description="Description 2",
            due_date=date(2026, 3, 16),
            status=TaskStatus.IN_PROGRESS,
        ),
    )

    # Get tasks
    tasks_response = await service.get_user_tasks(user_id)

    assert len(tasks_response.tasks) == 2
    assert all(task.title in ["Task 1", "Task 2"] for task in tasks_response.tasks)


@pytest.mark.asyncio
async def test_get_user_tasks_empty(db_session: AsyncSession) -> None:
    """Test getting tasks for a user with no tasks."""
    service = TaskService(db_session)

    tasks_response = await service.get_user_tasks("non-existent-user")

    assert tasks_response.tasks == []


@pytest.mark.asyncio
async def test_get_task_by_id(db_session: AsyncSession) -> None:
    """Test getting a specific task by ID."""
    service = TaskService(db_session)

    user_id = "test-user-id"

    # Create a task
    created_task = await service.create_task(
        user_id,
        TaskCreate(
            title="Test Task",
            description="Test Description",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )

    # Get the task
    task_response = await service.get_task_by_id(created_task.id, user_id)

    assert task_response.id == created_task.id
    assert task_response.title == "Test Task"


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(db_session: AsyncSession) -> None:
    """Test getting a non-existent task."""
    service = TaskService(db_session)

    with pytest.raises(NotFoundError, match="Task not found"):
        await service.get_task_by_id("non-existent-id", "test-user-id")


@pytest.mark.asyncio
async def test_get_task_by_id_not_owner(db_session: AsyncSession) -> None:
    """Test getting a task owned by another user."""
    service = TaskService(db_session)

    # Create a task for user1
    created_task = await service.create_task(
        "user1",
        TaskCreate(
            title="Test Task",
            description="Test Description",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )

    # Try to get the task as user2
    with pytest.raises(ForbiddenError, match="You do not have permission"):
        await service.get_task_by_id(created_task.id, "user2")


@pytest.mark.asyncio
async def test_update_task_status(db_session: AsyncSession) -> None:
    """Test updating a task."""
    service = TaskService(db_session)

    user_id = "test-user-id"

    # Create a task
    created_task = await service.create_task(
        user_id,
        TaskCreate(
            title="Original Title",
            description="Original Description",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )

    # Update the task
    update_data = TaskUpdate(
        title="Updated Title",
        status=TaskStatus.IN_PROGRESS,
    )

    updated_task = await service.update_task_status(
        created_task.id, user_id, update_data
    )

    assert updated_task.id == created_task.id
    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Original Description"
    assert updated_task.status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_task_status_not_found(db_session: AsyncSession) -> None:
    """Test updating a non-existent task."""
    service = TaskService(db_session)

    update_data = TaskUpdate(status=TaskStatus.DONE)

    with pytest.raises(NotFoundError, match="Task not found"):
        await service.update_task_status("non-existent-id", "test-user-id", update_data)


@pytest.mark.asyncio
async def test_update_task_status_not_owner(db_session: AsyncSession) -> None:
    """Test updating a task owned by another user."""
    service = TaskService(db_session)

    # Create a task for user1
    created_task = await service.create_task(
        "user1",
        TaskCreate(
            title="Test Task",
            description="Test Description",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )

    # Try to update the task as user2
    update_data = TaskUpdate(status=TaskStatus.DONE)

    with pytest.raises(ForbiddenError, match="You do not have permission"):
        await service.update_task_status(created_task.id, "user2", update_data)


@pytest.mark.asyncio
async def test_delete_task(db_session: AsyncSession) -> None:
    """Test deleting a task."""
    service = TaskService(db_session)

    user_id = "test-user-id"

    # Create a task
    created_task = await service.create_task(
        user_id,
        TaskCreate(
            title="Test Task",
            description="Test Description",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )

    # Delete the task
    await service.delete_task(created_task.id, user_id)

    # Verify task is deleted
    with pytest.raises(NotFoundError, match="Task not found"):
        await service.get_task_by_id(created_task.id, user_id)


@pytest.mark.asyncio
async def test_delete_task_not_found(db_session: AsyncSession) -> None:
    """Test deleting a non-existent task."""
    service = TaskService(db_session)

    with pytest.raises(NotFoundError, match="Task not found"):
        await service.delete_task("non-existent-id", "test-user-id")


@pytest.mark.asyncio
async def test_delete_task_not_owner(db_session: AsyncSession) -> None:
    """Test deleting a task owned by another user."""
    service = TaskService(db_session)

    # Create a task for user1
    created_task = await service.create_task(
        "user1",
        TaskCreate(
            title="Test Task",
            description="Test Description",
            due_date=date(2026, 3, 15),
            status=TaskStatus.TODO,
        ),
    )

    # Try to delete the task as user2
    with pytest.raises(ForbiddenError, match="You do not have permission"):
        await service.delete_task(created_task.id, "user2")