"""Integration tests for Task API endpoints."""

import pytest
from datetime import date
from httpx import AsyncClient
from src.models.task import TaskStatus


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient, sample_user_data: dict) -> None:
    """Test creating a new task via API."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create task
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2026-03-15",
        "status": TaskStatus.TODO,
    }

    response = await client.post(
        "/api/v1/tasks",
        json=task_data,
        cookies={"session_token": token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["due_date"] == "2026-03-15"
    assert data["status"] == TaskStatus.TODO
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_task_unauthenticated(client: AsyncClient) -> None:
    """Test creating a task without authentication."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2026-03-15",
        "status": TaskStatus.TODO,
    }

    response = await client.post("/api/v1/tasks", json=task_data)

    assert response.status_code == 401
    assert response.json()["error"] == "unauthorized"


@pytest.mark.asyncio
async def test_create_task_validation_error_empty_title(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test creating a task with empty title."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create task with empty title
    task_data = {
        "title": "",
        "description": "Test Description",
        "due_date": "2026-03-15",
        "status": TaskStatus.TODO,
    }

    response = await client.post(
        "/api/v1/tasks",
        json=task_data,
        cookies={"session_token": token},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_validation_error_invalid_status(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test creating a task with invalid status."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create task with invalid status
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2026-03-15",
        "status": "invalid_status",
    }

    response = await client.post(
        "/api/v1/tasks",
        json=task_data,
        cookies={"session_token": token},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


@pytest.mark.asyncio
async def test_get_tasks(client: AsyncClient, sample_user_data: dict) -> None:
    """Test getting all tasks for a user."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create multiple tasks
    await client.post(
        "/api/v1/tasks",
        json={
            "title": "Task 1",
            "description": "Description 1",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token},
    )
    await client.post(
        "/api/v1/tasks",
        json={
            "title": "Task 2",
            "description": "Description 2",
            "due_date": "2026-03-16",
            "status": TaskStatus.IN_PROGRESS,
        },
        cookies={"session_token": token},
    )

    # Get tasks
    response = await client.get(
        "/api/v1/tasks",
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert len(data["tasks"]) == 2


@pytest.mark.asyncio
async def test_get_tasks_empty(client: AsyncClient, sample_user_data: dict) -> None:
    """Test getting tasks when user has no tasks."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Get tasks
    response = await client.get(
        "/api/v1/tasks",
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []


@pytest.mark.asyncio
async def test_get_task_by_id(client: AsyncClient, sample_user_data: dict) -> None:
    """Test getting a specific task by ID."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token},
    )
    task_id = create_response.json()["id"]

    # Get the task
    response = await client.get(
        f"/api/v1/tasks/{task_id}",
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"


@pytest.mark.asyncio
async def test_get_task_by_id_not_found(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test getting a non-existent task."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Get non-existent task
    response = await client.get(
        "/api/v1/tasks/non-existent-id",
        cookies={"session_token": token},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "not_found"


@pytest.mark.asyncio
async def test_get_task_by_id_not_owner(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test getting a task owned by another user."""
    # Register and login user1
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response1 = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token1 = login_response1.json()["token"]

    # Create a task for user1
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token1},
    )
    task_id = create_response.json()["id"]

    # Register and login user2
    user2_data = {
        "email": "user2@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
    }
    await client.post("/api/v1/auth/register", json=user2_data)
    login_response2 = await client.post(
        "/api/v1/auth/login",
        json={"email": user2_data["email"], "password": user2_data["password"]},
    )
    token2 = login_response2.json()["token"]

    # Try to get user1's task as user2
    response = await client.get(
        f"/api/v1/tasks/{task_id}",
        cookies={"session_token": token2},
    )

    assert response.status_code == 403
    assert response.json()["error"] == "forbidden"


@pytest.mark.asyncio
async def test_update_task(client: AsyncClient, sample_user_data: dict) -> None:
    """Test updating a task."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Original Title",
            "description": "Original Description",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token},
    )
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {
        "title": "Updated Title",
        "status": TaskStatus.IN_PROGRESS,
    }
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json=update_data,
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original Description"
    assert data["status"] == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient, sample_user_data: dict) -> None:
    """Test deleting a task."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create a task
    create_response = await client.post(
        "/api/v1/tasks",
        json={
            "title": "Test Task",
            "description": "Test Description",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token},
    )
    task_id = create_response.json()["id"]

    # Delete the task
    response = await client.delete(
        f"/api/v1/tasks/{task_id}",
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Task deleted successfully"

    # Verify task is deleted
    get_response = await client.get(
        f"/api/v1/tasks/{task_id}",
        cookies={"session_token": token},
    )
    assert get_response.status_code == 404