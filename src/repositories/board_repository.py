"""Board repository for data access operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.board import Board


class BoardRepository:
    """Repository for Board model data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(self, user_id: str, name: str) -> Board:
        """Create a new board.

        Args:
            user_id: ID of the user who owns the board
            name: Board name

        Returns:
            Created Board instance
        """
        board = Board(user_id=user_id, name=name)
        self.session.add(board)
        await self.session.commit()
        await self.session.refresh(board)
        return board

    async def get_by_id(self, board_id: str) -> Optional[Board]:
        """Get board by ID.

        Args:
            board_id: Board ID

        Returns:
            Board instance if found, None otherwise
        """
        result = await self.session.execute(
            select(Board).where(Board.id == board_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: str) -> list[Board]:
        """Get all boards for a specific user.

        Args:
            user_id: User ID

        Returns:
            List of Board instances
        """
        result = await self.session.execute(
            select(Board).where(Board.user_id == user_id)
        )
        return list(result.scalars().all())

    async def get_by_user_id_and_name(self, user_id: str, name: str) -> Optional[Board]:
        """Get board by user ID and name.

        Args:
            user_id: User ID
            name: Board name

        Returns:
            Board instance if found, None otherwise
        """
        result = await self.session.execute(
            select(Board).where(Board.user_id == user_id, Board.name == name)
        )
        return result.scalar_one_or_none()

    async def count_by_user_id(self, user_id: str) -> int:
        """Count boards for a specific user.

        Args:
            user_id: User ID

        Returns:
            Number of boards owned by the user
        """
        result = await self.session.execute(
            select(func.count()).select_from(Board).where(Board.user_id == user_id)
        )
        return result.scalar()

    async def delete(self, board_id: str) -> bool:
        """Delete a board by ID.

        Args:
            board_id: Board ID

        Returns:
            True if board was deleted, False if not found
        """
        board = await self.get_by_id(board_id)
        if not board:
            return False
        await self.session.delete(board)
        await self.session.commit()
        return True


__all__ = ["BoardRepository"]