"""Add task ownership

Revision ID: 34fb71c57e71
Revises: 7a08b3b58d68
Create Date: 2026-10-06 15:26:03.880479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34fb71c57e71'
down_revision: Union[str, Sequence[str], None] = '7a08b3b58d68'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'tasks',
        sa.Column('user_id', sa.Integer(), nullable=True)
    )

    op.execute(
        "UPDATE tasks SET user_id = 1 WHERE user_id IS NULL"
    )

    op.create_foreign_key(
        'fk_tasks_user_id_users',
        'tasks',
        'users',
        ['user_id'],
        ['id']
    )

    op.alter_column(
        'tasks',
        'user_id',
        nullable=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        'fk_tasks_user_id_users',
        'tasks',
        type_='foreignkey'
    )

    op.drop_column('tasks', 'user_id')