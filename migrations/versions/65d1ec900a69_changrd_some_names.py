"""changrd some names

Revision ID: 65d1ec900a69
Revises: 
Create Date: 2024-08-20 12:14:13.085639

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '65d1ec900a69'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('adminuser', schema=None) as batch_op:
        batch_op.add_column(sa.Column('adminemail', sa.String(length=150), nullable=False))
        batch_op.drop_index('email')
        batch_op.create_unique_constraint(None, ['adminemail'])
        batch_op.drop_column('email')

    with op.batch_alter_table('collectoruser', schema=None) as batch_op:
        batch_op.add_column(sa.Column('collectoremail', sa.String(length=150), nullable=False))
        batch_op.drop_index('email')
        batch_op.create_unique_constraint(None, ['collectoremail'])
        batch_op.drop_column('email')

    with op.batch_alter_table('houseuser', schema=None) as batch_op:
        batch_op.add_column(sa.Column('houseemail', sa.String(length=150), nullable=False))
        batch_op.drop_index('email')
        batch_op.create_unique_constraint(None, ['houseemail'])
        batch_op.drop_column('email')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('houseuser', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', mysql.VARCHAR(length=150), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index('email', ['email'], unique=True)
        batch_op.drop_column('houseemail')

    with op.batch_alter_table('collectoruser', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', mysql.VARCHAR(length=150), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index('email', ['email'], unique=True)
        batch_op.drop_column('collectoremail')

    with op.batch_alter_table('adminuser', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email', mysql.VARCHAR(length=150), nullable=False))
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_index('email', ['email'], unique=True)
        batch_op.drop_column('adminemail')

    # ### end Alembic commands ###
