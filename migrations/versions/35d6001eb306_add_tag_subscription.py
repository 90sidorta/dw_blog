"""add tag subscription

Revision ID: 35d6001eb306
Revises: 7704dcae2f1d
Create Date: 2023-12-05 09:48:05.742954

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '35d6001eb306'
down_revision: Union[str, None] = '7704dcae2f1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tagsubscribers',
    sa.Column('tag_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('subscriber_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['subscriber_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'subscriber_id')
    )


def downgrade() -> None:
    op.drop_table('tagsubscribers')
