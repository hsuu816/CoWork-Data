"""tracking table

Revision ID: c14dc2dd026e
Revises: e32bb2d4f116
Create Date: 2021-03-20 10:21:19.282338

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c14dc2dd026e'
down_revision = 'e32bb2d4f116'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tracking_analysis',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.Column('all_user_count', sa.Integer(), nullable=True),
    sa.Column('active_user_count', sa.Integer(), nullable=True),
    sa.Column('new_user_count', sa.Integer(), nullable=True),
    sa.Column('return_user_count', sa.Integer(), nullable=True),
    sa.Column('view_count', sa.Integer(), nullable=True),
    sa.Column('view_item_count', sa.Integer(), nullable=True),
    sa.Column('add_to_cart_count', sa.Integer(), nullable=True),
    sa.Column('checkout_count', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date')
    )
    op.create_table('tracking_raw',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('request_url', sa.Text(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tracking_realtime',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.String(length=127), nullable=False),
    sa.Column('time', sa.TIMESTAMP(), nullable=False),
    sa.Column('event_type', sa.String(length=255), nullable=False),
    sa.Column('view_detail', sa.String(length=255), nullable=True),
    sa.Column('item_id', sa.Integer(), nullable=True),
    sa.Column('checkout_step', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tracking_realtime')
    op.drop_table('tracking_raw')
    op.drop_table('tracking_analysis')
    # ### end Alembic commands ###
