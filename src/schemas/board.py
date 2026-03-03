"""Board Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class ColumnResponse(BaseModel):
    """Schema for column response."""

    id: str
    name: str
    order: int
    board_id: str
    task_count: Optional[int] = Field(default=0, description="Number of tasks in column")

    class Config:
        """Pydantic config."""

        from_attributes = True


class ColumnCreate(BaseModel):
    """Schema for creating a column."""

    name: str = Field(..., min_length=1, max_length=100, description="Column name")
    order: int = Field(..., ge=1, le=5, description="Column order (1-5)")


class BoardBase(BaseModel):
    """Base board schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Board name")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate board name characters.

        Args:
            v: Board name to validate

        Returns:
            Validated board name

        Raises:
            ValueError: If name contains invalid characters
        """
        # Allow letters, numbers, spaces and basic punctuation: .,!?-:;
        pattern = r"^[\p{L}\p{N}\s.,!?\-:;]+$"
        if not re.match(pattern, v):
            raise ValueError(
                "Название может содержать только буквы, цифры, пробелы и символы .,!?-:;"
            )
        return v


class BoardCreate(BoardBase):
    """Schema for creating a new board."""

    pass


class BoardResponse(BoardBase):
    """Schema for board response."""

    id: str
    user_id: str
    created_at: datetime
    columns: list[ColumnResponse] = Field(default_factory=list)

    class Config:
        """Pydantic config."""

        from_attributes = True


class BoardListResponse(BaseModel):
    """Schema for board list response."""

    boards: list[BoardResponse]
    total: int
    message: Optional[str] = None


class BoardDeleteResponse(BaseModel):
    """Schema for board deletion response."""

    message: str = "Board deleted successfully"


__all__ = [
    "ColumnResponse",
    "ColumnCreate",
    "BoardBase",
    "BoardCreate",
    "BoardResponse",
    "BoardListResponse",
    "BoardDeleteResponse",
]