"""Add pid column to task_record table

Revision ID: 47df9ea9fcc3
Revises: 15cf38979f82
Create Date: 2025-01-09 10:41:54.167695

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '47df9ea9fcc3'
down_revision = '15cf38979f82'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('result_scan', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=sa.NUMERIC(precision=100),
               type_=sa.String(length=100),
               existing_nullable=True)

    with op.batch_alter_table('task_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pid', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task_record', schema=None) as batch_op:
        batch_op.drop_column('pid')

    with op.batch_alter_table('result_scan', schema=None) as batch_op:
        batch_op.alter_column('timestamp',
               existing_type=sa.String(length=100),
               type_=sa.NUMERIC(precision=100),
               existing_nullable=True)

    # ### end Alembic commands ###