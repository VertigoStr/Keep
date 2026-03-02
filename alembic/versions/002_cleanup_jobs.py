"""Add cleanup jobs for expired sessions and old failed login attempts

Revision ID: 002_cleanup_jobs
Revises: 001_initial
Create Date: 2026-03-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_cleanup_jobs'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This migration is a placeholder for cleanup job configuration
    # Actual cleanup jobs will be implemented as background tasks
    # or scheduled jobs using APScheduler or similar
    
    # Add comment to sessions table to indicate cleanup policy
    op.execute("""
        COMMENT ON TABLE sessions IS 'User sessions with 24-hour expiration. Expired sessions should be cleaned up periodically.'
    """)
    
    # Add comment to failed_login_attempts table to indicate cleanup policy
    op.execute("""
        COMMENT ON TABLE failed_login_attempts IS 'Failed login attempts for rate limiting. Records older than 24 hours should be cleaned up periodically.'
    """)


def downgrade() -> None:
    # Remove comments
    op.execute("COMMENT ON TABLE sessions IS NULL")
    op.execute("COMMENT ON TABLE failed_login_attempts IS NULL")