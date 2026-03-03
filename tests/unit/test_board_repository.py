"""Unit tests for BoardRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.board_repository import BoardRepository


@pytest.mark.asyncio
async def test_create_board(db_session: AsyncSession) -> None:
    """Test creating a new board."""
    repo = BoardRepository(db_session)

    user_id = "test-user-id"
    name = "Мой проект"

    board = await repo.create(user_id, name)

    assert board.id is not None
    assert board.name == name
    assert board.user_id == user_id


@pytest.mark.asyncio
async def test_get_board_by_id(db_session: AsyncSession) -> None:
    """Test getting a board by ID."""
    repo = BoardRepository(db_session)

    user_id = "test-user-id"
    name = "Мой проект"

    # Create board
    created_board = await repo.create(user_id, name)

    # Get board by ID
    board = await repo.get_by_id(created_board.id)

    assert board is not None
    assert board.id == created_board.id
    assert board.name == name


@pytest.mark.asyncio
async def test_get_board_by_id_not_found(db_session: AsyncSession) -> None:
    """Test getting a non-existent board by ID."""
    repo = BoardRepository(db_session)

    board = await repo.get_by_id("non-existent-id")

    assert board is None


@pytest.mark.asyncio
async def test_get_boards_by_user_id(db_session: AsyncSession) -> None:
    """Test getting all boards for a user."""
    repo = BoardRepository(db_session)

    user_id = "test-user-id"

    # Create multiple boards
    await repo.create(user_id, "Доска 1")
    await repo.create(user_id, "Доска 2")

    # Get boards
    boards = await repo.get_by_user_id(user_id)

    assert len(boards) == 2
    assert all(board.user_id == user_id for board in boards)


@pytest.mark.asyncio
async def test_get_boards_by_user_id_empty(db_session: AsyncSession) -> None:
    """Test getting boards for a user with no boards."""
    repo = BoardRepository(db_session)

    boards = await repo.get_by_user_id("non-existent-user")

    assert len(boards) == 0


@pytest.mark.asyncio
async def test_get_board_by_user_id_and_name(db_session: AsyncSession) -> None:
    """Test getting a board by user ID and name."""
    repo = BoardRepository(db_session)

    user_id = "test-user-id"
    name = "Мой проект"

    # Create board
    await repo.create(user_id, name)

    # Get board by user_id and name
    board = await repo.get_by_user_id_and_name(user_id, name)

    assert board is not None
    assert board.name == name
    assert board.user_id == user_id


@pytest.mark.asyncio
async def test_get_board_by_user_id_and_name_not_found(db_session: AsyncSession) -> None:
    """Test getting a non-existent board by user ID and name."""
    repo = BoardRepository(db_session)

    board = await repo.get_by_user_id_and_name("user-123", "Non-existent")

    assert board is None


@pytest.mark.asyncio
async def test_count_boards_by_user_id(db_session: AsyncSession) -> None:
    """Test counting boards for a user."""
    repo = BoardRepository(db_session)

    user_id = "test-user-id"

    # Create multiple boards
    await repo.create(user_id, "Доска 1")
    await repo.create(user_id, "Доска 2")
    await repo.create(user_id, "Доска 3")

    # Count boards
    count = await repo.count_by_user_id(user_id)

    assert count == 3


@pytest.mark.asyncio
async def test_count_boards_by_user_id_empty(db_session: AsyncSession) -> None:
    """Test counting boards for a user with no boards."""
    repo = BoardRepository(db_session)

    count = await repo.count_by_user_id("non-existent-user")

    assert count == 0


@pytest.mark.asyncio
async def test_delete_board(db_session: AsyncSession) -> None:
    """Test deleting a board."""
    repo = BoardRepository(db_session)

    user_id = "test-user-id"

    # Create board
    board = await repo.create(user_id, "Мой проект")
    board_id = board.id

    # Delete board
    result = await repo.delete(board_id)

    assert result is True

    # Verify board is deleted
    deleted_board = await repo.get_by_id(board_id)
    assert deleted_board is None


@pytest.mark.asyncio
async def test_delete_board_not_found(db_session: AsyncSession) -> None:
    """Test deleting a non-existent board."""
    repo = BoardRepository(db_session)

    result = await repo.delete("non-existent-id")

    assert result is False