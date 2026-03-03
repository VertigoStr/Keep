"""Contract tests for board management API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.contract
class TestBoardAPIContract:
    """Contract tests for board management API."""

    @pytest.mark.asyncio
    async def test_create_board_contract_success(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test successful board creation contract."""
        board_data = {"name": "Мой проект"}
        response = await client.post("/api/v1/boards", json=board_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == board_data["name"]
        assert "user_id" in data
        assert "created_at" in data
        assert "columns" in data
        assert len(data["columns"]) == 5

        # Verify predefined columns
        column_names = [col["name"] for col in data["columns"]]
        expected_columns = ["К выполнению", "В работу", "Возникла проблема", "Сделано", "Отмена"]
        assert column_names == expected_columns

        # Verify column order
        column_orders = [col["order"] for col in data["columns"]]
        assert column_orders == [1, 2, 3, 4, 5]

    @pytest.mark.asyncio
    async def test_create_board_contract_invalid_name(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board creation with invalid name characters."""
        board_data = {"name": "Invalid@Name#"}
        response = await client.post("/api/v1/boards", json=board_data, headers=auth_headers)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_create_board_contract_empty_name(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board creation with empty name."""
        board_data = {"name": ""}
        response = await client.post("/api/v1/boards", json=board_data, headers=auth_headers)

        assert response.status_code == 422
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_create_board_contract_duplicate_name(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board creation with duplicate name."""
        board_data = {"name": "Дубликат"}
        # First creation
        await client.post("/api/v1/boards", json=board_data, headers=auth_headers)
        # Second creation with same name
        response = await client.post("/api/v1/boards", json=board_data, headers=auth_headers)

        assert response.status_code == 409
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_create_board_contract_limit_exceeded(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board creation when limit exceeded (1 board per user)."""
        # Create first board
        await client.post("/api/v1/boards", json={"name": "Первая доска"}, headers=auth_headers)
        # Try to create second board
        response = await client.post("/api/v1/boards", json={"name": "Вторая доска"}, headers=auth_headers)

        assert response.status_code == 409
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_create_board_contract_unauthorized(
        self, client: AsyncClient
    ) -> None:
        """Test board creation without authentication."""
        board_data = {"name": "Мой проект"}
        response = await client.post("/api/v1/boards", json=board_data)

        assert response.status_code == 401
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_list_boards_contract_success(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test successful board listing contract."""
        # Create a board first
        await client.post("/api/v1/boards", json={"name": "Мой проект"}, headers=auth_headers)

        # List boards
        response = await client.get("/api/v1/boards", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "boards" in data
        assert "total" in data
        assert data["total"] == 1
        assert len(data["boards"]) == 1
        assert data["boards"][0]["name"] == "Мой проект"

    @pytest.mark.asyncio
    async def test_list_boards_contract_empty(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board listing when user has no boards."""
        response = await client.get("/api/v1/boards", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "boards" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["boards"]) == 0
        assert "message" in data

    @pytest.mark.asyncio
    async def test_get_board_contract_success(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test successful board retrieval contract."""
        # Create a board first
        create_response = await client.post(
            "/api/v1/boards", json={"name": "Мой проект"}, headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Get board
        response = await client.get(f"/api/v1/boards/{board_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == board_id
        assert data["name"] == "Мой проект"
        assert "columns" in data

    @pytest.mark.asyncio
    async def test_get_board_contract_not_found(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board retrieval with non-existent ID."""
        response = await client.get("/api/v1/boards/nonexistent-id", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_delete_board_contract_success(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test successful board deletion contract."""
        # Create a board first
        create_response = await client.post(
            "/api/v1/boards", json={"name": "Мой проект"}, headers=auth_headers
        )
        board_id = create_response.json()["id"]

        # Delete board
        response = await client.delete(f"/api/v1/boards/{board_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify board is deleted
        get_response = await client.get(f"/api/v1/boards/{board_id}", headers=auth_headers)
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_board_contract_not_found(
        self, client: AsyncClient, auth_headers: dict
    ) -> None:
        """Test board deletion with non-existent ID."""
        response = await client.delete("/api/v1/boards/nonexistent-id", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()
        assert "error" in data

    @pytest.mark.asyncio
    async def test_delete_board_contract_unauthorized(
        self, client: AsyncClient
    ) -> None:
        """Test board deletion without authentication."""
        response = await client.delete("/api/v1/boards/some-id")

        assert response.status_code == 401
        data = response.json()
        assert "error" in data