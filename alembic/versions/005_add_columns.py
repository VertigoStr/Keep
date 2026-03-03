"""Add columns table

Revision ID: 005_add_columns
Revises: 004_add_boards
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_add_columns'
down_revision: Union[str, None] = '004_add_boards'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create columns table
    op.create_table(
        'columns',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('board_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['board_id'], ['boards.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_columns_board_id', 'columns', ['board_id'])
    op.create_index('uq_board_column_order', 'columns', ['board_id', 'order'], unique=True)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('uq_board_column_order', table_name='columns')
    op.drop_index('idx_columns_board_id', table_name='columns')
    
    # Drop table
    op.drop_table('columns')