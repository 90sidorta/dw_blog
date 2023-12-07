"""change post model

Revision ID: 6829a58b99b8
Revises: 35d6001eb306
Create Date: 2023-12-07 19:40:56.575509

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6829a58b99b8'
down_revision: Union[str, None] = '35d6001eb306'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('image',
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
    sa.Column('caption', sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('img_type', sa.Enum('GIF', 'BMP', 'JPEG', 'JPG', 'PNG', 'SVG', 'TIFF', 'WEBP', name='imagetype'), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=False),
    sa.Column('date_modified', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_image_id'), 'image', ['id'], unique=False)
    op.create_table('postauthors',
    sa.Column('post_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('author_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.PrimaryKeyConstraint('post_id', 'author_id')
    )
    op.create_unique_constraint(None, 'blog', ['name'])
    op.add_column('post', sa.Column('notes', postgresql.ARRAY(sa.String(length=1500)), nullable=True))
    op.add_column('post', sa.Column('bibliography', postgresql.ARRAY(sa.String(length=3500)), nullable=True))
    op.add_column('post', sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False))
    op.add_column('post', sa.Column('body', sqlmodel.sql.sqltypes.AutoString(length=10000), nullable=False))
    op.alter_column('post', 'blog_id',
               existing_type=postgresql.UUID(),
               nullable=True)
    op.create_unique_constraint('_blog_post_title_uc', 'post', ['title', 'blog_id'])
    op.create_foreign_key(None, 'post', 'blog', ['blog_id'], ['id'])
    op.drop_column('post', 'author_nickname')
    op.drop_column('post', 'text')
    op.drop_column('post', 'author_id')


def downgrade() -> None:
    op.add_column('post', sa.Column('author_id', postgresql.UUID(), autoincrement=False, nullable=False))
    op.add_column('post', sa.Column('text', sa.VARCHAR(length=30000), autoincrement=False, nullable=False))
    op.add_column('post', sa.Column('author_nickname', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'post', type_='foreignkey')
    op.drop_constraint('_blog_post_title_uc', 'post', type_='unique')
    op.alter_column('post', 'blog_id',
               existing_type=postgresql.UUID(),
               nullable=False)
    op.drop_column('post', 'body')
    op.drop_column('post', 'title')
    op.drop_column('post', 'bibliography')
    op.drop_column('post', 'notes')
    op.drop_constraint(None, 'blog', type_='unique')
    op.drop_table('postauthors')
    op.drop_index(op.f('ix_image_id'), table_name='image')
    op.drop_table('image')
