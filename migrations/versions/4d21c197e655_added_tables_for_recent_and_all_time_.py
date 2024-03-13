"""added tables for recent and all time songs

Revision ID: 4d21c197e655
Revises: ec25e9191bc4
Create Date: 2024-03-12 23:18:21.784728

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d21c197e655'
down_revision = 'ec25e9191bc4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('all_time_songs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_stats_id', sa.Integer(), nullable=False),
    sa.Column('song', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['user_stats_id'], ['user_stats.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recent_songs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_stats_id', sa.Integer(), nullable=False),
    sa.Column('song', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['user_stats_id'], ['user_stats.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recent_songs')
    op.drop_table('all_time_songs')
    # ### end Alembic commands ###
