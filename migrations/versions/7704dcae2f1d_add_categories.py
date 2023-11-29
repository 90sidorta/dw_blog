"""add categories

Revision ID: 7704dcae2f1d
Revises: 57a49a2b3ade
Create Date: 2023-11-29 11:41:03.678568

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '7704dcae2f1d'
down_revision: Union[str, None] = '57a49a2b3ade'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('category',
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_modified', sa.DateTime(), nullable=False),
    sa.Column('approved', sa.Boolean(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint("name"),
    )
    op.create_index(op.f('ix_category_id'), 'category', ['id'], unique=False)
    op.create_table('categoryblogs',
    sa.Column('category_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('blog_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['blog_id'], ['blog.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('category_id', 'blog_id')
    )


def downgrade() -> None:
    op.drop_table('categoryblogs')
    op.drop_index(op.f('ix_category_id'), table_name='category')
    op.drop_table('category')
