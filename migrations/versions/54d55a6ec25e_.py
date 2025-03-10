"""empty message

Revision ID: 54d55a6ec25e
Revises: 056cf6d861a8
Create Date: 2024-12-25 21:42:46.893747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54d55a6ec25e'
down_revision = '056cf6d861a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_records', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', sa.Float(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_records', schema=None) as batch_op:
        batch_op.drop_column('rating')

    # ### end Alembic commands ###
