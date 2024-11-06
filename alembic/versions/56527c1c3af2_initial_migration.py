"""Initial migration

Revision ID: 56527c1c3af2
Revises: 5d68d3d35317
Create Date: 2024-10-01 12:58:59.744987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '56527c1c3af2'
down_revision: Union[str, None] = '5d68d3d35317'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('result',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('test_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.Column('question_ids', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('correct_answers', sa.Integer(), nullable=False),
    sa.Column('wrong_answers', sa.Integer(), nullable=False),
    sa.Column('number', sa.Integer(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('result')
    # ### end Alembic commands ###