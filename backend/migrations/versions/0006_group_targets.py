from alembic import op
import sqlalchemy as sa

revision = "0006_group_targets"
down_revision = "0005_smart_setup"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "benchmarks",
        sa.Column(
            "group_id",
            sa.String(36),
            sa.ForeignKey("instructor_groups.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("stable_id", sa.String(80), primary_key=True),
        sa.Column("target_date", sa.Date(), nullable=False),
    )


def downgrade():
    raise RuntimeError(
        "Removing benchmark data requires a separate local data decision."
    )
