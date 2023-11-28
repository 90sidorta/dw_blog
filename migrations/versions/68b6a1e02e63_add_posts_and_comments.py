"""add posts and comments

Revision ID: 68b6a1e02e63
Revises: 42e0045843c8
Create Date: 2023-11-10 11:35:50.673564

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "68b6a1e02e63"
down_revision: Union[str, None] = "42e0045843c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "post",
        sa.Column("text", sqlmodel.sql.sqltypes.AutoString(length=30000), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.Column("author_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("author_nickname", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_post_id"), "post", ["id"], unique=False)
    op.create_table(
        "comment",
        sa.Column("text", sqlmodel.sql.sqltypes.AutoString(length=10000), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_nickname", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("post_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["post_id"],
            ["post.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comment_id"), "comment", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_comment_id"), table_name="comment")
    op.drop_table("comment")
    op.drop_index(op.f("ix_post_id"), table_name="post")
    op.drop_table("post")
