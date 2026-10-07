"""Set refresh token revoked default

Revision ID: 8031981db418
Revises: 085f65b82c24
Create Date: 2026-10-07 17:00:51.322237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8031981db418'
down_revision: Union[str, Sequence[str], None] = '085f65b82c24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "refresh_tokens",
        "revoked",
        server_default=sa.false()
    )


def downgrade() -> None:
    op.alter_column(
        "refresh_tokens",
        "revoked",
        server_default=None
    )