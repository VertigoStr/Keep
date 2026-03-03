"""Unit tests for TaskRepository."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.task_repository import TaskRepository
from src.models.task import Task, TaskStatus


@pytest.mark.asyncio
async def test_create_task(db_session: AsyncSession) -> None:
    """Test creating a new task."""
    repo = TaskRepository(db_session)

    user_id = "test-user-id"
    task = await repo.create_task(
        user_id=user_id,
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    assert task.id is not None
    assert task.user_id == user_id
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.due_date == date(2026, 3, 15)
    assert task.status == TaskStatus.TODO


@pytest.mark.asyncio
async def test_create_task_with_default_description(db_session: AsyncSession) -> None:
    """Test creating a task with default empty description."""
    repo = TaskRepository(db_session)

    task = await repo.create_task(
        user_id="test-user-id",
        title="Test Task",
        description="",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    assert task.description == ""


@pytest.mark.asyncio
async def test_get_task_by_id(db_session: AsyncSession) -> None:
    """Test getting a task by ID."""
    repo = TaskRepository(db_session)

    # Create a task first
    created_task = await repo.create_task(
        user_id="test-user-id",
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Get the task by ID
    task = await repo.get_task_by_id(created_task.id)

    assert task is not None
    assert task.id == created_task.id
    assert task.title == "Test Task"


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(db_session: AsyncSession) -> None:
    """Test getting a non-existent task by ID."""
    repo = TaskRepository(db_session)

    task = await repo.get_task_by_id("non-existent-id")

    assert task is None


@pytest.mark.asyncio
async def test_get_user_tasks(db_session: AsyncSession) -> None:
    """Test getting all tasks for a user."""
    repo = TaskRepository(db_session)

    user_id = "test-user-id"

    # Create multiple tasks for the user
    await repo.create_task(
        user_id=user_id,
        title="Task 1",
        description="Description 1",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )
    await repo.create_task(
        user_id=user_id,
        title="Task 2",
        description="Description 2",
        due_date=date(2026, 3, 16),
        status=TaskStatus.IN_PROGRESS,
    )

    # Create a task for another user
    await repo.create_task(
        user_id="other-user-id",
        title="Other Task",
        description="Other Description",
        due_date=date(2026, 3, 17),
        status=TaskStatus.TODO,
    )

    # Get tasks for the user
    tasks = await repo.get_user_tasks(user_id)

    assert len(tasks) == 2
    assert all(task.user_id == user_id for task in tasks)


@pytest.mark.asyncio
async def test_get_user_tasks_empty(db_session: AsyncSession) -> None:
    """Test getting tasks for a user with no tasks."""
    repo = TaskRepository(db_session)

    tasks = await repo.get_user_tasks("non-existent-user")

    assert tasks == []


@pytest.mark.asyncio
async def test_update_task(db_session: AsyncSession) -> None:
    """Test updating a task."""
    repo = TaskRepository(db_session)

    # Create a task
    task = await repo.create_task(
        user_id="test-user-id",
        title="Original Title",
        description="Original Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Update the task
    updated_task = await repo.update_task(
        task_id=task.id,
        title="Updated Title",
        description="Updated Description",
        due_date=date(2026, 3, 20),
        status=TaskStatus.IN_PROGRESS,
    )

    assert updated_task is not None
    assert updated_task.id == task.id
    assert updated_task.title == "Updated Title"
    assert updated_task.description == "Updated Description"
    assert updated_task.due_date == date(2026, 3, 20)
    assert updated_task.status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_update_task_partial(db_session: AsyncSession) -> None:
    """Test updating a task with partial data."""
    repo = TaskRepository(db_session)

    # Create a task
    task = await repo.create_task(
        user_id="test-user-id",
        title="Original Title",
        description="Original Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Update only the status
    updated_task = await repo.update_task(
        task_id=task.id,
        status=TaskStatus.DONE,
    )

    assert updated_task is not None
    assert updated_task.title == "Original Title"
    assert updated_task.description == "Original Description"
    assert updated_task.due_date == date(2026, 3, 15)
    assert updated_task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_update_task_not_found(db_session: AsyncSession) -> None:
    """Test updating a non-existent task."""
    repo = TaskRepository(db_session)

    updated_task = await repo.update_task(
        task_id="non-existent-id",
        title="Updated Title",
    )

    assert updated_task is None


@pytest.mark.asyncio
async def test_delete_task(db_session: AsyncSession) -> None:
    """Test deleting a task."""
    repo = TaskRepository(db_session)

    # Create a task
    task = await repo.create_task(
        user_id="test-user-id",
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Delete the task
    result = await repo.delete_task(task.id)

    assert result is True

    # Verify task is deleted
    deleted_task = await repo.get_task_by_id(task.id)
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_task_not_found(db_session: AsyncSession) -> None:
    """Test deleting a non-existent task."""
    repo = TaskRepository(db_session)

    result = await repo.delete_task("non-existent-id")

    assert result is False


@pytest.mark.asyncio
async def test_task_exists(db_session: AsyncSession) -> None:
    """Test checking if a task exists."""
    repo = TaskRepository(db_session)

    # Create a task
    task = await repo.create_task(
        user_id="test-user-id",
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Check if task exists
    exists = await repo.task_exists(task.id)

    assert exists is True


@pytest.mark.asyncio
async def test_task_exists_not_found(db_session: AsyncSession) -> None:
    """Test checking if a non-existent task exists."""
    repo = TaskRepository(db_session)

    exists = await repo.task_exists("non-existent-id")

    assert exists is False


@pytest.mark.asyncio
async def test_is_task_owner(db_session: AsyncSession) -> None:
    """Test checking if a user is the owner of a task."""
    repo = TaskRepository(db_session)

    user_id = "test-user-id"

    # Create a task
    task = await repo.create_task(
        user_id=user_id,
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Check if user is owner
    is_owner = await repo.is_task_owner(task.id, user_id)

    assert is_owner is True


@pytest.mark.asyncio
async def test_is_task_owner_false(db_session: AsyncSession) -> None:
    """Test checking if a different user is the owner of a task."""
    repo = TaskRepository(db_session)

    # Create a task
    task = await repo.create_task(
        user_id="test-user-id",
        title="Test Task",
        description="Test Description",
        due_date=date(2026, 3, 15),
        status=TaskStatus.TODO,
    )

    # Check if different user is owner
    is_owner = await repo.is_task_owner(task.id, "other-user-id")

    assert is_owner is False


@pytest.mark.asyncio
async def test_is_task_owner_not_found(db_session: AsyncSession) -> None:
    """Test checking ownership of a non-existent task."""
    repo = TaskRepository(db_session)

    is_owner = await repo.is_task_owner("non-existent-id", "test-user-id")

    assert is_owner is False