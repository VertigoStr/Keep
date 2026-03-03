"""Board service for board business logic."""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.board_repository import BoardRepository
from src.repositories.column_repository import ColumnRepository
from src.schemas.board import (
    BoardCreate,
    BoardResponse,
    BoardListResponse,
    ColumnResponse,
)
from src.utils.board_validators import (
    validate_board_limit,
    validate_board_ownership,
)
from src.middleware.error_handler import NotFoundError, ForbiddenError, ConflictError

logger = logging.getLogger(__name__)

# Predefined columns for new boards
PREDEFINED_COLUMNS = [
    {"name": "К выполнению", "order": 1},
    {"name": "В работу", "order": 2},
    {"name": "Возникла проблема", "order": 3},
    {"name": "Сделано", "order": 4},
    {"name": "Отмена", "order": 5},
]


class BoardService:
    """Service for board business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize board service with database session."""
        self.session = session
        self.board_repository = BoardRepository(session)
        self.column_repository = ColumnRepository(session)

    async def create_board(
        self,
        user_id: str,
        board_data: BoardCreate,
    ) -> BoardResponse:
        """Create a new board with predefined columns.

        Args:
            user_id: ID of the user creating the board
            board_data: Board creation data

        Returns:
            Created board response with columns

        Raises:
            ConflictError: If board name already exists or limit exceeded
        """
        logger.info(f"Creating board for user {user_id}: {board_data.name}")

        # Check for duplicate board name
        existing_board = await self.board_repository.get_by_user_id_and_name(
            user_id, board_data.name
        )
        if existing_board:
            logger.warning(f"Board name '{board_data.name}' already exists for user {user_id}")
            raise ConflictError("Доска с таким названием уже существует")

        # Check board limit (1 board per user)
        current_count = await self.board_repository.count_by_user_id(user_id)
        if not validate_board_limit(current_count):
            logger.warning(f"User {user_id} exceeded board limit")
            raise ConflictError("Достигнут лимит досок (максимум 1)")

        # Create board
        board = await self.board_repository.create(user_id, board_data.name)

        # Create predefined columns
        columns = await self.column_repository.create_columns(
            board.id, PREDEFINED_COLUMNS
        )

        logger.info(f"Board created successfully: {board.id} with {len(columns)} columns")

        # Build response with columns
        column_responses = [
            ColumnResponse.model_validate(column) for column in columns
        ]
        return BoardResponse(
            id=board.id,
            name=board.name,
            user_id=board.user_id,
            created_at=board.created_at,
            columns=column_responses
        )

    async def list_boards(self, user_id: str) -> BoardListResponse:
        """Get all boards for the authenticated user.

        Args:
            user_id: ID of the user

        Returns:
            List of boards with columns and task counts
        """
        logger.info(f"Retrieving boards for user {user_id}")

        boards = await self.board_repository.get_by_user_id(user_id)

        board_responses = []
        for board in boards:
            # Get columns for this board
            columns = await self.column_repository.get_by_board_id(board.id)

            # Add task count to each column
            column_responses = []
            for column in columns:
                task_count = await self.column_repository.count_tasks_by_column(column.id)
                column_responses.append(
                    ColumnResponse.model_validate(column).model_copy(
                        update={"task_count": task_count}
                    )
                )

            board_responses.append(
                BoardResponse(
                    id=board.id,
                    name=board.name,
                    user_id=board.user_id,
                    created_at=board.created_at,
                    columns=column_responses
                )
            )

        logger.info(f"Found {len(boards)} boards for user {user_id}")

        if not boards:
            return BoardListResponse(
                boards=[],
                total=0,
                message="У вас пока нет досок"
            )

        return BoardListResponse(boards=board_responses, total=len(boards))

    async def get_board(self, board_id: str, user_id: str) -> BoardResponse:
        """Get a specific board by ID.

        Args:
            board_id: Board ID
            user_id: ID of the user requesting the board

        Returns:
            Board response with columns and task counts

        Raises:
            NotFoundError: If board not found
            ForbiddenError: If user is not the board owner
        """
        logger.info(f"Retrieving board {board_id} for user {user_id}")

        board = await self.board_repository.get_by_id(board_id)
        if not board:
            logger.warning(f"Board {board_id} not found")
            raise NotFoundError("Доска не найдена")

        # Check ownership
        if not validate_board_ownership(board.user_id, user_id):
            logger.warning(f"User {user_id} does not own board {board_id}")
            raise ForbiddenError("У вас нет прав на просмотр этой доски")

        # Get columns with task counts
        columns = await self.column_repository.get_by_board_id(board_id)
        column_responses = []
        for column in columns:
            task_count = await self.column_repository.count_tasks_by_column(column.id)
            column_responses.append(
                ColumnResponse.model_validate(column).model_copy(
                    update={"task_count": task_count}
                )
            )

        logger.info(f"Board {board_id} retrieved successfully")
        return BoardResponse(
            id=board.id,
            name=board.name,
            user_id=board.user_id,
            created_at=board.created_at,
            columns=column_responses
        )

    async def delete_board(self, board_id: str, user_id: str) -> None:
        """Delete a board and all its columns and tasks.

        Args:
            board_id: Board ID
            user_id: ID of the user requesting deletion

        Raises:
            NotFoundError: If board not found
            ForbiddenError: If user is not the board owner
        """
        logger.info(f"Deleting board {board_id} for user {user_id}")

        board = await self.board_repository.get_by_id(board_id)
        if not board:
            logger.warning(f"Board {board_id} not found")
            raise NotFoundError("Доска не найдена")

        # Check ownership
        if not validate_board_ownership(board.user_id, user_id):
            logger.warning(f"User {user_id} does not own board {board_id}")
            raise ForbiddenError("У вас нет прав на удаление этой доски")

        # Delete board (cascade will delete columns and tasks)
        await self.board_repository.delete(board_id)

        logger.info(f"Board {board_id} deleted successfully")


__all__ = ["BoardService"]