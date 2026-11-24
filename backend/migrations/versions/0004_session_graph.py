"""Preserve the recoverable session graph and its order."""

from alembic import op
import sqlalchemy as sa

revision = "0004_session_graph"
down_revision = "0003_session_goal_progress"
branch_labels = None
depends_on = None


def ref(name, target):
    return sa.Column(
        name,
        sa.String(36),
        sa.ForeignKey(target + ".id", ondelete="CASCADE"),
        primary_key=True,
    )


def upgrade():
    for table in ("topics", "teaching_sessions"):
        op.add_column(
            table,
            sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        )
    op.create_table(
        "session_topics",
        ref("session_id", "teaching_sessions"),
        ref("topic_id", "topics"),
    )
    op.create_table(
        "session_edges",
        ref("roadmap_version_id", "roadmap_versions"),
        ref("from_session_id", "teaching_sessions"),
        ref("to_session_id", "teaching_sessions"),
        sa.Column("edge_type", sa.String(32), primary_key=True),
        sa.Column("note", sa.String(500)),
        sa.CheckConstraint("from_session_id != to_session_id", name="ck_edge_not_self"),
    )
    op.execute("""WITH ranked AS (SELECT id, row_number() OVER
               (PARTITION BY roadmap_version_id ORDER BY created_at,id)-1 AS n FROM topics)
               UPDATE topics SET sort_order=(SELECT n FROM ranked WHERE ranked.id=topics.id)""")
    op.execute("""WITH ranked AS (SELECT s.id, row_number() OVER
               (PARTITION BY s.roadmap_version_id ORDER BY t.sort_order,s.sequence_index,s.id)-1 AS n
               FROM teaching_sessions s JOIN topics t ON t.id=s.topic_id)
               UPDATE teaching_sessions SET sort_order=(SELECT n FROM ranked WHERE ranked.id=teaching_sessions.id)""")
    op.execute("INSERT INTO session_topics SELECT id,topic_id FROM teaching_sessions")
    op.execute("""INSERT INTO session_edges
               SELECT roadmap_version_id,prev,id,'prerequisite',NULL FROM
               (SELECT *,lag(id) OVER (PARTITION BY topic_id ORDER BY sequence_index) AS prev FROM teaching_sessions)
               WHERE prev IS NOT NULL""")
    op.execute("""INSERT INTO session_edges SELECT roadmap_version_id,a,b,'prerequisite',NULL FROM
               (SELECT d.roadmap_version_id,
               (SELECT id FROM teaching_sessions WHERE topic_id=d.prerequisite_topic_id ORDER BY sequence_index DESC LIMIT 1) AS a,
               (SELECT id FROM teaching_sessions WHERE topic_id=d.dependent_topic_id ORDER BY sequence_index LIMIT 1) AS b
               FROM topic_dependencies d) WHERE a IS NOT NULL AND b IS NOT NULL""")


def downgrade():
    raise RuntimeError(
        "Removing stored session relationships requires explicit owner approval."
    )
