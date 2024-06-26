"""altered matches configuration again

Revision ID: bb7fb06cb4fd
Revises: 8640ffeb6ba2
Create Date: 2024-04-12 12:38:57.043351

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'bb7fb06cb4fd'
down_revision = '8640ffeb6ba2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user1_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('user2_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('compatibility', sa.Float(), nullable=True))
        batch_op.drop_constraint('matches_ibfk_1', type_='foreignkey')
        batch_op.drop_constraint('matches_ibfk_2', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['user2_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key(None, 'user', ['user1_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('compatibility_score')
        batch_op.drop_column('user_2_id')
        batch_op.drop_column('user_1_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('matches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_1_id', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('user_2_id', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('compatibility_score', mysql.FLOAT(), nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('matches_ibfk_2', 'user', ['user_1_id'], ['id'], ondelete='CASCADE')
        batch_op.create_foreign_key('matches_ibfk_1', 'user', ['user_2_id'], ['id'], ondelete='CASCADE')
        batch_op.drop_column('compatibility')
        batch_op.drop_column('user2_id')
        batch_op.drop_column('user1_id')

    # ### end Alembic commands ###
