"""Add boards table

Revision ID: 004_add_boards
Revises: 003_add_tasks
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_add_boards'
down_revision: Union[str, None] = '003_add_tasks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create boards table
    op.create_table(
        'boards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_user_board_name')
    )
    
    # Create indexes
    op.create_index('idx_boards_user_id', 'boards', ['user_id'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_boards_user_id', table_name='boards')
    
    # Drop table
    op.drop_table('boards')