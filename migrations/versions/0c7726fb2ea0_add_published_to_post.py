"""add published to post

Revision ID: 0c7726fb2ea0
Revises: 68b6a1e02e63
Create Date: 2023-11-12 19:16:44.883916

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0c7726fb2ea0"
down_revision: Union[str, None] = "68b6a1e02e63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("post", sa.Column("published", sa.Boolean(), nullable=False))


def downgrade() -> None:
    op.drop_column("post", "published")
