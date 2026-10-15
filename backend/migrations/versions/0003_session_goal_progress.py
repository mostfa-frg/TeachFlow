"""Add per-session objectives and group goal completion.

Revision ID: 0003_session_goal_progress
Revises: 0002_session_sequence
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_session_goal_progress"
down_revision = "0002_session_sequence"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    session_columns = {c["name"] for c in sa.inspect(bind).get_columns("teaching_sessions")}
    if "learning_objectives" not in session_columns:
        op.add_column("teaching_sessions", sa.Column("learning_objectives", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
        bind.execute(sa.text("UPDATE teaching_sessions SET learning_objectives = (SELECT topics.learning_objectives FROM topics WHERE topics.id = teaching_sessions.topic_id) WHERE EXISTS (SELECT 1 FROM topics WHERE topics.id = teaching_sessions.topic_id)"))
    progress_columns = {c["name"] for c in sa.inspect(bind).get_columns("group_session_progress")}
    if "completed_objective_indexes" not in progress_columns:
        op.add_column("group_session_progress", sa.Column("completed_objective_indexes", sa.JSON(), nullable=False, server_default=sa.text("'[]'")))


def downgrade() -> None:
    bind = op.get_bind()
    progress_columns = {c["name"] for c in sa.inspect(bind).get_columns("group_session_progress")}
    if "completed_objective_indexes" in progress_columns:
        with op.batch_alter_table("group_session_progress") as batch_op:
            batch_op.drop_column("completed_objective_indexes")
    session_columns = {c["name"] for c in sa.inspect(bind).get_columns("teaching_sessions")}
    if "learning_objectives" in session_columns:
        with op.batch_alter_table("teaching_sessions") as batch_op:
            batch_op.drop_column("learning_objectives")
