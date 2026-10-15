"""Add session ordering to databases created by an older initial migration.

Revision ID: 0002_session_sequence
Revises: 0001_domain
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_session_sequence"
down_revision = "0001_domain"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if "sequence_index" in {
        column["name"]
        for column in sa.inspect(bind).get_columns("teaching_sessions")
    }:
        return

    op.add_column(
        "teaching_sessions",
        sa.Column("sequence_index", sa.Integer(), nullable=False, server_default="1"),
    )

    rows = bind.execute(
        sa.text(
            "SELECT id, topic_id FROM teaching_sessions "
            "ORDER BY topic_id, created_at, id"
        )
    )
    sequence_by_topic: dict[str, int] = {}
    for session_id, topic_id in rows:
        sequence = sequence_by_topic.get(topic_id, 0) + 1
        sequence_by_topic[topic_id] = sequence
        bind.execute(
            sa.text(
                "UPDATE teaching_sessions SET sequence_index = :sequence "
                "WHERE id = :session_id"
            ),
            {"sequence": sequence, "session_id": session_id},
        )

    op.create_index(
        "ix_teaching_sessions_topic_sequence_compat",
        "teaching_sessions",
        ["topic_id", "sequence_index"],
        unique=True,
    )


def downgrade() -> None:
    bind = op.get_bind()
    if "sequence_index" not in {
        column["name"]
        for column in sa.inspect(bind).get_columns("teaching_sessions")
    }:
        return
    indexes = {
        index["name"] for index in sa.inspect(bind).get_indexes("teaching_sessions")
    }
    if "ix_teaching_sessions_topic_sequence_compat" in indexes:
        op.drop_index(
            "ix_teaching_sessions_topic_sequence_compat",
            table_name="teaching_sessions",
        )
    with op.batch_alter_table("teaching_sessions") as batch_op:
        batch_op.drop_column("sequence_index")
