"""Add column_id to tasks table

Revision ID: 006_add_task_column
Revises: 005_add_columns
Create Date: 2026-03-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '006_add_task_column'
down_revision: Union[str, None] = '005_add_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add column_id column to tasks table
    op.add_column(
        'tasks',
        sa.Column('column_id', sa.String(), nullable=True)
    )
    
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_tasks_column_id',
        'tasks', 'columns',
        ['column_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create index
    op.create_index('idx_tasks_column_id', 'tasks', ['column_id'])


def downgrade() -> None:
    # Drop index
    op.drop_index('idx_tasks_column_id', table_name='tasks')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_tasks_column_id', 'tasks', type_='foreignkey')
    
    # Drop column
    op.drop_column('tasks', 'column_id')