"""added artists to each track

Revision ID: 1f7a993e768a
Revises: ac2d60092922
Create Date: 2024-04-11 19:25:29.776024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f7a993e768a'
down_revision = 'ac2d60092922'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('all_time_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist', sa.String(length=100), nullable=True))

    with op.batch_alter_table('medium_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist', sa.String(length=100), nullable=True))

    with op.batch_alter_table('recent_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('artist', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recent_tracks', schema=None) as batch_op:
        batch_op.drop_column('artist')

    with op.batch_alter_table('medium_tracks', schema=None) as batch_op:
        batch_op.drop_column('artist')

    with op.batch_alter_table('all_time_tracks', schema=None) as batch_op:
        batch_op.drop_column('artist')

    # ### end Alembic commands ###
