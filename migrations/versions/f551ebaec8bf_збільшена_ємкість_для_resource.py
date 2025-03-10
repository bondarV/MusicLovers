"""Збільшена ємкість для resource

Revision ID: f551ebaec8bf
Revises: 41057daea426
Create Date: 2024-12-23 19:05:25.562424

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f551ebaec8bf'
down_revision = '41057daea426'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('urls', schema=None) as batch_op:
        batch_op.alter_column('resource',
               existing_type=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               type_=sa.String(length=200),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('urls', schema=None) as batch_op:
        batch_op.alter_column('resource',
               existing_type=sa.String(length=200),
               type_=sa.VARCHAR(length=100, collation='SQL_Latin1_General_CP1_CI_AS'),
               existing_nullable=False)

    # ### end Alembic commands ###
