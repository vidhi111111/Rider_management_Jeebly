from alembic import op
import sqlalchemy as sa

revision = "0543125baca4"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("order", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("rider_id", sa.Integer(), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("order", schema=None) as batch_op:
        batch_op.drop_column("rider_id")