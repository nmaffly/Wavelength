"""share token row in user table

Revision ID: 9d2041d54c08
Revises: 3381a0211b3c
Create Date: 2024-03-13 00:26:44.112711

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d2041d54c08'
down_revision = '3381a0211b3c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('share_token', sa.String(length=5), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('share_token')

    # ### end Alembic commands ###
