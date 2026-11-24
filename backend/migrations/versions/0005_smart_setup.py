"""Store structured local schedules and extracted evidence."""

from alembic import op
import sqlalchemy as sa

revision = "0005_smart_setup"
down_revision = "0004_session_graph"
branch_labels = None
depends_on = None


def upgrade():
    for name, kind in [
        ("weekday", sa.String(12)),
        ("start_time", sa.String(5)),
        ("start_date", sa.Date()),
    ]:
        op.add_column("instructor_groups", sa.Column(name, kind))
    op.add_column(
        "teaching_sessions",
        sa.Column(
            "supporting_chunk_ids", sa.JSON(), nullable=False, server_default="[]"
        ),
    )
    op.create_table(
        "material_chunks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "material_id",
            sa.String(36),
            sa.ForeignKey("materials.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("locator", sa.Text(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.UniqueConstraint("material_id", "position"),
    )


def downgrade():
    raise RuntimeError(
        "Keep stored source evidence. Restore a disposable test database to roll back."
    )
