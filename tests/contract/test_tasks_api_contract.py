"""Contract tests for Task API endpoints."""

import pytest
from datetime import date
from httpx import AsyncClient
from src.models.task import TaskStatus


@pytest.mark.asyncio
async def test_post_tasks_contract(client: AsyncClient, sample_user_data: dict) -> None:
    """Test POST /tasks contract."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create task
    task_data = {
        "title": "Complete project documentation",
        "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
        "due_date": "2026-03-15",
        "status": TaskStatus.TODO,
    }

    response = await client.post(
        "/api/v1/tasks",
        json=task_data,
        cookies={"session_token": token},
    )

    # Verify response status
    assert response.status_code == 201

    # Verify response structure
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "due_date" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify response values
    assert data["title"] == "Complete project documentation"
    assert data["description"] == "Write comprehensive documentation for the new feature including API reference and user guide."
    assert data["due_date"] == "2026-03-15"
    assert data["status"] == TaskStatus.TODO


@pytest.mark.asyncio
async def test_post_tasks_validation_error_contract(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test POST /tasks validation error contract."""
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

    # Verify response status
    assert response.status_code == 422

    # Verify error response structure
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert data["error"] == "validation_error"


@pytest.mark.asyncio
async def test_post_tasks_unauthorized_contract(client: AsyncClient) -> None:
    """Test POST /tasks unauthorized contract."""
    task_data = {
        "title": "Test Task",
        "description": "Test Description",
        "due_date": "2026-03-15",
        "status": TaskStatus.TODO,
    }

    response = await client.post("/api/v1/tasks", json=task_data)

    # Verify response status
    assert response.status_code == 401

    # Verify error response structure
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert data["error"] == "unauthorized"


@pytest.mark.asyncio
async def test_get_tasks_contract(client: AsyncClient, sample_user_data: dict) -> None:
    """Test GET /tasks contract."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create tasks
    await client.post(
        "/api/v1/tasks",
        json={
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token},
    )
    await client.post(
        "/api/v1/tasks",
        json={
            "title": "Fix login bug",
            "description": "Users cannot login with special characters in password",
            "due_date": "2026-03-10",
            "status": TaskStatus.IN_PROGRESS,
        },
        cookies={"session_token": token},
    )

    # Get tasks
    response = await client.get(
        "/api/v1/tasks",
        cookies={"session_token": token},
    )

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) == 2

    # Verify task structure
    task = data["tasks"][0]
    assert "id" in task
    assert "title" in task
    assert "description" in task
    assert "due_date" in task
    assert "status" in task
    assert "created_at" in task
    assert "updated_at" in task


@pytest.mark.asyncio
async def test_get_tasks_empty_contract(client: AsyncClient, sample_user_data: dict) -> None:
    """Test GET /tasks empty list contract."""
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

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "tasks" in data
    assert data["tasks"] == []


@pytest.mark.asyncio
async def test_get_task_by_id_contract(client: AsyncClient, sample_user_data: dict) -> None:
    """Test GET /tasks/{task_id} contract."""
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
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
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

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "due_date" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify response values
    assert data["id"] == task_id
    assert data["title"] == "Complete project documentation"


@pytest.mark.asyncio
async def test_get_task_by_id_not_found_contract(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test GET /tasks/{task_id} not found contract."""
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

    # Verify response status
    assert response.status_code == 404

    # Verify error response structure
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert data["error"] == "not_found"


@pytest.mark.asyncio
async def test_get_task_by_id_forbidden_contract(
    client: AsyncClient, sample_user_data: dict
) -> None:
    """Test GET /tasks/{task_id} forbidden contract."""
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

    # Verify response status
    assert response.status_code == 403

    # Verify error response structure
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert data["error"] == "forbidden"


@pytest.mark.asyncio
async def test_put_task_by_id_contract(client: AsyncClient, sample_user_data: dict) -> None:
    """Test PUT /tasks/{task_id} contract."""
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
            "title": "Complete project documentation",
            "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
            "due_date": "2026-03-15",
            "status": TaskStatus.TODO,
        },
        cookies={"session_token": token},
    )
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {
        "title": "Complete project documentation (updated)",
        "description": "Write comprehensive documentation for the new feature including API reference and user guide. Add examples.",
        "due_date": "2026-03-20",
        "status": TaskStatus.IN_PROGRESS,
    }
    response = await client.put(
        f"/api/v1/tasks/{task_id}",
        json=update_data,
        cookies={"session_token": token},
    )

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "id" in data
    assert "title" in data
    assert "description" in data
    assert "due_date" in data
    assert "status" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify response values
    assert data["id"] == task_id
    assert data["title"] == "Complete project documentation (updated)"
    assert data["status"] == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_delete_task_by_id_contract(client: AsyncClient, sample_user_data: dict) -> None:
    """Test DELETE /tasks/{task_id} contract."""
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

    # Verify response status
    assert response.status_code == 200

    # Verify response structure
    data = response.json()
    assert "message" in data
    assert data["message"] == "Task deleted successfully"