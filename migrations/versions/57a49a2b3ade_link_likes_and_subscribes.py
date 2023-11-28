"""link likes and subscribes

Revision ID: 57a49a2b3ade
Revises: 2be4b6709478
Create Date: 2023-11-24 19:26:09.025166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "57a49a2b3ade"
down_revision: Union[str, None] = "2be4b6709478"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bloglikes",
        sa.Column("blog_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("liker_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["blog_id"],
            ["blog.id"],
        ),
        sa.ForeignKeyConstraint(
            ["liker_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("blog_id", "liker_id"),
    )
    op.create_table(
        "blogsubscribers",
        sa.Column("blog_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("subscriber_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["blog_id"],
            ["blog.id"],
        ),
        sa.ForeignKeyConstraint(
            ["subscriber_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("blog_id", "subscriber_id"),
    )
    op.add_column("blog", sa.Column("archived", sa.Boolean(), nullable=True))
    op.execute("UPDATE blog SET archived = false")
    op.alter_column("blog", "archived", nullable=False)


def downgrade() -> None:
    op.drop_column("blog", "archived")
    op.drop_table("blogsubscribers")
    op.drop_table("bloglikes")
