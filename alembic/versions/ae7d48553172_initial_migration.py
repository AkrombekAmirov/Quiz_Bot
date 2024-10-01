"""Initial migration

Revision ID: ae7d48553172
Revises: 7a3467c77a46
Create Date: 2024-10-01 10:36:06.102513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'ae7d48553172'
down_revision: Union[str, None] = '7a3467c77a46'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('answer_question_id_fkey', 'answer', type_='foreignkey')
    op.drop_constraint('question_subject_id_fkey', 'question', type_='foreignkey')
    op.drop_constraint('result_user_id_fkey', 'result', type_='foreignkey')
    op.drop_constraint('result_answer_id_fkey', 'result', type_='foreignkey')
    op.drop_constraint('result_question_id_fkey', 'result', type_='foreignkey')
    op.add_column('subject', sa.Column('ansver_value', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('test', sa.Column('number', sa.Integer(), nullable=False))
    op.add_column('test', sa.Column('status', sa.Boolean(), nullable=False))
    op.drop_constraint('test_subject_id_fkey', 'test', type_='foreignkey')
    op.drop_constraint('test_user_id_fkey', 'test', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('test_user_id_fkey', 'test', 'user', ['user_id'], ['id'])
    op.create_foreign_key('test_subject_id_fkey', 'test', 'subject', ['subject_id'], ['id'])
    op.drop_column('test', 'status')
    op.drop_column('test', 'number')
    op.drop_column('subject', 'ansver_value')
    op.create_foreign_key('result_question_id_fkey', 'result', 'question', ['question_id'], ['id'])
    op.create_foreign_key('result_answer_id_fkey', 'result', 'answer', ['answer_id'], ['id'])
    op.create_foreign_key('result_user_id_fkey', 'result', 'user', ['user_id'], ['id'])
    op.create_foreign_key('question_subject_id_fkey', 'question', 'subject', ['subject_id'], ['id'])
    op.create_foreign_key('answer_question_id_fkey', 'answer', 'question', ['question_id'], ['id'])
    # ### end Alembic commands ###
