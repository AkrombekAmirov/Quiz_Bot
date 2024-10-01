"""Initial migration

Revision ID: eb898471c52c
Revises: ff88b4b1a45d
Create Date: 2024-09-29 12:50:30.999867

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'eb898471c52c'
down_revision: Union[str, None] = 'ff88b4b1a45d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('question_correct_answer_id_fkey', 'question', type_='foreignkey')
    op.drop_column('question', 'correct_answer_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('correct_answer_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('question_correct_answer_id_fkey', 'question', 'answer', ['correct_answer_id'], ['id'])
    # ### end Alembic commands ###
