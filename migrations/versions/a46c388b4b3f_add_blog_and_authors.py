"""add blog and authors

Revision ID: a46c388b4b3f
Revises: 1bd3ba007d01
Create Date: 2023-11-14 20:02:40.891752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = "a46c388b4b3f"
down_revision: Union[str, None] = "1bd3ba007d01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "blog",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=False),
        sa.Column("date_modified", sa.DateTime(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_blog_id"), "blog", ["id"], unique=False)
    op.create_table(
        "blogauthors",
        sa.Column("blog_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("author_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["blog_id"],
            ["blog.id"],
        ),
        sa.PrimaryKeyConstraint("blog_id", "author_id"),
    )
    op.add_column("post", sa.Column("blog_id", sqlmodel.sql.sqltypes.GUID(), nullable=False))
    op.add_column("tag", sa.Column("blog_id", sqlmodel.sql.sqltypes.GUID(), nullable=True))
    op.create_foreign_key(None, "tag", "blog", ["blog_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint(None, "tag", type_="foreignkey")
    op.drop_column("tag", "blog_id")
    op.drop_column("post", "blog_id")
    op.drop_table("blogauthors")
    op.drop_index(op.f("ix_blog_id"), table_name="blog")
    op.drop_table("blog")
