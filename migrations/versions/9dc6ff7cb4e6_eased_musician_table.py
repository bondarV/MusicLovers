"""Eased musician table

Revision ID: 9dc6ff7cb4e6
Revises: 12efceca5145
Create Date: 2024-12-26 09:48:43.004169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9dc6ff7cb4e6'
down_revision = '12efceca5145'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('musicians', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(length=50, collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('musicians', schema=None) as batch_op:
        batch_op.alter_column('type',
               existing_type=sa.VARCHAR(length=50, collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=False)

    # ### end Alembic commands ###
