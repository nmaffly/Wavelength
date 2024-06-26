"""more rows for artist and track info

Revision ID: a4f4d121194f
Revises: 9a83cc3b5619
Create Date: 2024-03-29 22:34:00.689444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4f4d121194f'
down_revision = '9a83cc3b5619'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('all_time_artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('img_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('spotify_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('href', sa.String(length=100), nullable=True))

    with op.batch_alter_table('all_time_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('album_art_img_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('preview_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('spotify_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('href', sa.String(length=100), nullable=True))

    with op.batch_alter_table('medium_artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('img_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('spotify_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('href', sa.String(length=100), nullable=True))

    with op.batch_alter_table('medium_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('album_art_img_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('preview_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('spotify_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('href', sa.String(length=100), nullable=True))

    with op.batch_alter_table('recent_artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('img_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('spotify_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('href', sa.String(length=100), nullable=True))

    with op.batch_alter_table('recent_tracks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('album_art_img_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('preview_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('spotify_url', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('href', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recent_tracks', schema=None) as batch_op:
        batch_op.drop_column('href')
        batch_op.drop_column('spotify_url')
        batch_op.drop_column('preview_url')
        batch_op.drop_column('album_art_img_url')

    with op.batch_alter_table('recent_artists', schema=None) as batch_op:
        batch_op.drop_column('href')
        batch_op.drop_column('spotify_url')
        batch_op.drop_column('img_url')

    with op.batch_alter_table('medium_tracks', schema=None) as batch_op:
        batch_op.drop_column('href')
        batch_op.drop_column('spotify_url')
        batch_op.drop_column('preview_url')
        batch_op.drop_column('album_art_img_url')

    with op.batch_alter_table('medium_artists', schema=None) as batch_op:
        batch_op.drop_column('href')
        batch_op.drop_column('spotify_url')
        batch_op.drop_column('img_url')

    with op.batch_alter_table('all_time_tracks', schema=None) as batch_op:
        batch_op.drop_column('href')
        batch_op.drop_column('spotify_url')
        batch_op.drop_column('preview_url')
        batch_op.drop_column('album_art_img_url')

    with op.batch_alter_table('all_time_artists', schema=None) as batch_op:
        batch_op.drop_column('href')
        batch_op.drop_column('spotify_url')
        batch_op.drop_column('img_url')

    # ### end Alembic commands ###
