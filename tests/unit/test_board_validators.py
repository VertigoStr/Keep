"""Unit tests for board validators."""

import pytest
from src.utils.board_validators import (
    validate_board_name,
    validate_board_limit,
    validate_board_ownership,
)


def test_validate_board_name_valid() -> None:
    """Test validating a valid board name."""
    assert validate_board_name("Мой проект") is True
    assert validate_board_name("Project 2024") is True
    assert validate_board_name("Test-Board") is True
    assert validate_board_name("Board: Test") is True
    assert validate_board_name("Board! Test?") is True


def test_validate_board_name_empty() -> None:
    """Test validating an empty board name."""
    assert validate_board_name("") is False
    assert validate_board_name("   ") is False


def test_validate_board_name_too_long() -> None:
    """Test validating a board name that exceeds max length."""
    long_name = "a" * 256
    assert validate_board_name(long_name) is False


def test_validate_board_name_invalid_characters() -> None:
    """Test validating a board name with invalid characters."""
    assert validate_board_name("Board@Name") is False
    assert validate_board_name("Board#Name") is False
    assert validate_board_name("Board$Name") is False
    assert validate_board_name("Board%Name") is False
    assert validate_board_name("Board&Name") is False
    assert validate_board_name("Board*Name") is False
    assert validate_board_name("Board+Name") is False
    assert validate_board_name("Board=Name") is False
    assert validate_board_name("Board/Name") is False
    assert validate_board_name("Board\\Name") is False
    assert validate_board_name("Board|Name") is False
    assert validate_board_name("Board<Name>") is False
    assert validate_board_name("Board>Name") is False
    assert validate_board_name("Board[Name]") is False
    assert validate_board_name("Board{Name}") is False
    assert validate_board_name("Board(Name)") is False
    assert validate_board_name("Board^Name") is False
    assert validate_board_name("Board~Name") is False
    assert validate_board_name("Board`Name") is False


def test_validate_board_name_max_length() -> None:
    """Test validating a board name at max length."""
    max_length_name = "a" * 255
    assert validate_board_name(max_length_name) is True


def test_validate_board_limit_within_limit() -> None:
    """Test validating board limit when within limit."""
    assert validate_board_limit(0) is True
    assert validate_board_limit(0, max_boards=1) is True


def test_validate_board_limit_at_limit() -> None:
    """Test validating board limit when at limit."""
    assert validate_board_limit(1, max_boards=1) is False
    assert validate_board_limit(2, max_boards=2) is False


def test_validate_board_limit_exceeded() -> None:
    """Test validating board limit when exceeded."""
    assert validate_board_limit(2, max_boards=1) is False
    assert validate_board_limit(5, max_boards=3) is False


def test_validate_board_limit_custom_max() -> None:
    """Test validating board limit with custom max."""
    assert validate_board_limit(2, max_boards=5) is True
    assert validate_board_limit(5, max_boards=5) is False
    assert validate_board_limit(6, max_boards=5) is False


def test_validate_board_ownership_valid() -> None:
    """Test validating board ownership when user owns the board."""
    assert validate_board_ownership("user-123", "user-123") is True


def test_validate_board_ownership_invalid() -> None:
    """Test validating board ownership when user doesn't own the board."""
    assert validate_board_ownership("user-123", "user-456") is False
    assert validate_board_ownership("user-1", "user-2") is False


def test_validate_board_ownership_empty_ids() -> None:
    """Test validating board ownership with empty IDs."""
    assert validate_board_ownership("", "") is True
    assert validate_board_ownership("user-123", "") is False
    assert validate_board_ownership("", "user-123") is False