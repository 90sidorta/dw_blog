"""add user model

Revision ID: 42e0045843c8
Revises: f03a36613183
Create Date: 2023-11-08 07:59:17.819087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '42e0045843c8'
down_revision: Union[str, None] = 'f03a36613183'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
    sa.Column('nickname', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('user_type', sa.Enum('author', 'regular', name='usertype'), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
    sa.Column('password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('nickname')
    )
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_table('user')
