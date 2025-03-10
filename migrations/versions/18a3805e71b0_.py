"""empty message

Revision ID: 18a3805e71b0
Revises: 63ddbacde0f4
Create Date: 2024-12-25 16:57:21.285458

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mssql

# revision identifiers, used by Alembic.
revision = '18a3805e71b0'
down_revision = '63ddbacde0f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('sysdiagrams')
    with op.batch_alter_table('musicians', schema=None) as batch_op:
        batch_op.alter_column('country',
               existing_type=sa.VARCHAR(length=3, collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('musicians', schema=None) as batch_op:
        batch_op.alter_column('country',
               existing_type=sa.VARCHAR(length=3, collation='SQL_Latin1_General_CP1_CI_AS'),
               nullable=False)

    op.create_table('sysdiagrams',
    sa.Column('name', sa.NVARCHAR(length=128, collation='SQL_Latin1_General_CP1_CI_AS'), autoincrement=False, nullable=False),
    sa.Column('principal_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('diagram_id', sa.INTEGER(), sa.Identity(always=False, start=1, increment=1), autoincrement=True, nullable=False),
    sa.Column('version', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('definition', mssql.VARBINARY(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('diagram_id', name='PK__sysdiagr__C2B05B6109F87D26')
    )
    # ### end Alembic commands ###
