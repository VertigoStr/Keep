"""Board management API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.services.board_service import BoardService
from src.utils.security import get_current_user
from src.schemas.board import (
    BoardCreate,
    BoardResponse,
    BoardListResponse,
    ErrorResponse,
)

router = APIRouter()


@router.post(
    "/boards",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid board name"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        409: {"model": ErrorResponse, "description": "Board already exists or limit exceeded"},
    },
)
async def create_board(
    board_data: BoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
) -> BoardResponse:
    """Create a new board with predefined columns.

    Creates a new board for the authenticated user with five predefined columns:
    "К выполнению", "В работу", "Возникла проблема", "Сделано", "Отмена".

    Args:
        board_data: Board creation data with name
        db: Database session
        current_user_id: ID of the authenticated user

    Returns:
        Created board with all columns

    Raises:
        ConflictError: If board name already exists or limit exceeded
    """
    board_service = BoardService(db)
    return await board_service.create_board(current_user_id, board_data)


@router.get(
    "/boards",
    response_model=BoardListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
)
async def list_boards(
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
) -> BoardListResponse:
    """Get all boards for the authenticated user.

    Returns a list of all boards owned by the user with their columns
    and task counts for each column.

    Args:
        db: Database session
        current_user_id: ID of the authenticated user

    Returns:
        List of boards with columns and task counts
    """
    board_service = BoardService(db)
    return await board_service.list_boards(current_user_id)


@router.get(
    "/boards/{board_id}",
    response_model=BoardResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Board not found"},
    },
)
async def get_board(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
) -> BoardResponse:
    """Get a specific board by ID.

    Returns detailed information about a board including all columns
    and task counts for each column.

    Args:
        board_id: ID of the board to retrieve
        db: Database session
        current_user_id: ID of the authenticated user

    Returns:
        Board with columns and task counts

    Raises:
        NotFoundError: If board not found
        ForbiddenError: If user is not the board owner
    """
    board_service = BoardService(db)
    return await board_service.get_board(board_id, current_user_id)


@router.delete(
    "/boards/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Board not found"},
    },
)
async def delete_board(
    board_id: str,
    db: AsyncSession = Depends(get_db),
    current_user_id: str = Depends(get_current_user),
) -> None:
    """Delete a board and all its columns and tasks.

    Permanently deletes a board and all associated data including
    columns and tasks. This action cannot be undone.

    Args:
        board_id: ID of the board to delete
        db: Database session
        current_user_id: ID of the authenticated user

    Raises:
        NotFoundError: If board not found
        ForbiddenError: If user is not the board owner
    """
    board_service = BoardService(db)
    await board_service.delete_board(board_id, current_user_id)


__all__ = ["router"]