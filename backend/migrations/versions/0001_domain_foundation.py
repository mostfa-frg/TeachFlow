"""Create initial TeachFlow instructor domain tables.

Revision ID: 0001_domain
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_domain"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("learner_level", sa.String(30)),
        sa.Column("learning_goals", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "instructor_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("schedule_description", sa.String(500)),
        sa.Column("session_duration_minutes", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("course_id", "name"),
        sa.CheckConstraint(
            "session_duration_minutes IS NULL OR session_duration_minutes > 0",
            name="ck_group_duration_positive",
        ),
    )
    op.create_index("ix_instructor_groups_course_id", "instructor_groups", ["course_id"])
    op.create_table(
        "materials",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("media_type", sa.String(120)),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("storage_name", sa.String(80), nullable=False, unique=True),
        sa.Column("extracted_name", sa.String(80), unique=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("error_message", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("size_bytes >= 0", name="ck_material_size_nonnegative"),
        sa.CheckConstraint(
            "status IN ('processed', 'partial', 'empty', 'unsupported', 'failed')",
            name="ck_material_status",
        ),
    )
    op.create_index("ix_materials_course_id", "materials", ["course_id"])
    op.create_index("ix_materials_course_status", "materials", ["course_id", "status"])
    op.create_table(
        "roadmap_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("idempotency_key", sa.String(120)),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("course_id", "version_number"),
        sa.UniqueConstraint("course_id", "idempotency_key"),
        sa.CheckConstraint(
            "state IN ('draft', 'approved', 'superseded')",
            name="ck_roadmap_version_state",
        ),
    )
    op.create_index("ix_roadmap_versions_course_id", "roadmap_versions", ["course_id"])
    op.create_index("ix_roadmap_versions_course_state", "roadmap_versions", ["course_id", "state"])
    op.create_index(
        "uq_roadmap_approved_course",
        "roadmap_versions",
        ["course_id"],
        unique=True,
        sqlite_where=sa.text("state = 'approved'"),
        postgresql_where=sa.text("state = 'approved'"),
    )
    op.create_table(
        "topics",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("roadmap_version_id", sa.String(36), sa.ForeignKey("roadmap_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stable_id", sa.String(80), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("learning_objectives", sa.JSON(), nullable=False),
        sa.Column("support_note", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("roadmap_version_id", "stable_id"),
    )
    op.create_index("ix_topics_roadmap_version_id", "topics", ["roadmap_version_id"])
    op.create_table(
        "teaching_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("roadmap_version_id", sa.String(36), sa.ForeignKey("roadmap_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("topic_id", sa.String(36), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stable_id", sa.String(80), nullable=False),
        sa.Column("sequence_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("supporting_material_ids", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("roadmap_version_id", "stable_id"),
        sa.UniqueConstraint("topic_id", "sequence_index"),
        sa.CheckConstraint("duration_minutes > 0", name="ck_session_duration_positive"),
        sa.CheckConstraint("sequence_index > 0", name="ck_session_sequence_positive"),
    )
    op.create_index("ix_teaching_sessions_roadmap_version_id", "teaching_sessions", ["roadmap_version_id"])
    op.create_index("ix_teaching_sessions_topic_id", "teaching_sessions", ["topic_id"])
    op.create_table(
        "topic_dependencies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("roadmap_version_id", sa.String(36), sa.ForeignKey("roadmap_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prerequisite_topic_id", sa.String(36), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("dependent_topic_id", sa.String(36), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("roadmap_version_id", "prerequisite_topic_id", "dependent_topic_id"),
        sa.CheckConstraint(
            "prerequisite_topic_id != dependent_topic_id",
            name="ck_topic_dependency_not_self",
        ),
    )
    op.create_index("ix_topic_dependencies_roadmap_version_id", "topic_dependencies", ["roadmap_version_id"])
    op.create_index("ix_topic_dependencies_dependent", "topic_dependencies", ["dependent_topic_id"])
    op.create_table(
        "group_session_progress",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("instructor_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("teaching_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("state", sa.String(20), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("group_id", "session_id"),
        sa.CheckConstraint(
            "state IN ('upcoming', 'in_progress', 'completed')",
            name="ck_group_progress_state",
        ),
    )
    op.create_index("ix_group_session_progress_group_id", "group_session_progress", ["group_id"])
    op.create_index("ix_group_session_progress_session_id", "group_session_progress", ["session_id"])
    op.create_index("ix_group_progress_group_state", "group_session_progress", ["group_id", "state"])


def downgrade() -> None:
    op.drop_table("group_session_progress")
    op.drop_table("topic_dependencies")
    op.drop_table("teaching_sessions")
    op.drop_table("topics")
    op.drop_table("roadmap_versions")
    op.drop_table("materials")
    op.drop_table("instructor_groups")
    op.drop_table("courses")
