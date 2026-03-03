"""Column repository for data access operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models.column import Column


class ColumnRepository:
    """Repository for Column model data access."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session."""
        self.session = session

    async def create(self, board_id: str, name: str, order: int) -> Column:
        """Create a new column.

        Args:
            board_id: ID of the board the column belongs to
            name: Column name
            order: Column order (1-5)

        Returns:
            Created Column instance
        """
        column = Column(board_id=board_id, name=name, order=order)
        self.session.add(column)
        await self.session.commit()
        await self.session.refresh(column)
        return column

    async def create_columns(self, board_id: str, columns_data: list[dict]) -> list[Column]:
        """Create multiple columns for a board.

        Args:
            board_id: ID of the board
            columns_data: List of dicts with 'name' and 'order' keys

        Returns:
            List of created Column instances
        """
        columns = [
            Column(board_id=board_id, name=data['name'], order=data['order'])
            for data in columns_data
        ]
        self.session.add_all(columns)
        await self.session.commit()
        for column in columns:
            await self.session.refresh(column)
        return columns

    async def get_by_id(self, column_id: str) -> Optional[Column]:
        """Get column by ID.

        Args:
            column_id: Column ID

        Returns:
            Column instance if found, None otherwise
        """
        result = await self.session.execute(
            select(Column).where(Column.id == column_id)
        )
        return result.scalar_one_or_none()

    async def get_by_board_id(self, board_id: str) -> list[Column]:
        """Get all columns for a specific board.

        Args:
            board_id: Board ID

        Returns:
            List of Column instances ordered by order field
        """
        result = await self.session.execute(
            select(Column).where(Column.board_id == board_id).order_by(Column.order)
        )
        return list(result.scalars().all())

    async def count_tasks_by_column(self, column_id: str) -> int:
        """Count tasks in a specific column.

        Args:
            column_id: Column ID

        Returns:
            Number of tasks in the column
        """
        from src.models.task import Task
        result = await self.session.execute(
            select(func.count()).select_from(Task).where(Task.column_id == column_id)
        )
        return result.scalar()


__all__ = ["ColumnRepository"]