"""change usertype enum author to admin

Revision ID: 2be4b6709478
Revises: a46c388b4b3f
Create Date: 2023-11-14 20:07:27.553585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2be4b6709478'
down_revision: Union[str, None] = 'a46c388b4b3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE usertype RENAME VALUE 'author' TO 'admin'")



def downgrade() -> None:
    op.execute("ALTER TYPE usertype RENAME VALUE 'admin' TO 'author'")
