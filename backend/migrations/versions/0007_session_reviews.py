from alembic import op
import sqlalchemy as sa

revision = "0007_session_reviews"
down_revision = "0006_group_targets"
branch_labels = None
depends_on = None


def key():
    return sa.Column("id", sa.String(36), primary_key=True)


def ref(name, table, unique=False):
    return sa.Column(
        name,
        sa.String(36),
        sa.ForeignKey(table + ".id", ondelete="CASCADE"),
        nullable=False,
        unique=unique,
    )


def state_fields():
    return [
        sa.Column("mode", sa.String(16), nullable=False),
        sa.Column("state", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def upgrade():
    op.create_table(
        "session_reviews",
        key(),
        ref("group_id", "instructor_groups"),
        ref("session_id", "teaching_sessions"),
        sa.Column("transcript", sa.Text(), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
        *state_fields(),
    )
    op.create_table(
        "follow_ups",
        key(),
        ref("review_id", "session_reviews", True),
        sa.Column("items", sa.JSON(), nullable=False),
        *state_fields(),
    )
    op.create_table(
        "approval_events",
        key(),
        ref("course_id", "courses"),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("item", sa.String(40), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    raise RuntimeError(
        "Removing review history requires an explicit local data decision."
    )
