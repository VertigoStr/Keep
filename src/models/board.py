"""Board SQLAlchemy model."""

from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from src.models import BaseModel


class Board(BaseModel):
    """Board model representing a user's task board."""

    __tablename__ = "boards"

    name = Column(String(255), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relationships
    user = relationship("User", backref="boards")
    columns = relationship("Column", backref="board", cascade="all, delete-orphan")

    # Unique constraint for user_id and name
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_board_name'),
    )

    def __repr__(self) -> str:
        """String representation of Board."""
        return f"<Board(id={self.id}, name={self.name}, user_id={self.user_id})>"


__all__ = ["Board"]