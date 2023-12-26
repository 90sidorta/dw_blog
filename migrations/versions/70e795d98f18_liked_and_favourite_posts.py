"""liked and favourite posts

Revision ID: 70e795d98f18
Revises: 6829a58b99b8
Create Date: 2023-12-26 17:13:52.915281

"""
from typing import Sequence, Union

from alembic import op
import sqlmodel
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '70e795d98f18'
down_revision: Union[str, None] = '6829a58b99b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('postfavourites',
    sa.Column('post_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('favouriter_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['favouriter_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.PrimaryKeyConstraint('post_id', 'favouriter_id')
    )
    op.create_table('postlikers',
    sa.Column('post_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('liker_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['liker_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.PrimaryKeyConstraint('post_id', 'liker_id')
    )
    op.drop_table('song')


def downgrade() -> None:
    op.create_table('song',
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('artist', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id', name='song_pkey')
    )
    op.drop_table('postlikers')
    op.drop_table('postfavourites')
