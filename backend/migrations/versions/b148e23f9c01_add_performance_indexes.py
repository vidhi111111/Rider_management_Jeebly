"""add performance indexes for query optimization

Revision ID: b148e23f9c01
Revises: 0543125baca4
Create Date: 2026-11-13 13:51:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b148e23f9c01'
down_revision = '0543125baca4'
branch_labels = None
depends_on = None


def upgrade():
    # Indexes for table 'rider'
    with op.batch_alter_table('rider', schema=None) as batch_op:
        batch_op.create_index('ix_rider_status', ['status'], unique=False)
        batch_op.create_index('ix_rider_mobile', ['mobile'], unique=False)
        batch_op.create_index('ix_rider_email', ['email'], unique=False)
        batch_op.create_index('ix_rider_availability', ['availability'], unique=False)
        batch_op.create_index('ix_rider_status_availability', ['status', 'availability'], unique=False)

    # Indexes for table 'order'
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.create_index('ix_order_status', ['status'], unique=False)
        batch_op.create_index('ix_order_created_at', ['created_at'], unique=False)
        batch_op.create_index('ix_order_rider_id', ['rider_id'], unique=False)
        batch_op.create_index('ix_order_rider_id_status', ['rider_id', 'status'], unique=False)


def downgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_index('ix_order_rider_id_status')
        batch_op.drop_index('ix_order_rider_id')
        batch_op.drop_index('ix_order_created_at')
        batch_op.drop_index('ix_order_status')

    with op.batch_alter_table('rider', schema=None) as batch_op:
        batch_op.drop_index('ix_rider_status_availability')
        batch_op.drop_index('ix_rider_availability')
        batch_op.drop_index('ix_rider_email')
        batch_op.drop_index('ix_rider_mobile')
        batch_op.drop_index('ix_rider_status')
