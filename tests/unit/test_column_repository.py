"""Unit tests for ColumnRepository."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.column_repository import ColumnRepository
from src.repositories.board_repository import BoardRepository


@pytest.mark.asyncio
async def test_create_column(db_session: AsyncSession) -> None:
    """Test creating a new column."""
    column_repo = ColumnRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create a board first
    board = await board_repo.create("test-user-id", "Мой проект")

    # Create column
    column = await column_repo.create(board.id, "К выполнению", 1)

    assert column.id is not None
    assert column.name == "К выполнению"
    assert column.order == 1
    assert column.board_id == board.id


@pytest.mark.asyncio
async def test_create_columns(db_session: AsyncSession) -> None:
    """Test creating multiple columns for a board."""
    column_repo = ColumnRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create a board first
    board = await board_repo.create("test-user-id", "Мой проект")

    # Create multiple columns
    columns_data = [
        {"name": "К выполнению", "order": 1},
        {"name": "В работу", "order": 2},
        {"name": "Сделано", "order": 3},
    ]

    columns = await column_repo.create_columns(board.id, columns_data)

    assert len(columns) == 3
    assert columns[0].name == "К выполнению"
    assert columns[1].name == "В работу"
    assert columns[2].name == "Сделано"


@pytest.mark.asyncio
async def test_get_column_by_id(db_session: AsyncSession) -> None:
    """Test getting a column by ID."""
    column_repo = ColumnRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create a board and column
    board = await board_repo.create("test-user-id", "Мой проект")
    created_column = await column_repo.create(board.id, "К выполнению", 1)

    # Get column by ID
    column = await column_repo.get_by_id(created_column.id)

    assert column is not None
    assert column.id == created_column.id
    assert column.name == "К выполнению"


@pytest.mark.asyncio
async def test_get_column_by_id_not_found(db_session: AsyncSession) -> None:
    """Test getting a non-existent column by ID."""
    column_repo = ColumnRepository(db_session)

    column = await column_repo.get_by_id("non-existent-id")

    assert column is None


@pytest.mark.asyncio
async def test_get_columns_by_board_id(db_session: AsyncSession) -> None:
    """Test getting all columns for a board."""
    column_repo = ColumnRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create a board
    board = await board_repo.create("test-user-id", "Мой проект")

    # Create multiple columns
    await column_repo.create(board.id, "К выполнению", 1)
    await column_repo.create(board.id, "В работу", 2)
    await column_repo.create(board.id, "Сделано", 3)

    # Get columns
    columns = await column_repo.get_by_board_id(board.id)

    assert len(columns) == 3
    assert columns[0].order == 1
    assert columns[1].order == 2
    assert columns[2].order == 3


@pytest.mark.asyncio
async def test_get_columns_by_board_id_empty(db_session: AsyncSession) -> None:
    """Test getting columns for a board with no columns."""
    column_repo = ColumnRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create a board
    board = await board_repo.create("test-user-id", "Мой проект")

    # Get columns (should be empty)
    columns = await column_repo.get_by_board_id(board.id)

    assert len(columns) == 0


@pytest.mark.asyncio
async def test_count_tasks_by_column(db_session: AsyncSession) -> None:
    """Test counting tasks in a column."""
    column_repo = ColumnRepository(db_session)
    board_repo = BoardRepository(db_session)

    # Create a board and column
    board = await board_repo.create("test-user-id", "Мой проект")
    column = await column_repo.create(board.id, "К выполнению", 1)

    # Count tasks (should be 0 initially)
    count = await column_repo.count_tasks_by_column(column.id)

    assert count == 0


@pytest.mark.asyncio
async def test_count_tasks_by_column_not_found(db_session: AsyncSession) -> None:
    """Test counting tasks for a non-existent column."""
    column_repo = ColumnRepository(db_session)

    count = await column_repo.count_tasks_by_column("non-existent-id")

    assert count == 0