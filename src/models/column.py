"""Column SQLAlchemy model."""

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.models import BaseModel


class Column(BaseModel):
    """Column model representing a status column in a board."""

    __tablename__ = "columns"

    name = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    board_id = Column(String, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    tasks = relationship("Task", backref="column", cascade="all, delete-orphan")

    # Unique constraint for board_id and order
    __table_args__ = (
        UniqueConstraint('board_id', 'order', name='uq_board_column_order'),
    )

    def __repr__(self) -> str:
        """String representation of Column."""
        return f"<Column(id={self.id}, name={self.name}, order={self.order}, board_id={self.board_id})>"


__all__ = ["Column"]