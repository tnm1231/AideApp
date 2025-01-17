"""empty message

Revision ID: ff53991570c5
Revises: 
Create Date: 2024-11-26 09:21:17.442958

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff53991570c5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('check_log',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('check_type', sa.String(length=50), nullable=False),
    sa.Column('sepecific_file', sa.String(length=255), nullable=True),
    sa.Column('custom_config', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('check_log')
    # ### end Alembic commands ###
