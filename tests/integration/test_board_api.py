"""Integration tests for Board API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_board_integration(client: AsyncClient, sample_user_data: dict) -> None:
    """Test creating a board via API with full integration."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create board
    board_data = {"name": "Мой проект"}
    response = await client.post(
        "/api/v1/boards",
        json=board_data,
        cookies={"session_token": token},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Мой проект"
    assert "id" in data
    assert "created_at" in data
    assert "columns" in data
    assert len(data["columns"]) == 5

    # Verify predefined columns
    column_names = [col["name"] for col in data["columns"]]
    expected_columns = ["К выполнению", "В работу", "Возникла проблема", "Сделано", "Отмена"]
    assert column_names == expected_columns


@pytest.mark.asyncio
async def test_create_board_unauthenticated(client: AsyncClient) -> None:
    """Test creating a board without authentication."""
    board_data = {"name": "Мой проект"}
    response = await client.post("/api/v1/boards", json=board_data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_board_limit_exceeded(client: AsyncClient, sample_user_data: dict) -> None:
    """Test creating a board when limit exceeded."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create first board
    await client.post(
        "/api/v1/boards",
        json={"name": "Первая доска"},
        cookies={"session_token": token},
    )

    # Try to create second board
    response = await client.post(
        "/api/v1/boards",
        json={"name": "Вторая доска"},
        cookies={"session_token": token},
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_boards_integration(client: AsyncClient, sample_user_data: dict) -> None:
    """Test listing boards via API with full integration."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create a board
    await client.post(
        "/api/v1/boards",
        json={"name": "Мой проект"},
        cookies={"session_token": token},
    )

    # List boards
    response = await client.get(
        "/api/v1/boards",
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["boards"]) == 1
    assert data["boards"][0]["name"] == "Мой проект"


@pytest.mark.asyncio
async def test_get_board_integration(client: AsyncClient, sample_user_data: dict) -> None:
    """Test getting a board via API with full integration."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create a board
    create_response = await client.post(
        "/api/v1/boards",
        json={"name": "Мой проект"},
        cookies={"session_token": token},
    )
    board_id = create_response.json()["id"]

    # Get board
    response = await client.get(
        f"/api/v1/boards/{board_id}",
        cookies={"session_token": token},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == board_id
    assert data["name"] == "Мой проект"


@pytest.mark.asyncio
async def test_delete_board_integration(client: AsyncClient, sample_user_data: dict) -> None:
    """Test deleting a board via API with full integration."""
    # Register and login user
    await client.post("/api/v1/auth/register", json=sample_user_data)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": sample_user_data["email"], "password": sample_user_data["password"]},
    )
    token = login_response.json()["token"]

    # Create a board
    create_response = await client.post(
        "/api/v1/boards",
        json={"name": "Мой проект"},
        cookies={"session_token": token},
    )
    board_id = create_response.json()["id"]

    # Delete board
    response = await client.delete(
        f"/api/v1/boards/{board_id}",
        cookies={"session_token": token},
    )

    assert response.status_code == 204

    # Verify board is deleted
    get_response = await client.get(
        f"/api/v1/boards/{board_id}",
        cookies={"session_token": token},
    )
    assert get_response.status_code == 404