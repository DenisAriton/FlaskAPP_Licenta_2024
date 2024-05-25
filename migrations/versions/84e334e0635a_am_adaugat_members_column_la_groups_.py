"""Am adaugat members column la Groups pentru a retine cati membrii are detine grupa!

Revision ID: 84e334e0635a
Revises: fb308a48e829
Create Date: 2024-05-21 21:57:08.695299

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '84e334e0635a'
down_revision = 'fb308a48e829'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.add_column(sa.Column('members', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('groups', schema=None) as batch_op:
        batch_op.drop_column('members')

    # ### end Alembic commands ###
