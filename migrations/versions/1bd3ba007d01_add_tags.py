"""add tags

Revision ID: 1bd3ba007d01
Revises: 0c7726fb2ea0
Create Date: 2023-11-12 21:23:24.652549

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1bd3ba007d01"
down_revision: Union[str, None] = "0c7726fb2ea0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tag",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_tag_id"), "tag", ["id"], unique=False)
    op.create_table(
        "tagposts",
        sa.Column("tag_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("post_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["post.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
        ),
        sa.PrimaryKeyConstraint("tag_id", "post_id"),
    )


def downgrade() -> None:
    op.drop_table("tagposts")
    op.drop_index(op.f("ix_tag_id"), table_name="tag")
    op.drop_table("tag")
