"""Board validators for business logic validation."""

import re


def validate_board_name(name: str) -> bool:
    """Validate board name meets requirements.

    Requirements:
    - Not empty
    - Maximum 255 characters
    - Only letters, numbers, spaces and symbols: .,!?-:;

    Args:
        name: Board name to validate

    Returns:
        True if name is valid, False otherwise
    """
    if not name:
        return False

    if len(name) > 255:
        return False

    # Allow letters, numbers, spaces and basic punctuation: .,!?-:;
    pattern = r"^[\p{L}\p{N}\s.,!?\-:;]+$"
    return re.match(pattern, name) is not None


def validate_board_limit(current_board_count: int, max_boards: int = 1) -> bool:
    """Validate user hasn't exceeded board limit.

    Args:
        current_board_count: Current number of boards owned by user
        max_boards: Maximum allowed boards per user (default: 1)

    Returns:
        True if user can create more boards, False otherwise
    """
    return current_board_count < max_boards


def validate_board_ownership(board_user_id: str, current_user_id: str) -> bool:
    """Validate user owns the board.

    Args:
        board_user_id: ID of the user who owns the board
        current_user_id: ID of the current user

    Returns:
        True if user owns the board, False otherwise
    """
    return board_user_id == current_user_id


__all__ = [
    "validate_board_name",
    "validate_board_limit",
    "validate_board_ownership",
]