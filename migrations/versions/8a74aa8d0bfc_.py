"""empty message

Revision ID: 8a74aa8d0bfc
Revises: 8d46a831f91d
Create Date: 2024-03-30 18:06:42.586536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a74aa8d0bfc'
down_revision = '8d46a831f91d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('all_time_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('track_id', sa.String(length=100), nullable=True))

    with op.batch_alter_table('medium_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('track_id', sa.String(length=100), nullable=True))

    with op.batch_alter_table('recent_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('track_id', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recent_tracks', schema=None) as batch_op:
        batch_op.drop_column('track_id')

    with op.batch_alter_table('medium_tracks', schema=None) as batch_op:
        batch_op.drop_column('track_id')

    with op.batch_alter_table('all_time_tracks', schema=None) as batch_op:
        batch_op.drop_column('track_id')

    # ### end Alembic commands ###
