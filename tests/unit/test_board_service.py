"""Unit tests for BoardService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.board_service import BoardService
from src.schemas.board import BoardCreate
from src.middleware.error_handler import ConflictError, NotFoundError, ForbiddenError


@pytest.mark.asyncio
async def test_create_board_success(db_session: AsyncSession) -> None:
    """Test creating a new board with predefined columns."""
    service = BoardService(db_session)

    user_id = "test-user-id"
    board_data = BoardCreate(name="Мой проект")

    board_response = await service.create_board(user_id, board_data)

    assert board_response.id is not None
    assert board_response.name == "Мой проект"
    assert board_response.user_id == user_id
    assert len(board_response.columns) == 5

    # Verify predefined columns
    column_names = [col.name for col in board_response.columns]
    expected_columns = ["К выполнению", "В работу", "Возникла проблема", "Сделано", "Отмена"]
    assert column_names == expected_columns


@pytest.mark.asyncio
async def test_create_board_limit_exceeded(db_session: AsyncSession) -> None:
    """Test creating a board when limit exceeded (1 board per user)."""
    service = BoardService(db_session)

    user_id = "test-user-id"

    # Create first board
    await service.create_board(user_id, BoardCreate(name="Первая доска"))

    # Try to create second board
    with pytest.raises(ConflictError) as exc_info:
        await service.create_board(user_id, BoardCreate(name="Вторая доска"))

    assert "лимит" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_create_board_duplicate_name(db_session: AsyncSession) -> None:
    """Test creating a board with duplicate name."""
    service = BoardService(db_session)

    user_id = "test-user-id"
    board_name = "Дубликат"

    # Create first board
    await service.create_board(user_id, BoardCreate(name=board_name))

    # Try to create second board with same name
    with pytest.raises(ConflictError) as exc_info:
        await service.create_board(user_id, BoardCreate(name=board_name))

    assert "уже существует" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_list_boards_success(db_session: AsyncSession) -> None:
    """Test listing boards for a user."""
    service = BoardService(db_session)

    user_id = "test-user-id"

    # Create a board
    await service.create_board(user_id, BoardCreate(name="Мой проект"))

    # List boards
    boards_response = await service.list_boards(user_id)

    assert boards_response.total == 1
    assert len(boards_response.boards) == 1
    assert boards_response.boards[0].name == "Мой проект"


@pytest.mark.asyncio
async def test_list_boards_empty(db_session: AsyncSession) -> None:
    """Test listing boards when user has no boards."""
    service = BoardService(db_session)

    boards_response = await service.list_boards("non-existent-user")

    assert boards_response.total == 0
    assert len(boards_response.boards) == 0
    assert boards_response.message == "У вас пока нет досок"


@pytest.mark.asyncio
async def test_get_board_success(db_session: AsyncSession) -> None:
    """Test getting a specific board by ID."""
    service = BoardService(db_session)

    user_id = "test-user-id"

    # Create a board
    board_response = await service.create_board(user_id, BoardCreate(name="Мой проект"))
    board_id = board_response.id

    # Get board
    board = await service.get_board(board_id, user_id)

    assert board.id == board_id
    assert board.name == "Мой проект"
    assert len(board.columns) == 5


@pytest.mark.asyncio
async def test_get_board_not_found(db_session: AsyncSession) -> None:
    """Test getting a non-existent board."""
    service = BoardService(db_session)

    with pytest.raises(NotFoundError) as exc_info:
        await service.get_board("non-existent-id", "test-user-id")

    assert "не найдена" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_get_board_forbidden(db_session: AsyncSession) -> None:
    """Test getting a board owned by another user."""
    service = BoardService(db_session)

    user_id_1 = "user-1"
    user_id_2 = "user-2"

    # Create board for user 1
    board_response = await service.create_board(user_id_1, BoardCreate(name="Доска пользователя 1"))
    board_id = board_response.id

    # Try to get board as user 2
    with pytest.raises(ForbiddenError) as exc_info:
        await service.get_board(board_id, user_id_2)

    assert "нет прав" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_delete_board_success(db_session: AsyncSession) -> None:
    """Test deleting a board."""
    service = BoardService(db_session)

    user_id = "test-user-id"

    # Create a board
    board_response = await service.create_board(user_id, BoardCreate(name="Мой проект"))
    board_id = board_response.id

    # Delete board
    await service.delete_board(board_id, user_id)

    # Verify board is deleted
    with pytest.raises(NotFoundError):
        await service.get_board(board_id, user_id)


@pytest.mark.asyncio
async def test_delete_board_not_found(db_session: AsyncSession) -> None:
    """Test deleting a non-existent board."""
    service = BoardService(db_session)

    with pytest.raises(NotFoundError) as exc_info:
        await service.delete_board("non-existent-id", "test-user-id")

    assert "не найдена" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_delete_board_forbidden(db_session: AsyncSession) -> None:
    """Test deleting a board owned by another user."""
    service = BoardService(db_session)

    user_id_1 = "user-1"
    user_id_2 = "user-2"

    # Create board for user 1
    board_response = await service.create_board(user_id_1, BoardCreate(name="Доска пользователя 1"))
    board_id = board_response.id

    # Try to delete board as user 2
    with pytest.raises(ForbiddenError) as exc_info:
        await service.delete_board(board_id, user_id_2)

    assert "нет прав" in str(exc_info.value).lower()