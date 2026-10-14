"""Relational domain model; progress belongs to a group, plans belong to a course."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db import Base


def new_id() -> str:
    return str(uuid4())


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=now_utc, onupdate=now_utc, nullable=False
    )


class Course(TimestampMixin, Base):
    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    learner_level: Mapped[str | None] = mapped_column(String(30))
    learning_goals: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    groups: Mapped[list["InstructorGroup"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    materials: Mapped[list["Material"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    roadmap_versions: Mapped[list["RoadmapVersion"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )


class InstructorGroup(TimestampMixin, Base):
    __tablename__ = "instructor_groups"
    __table_args__ = (
        UniqueConstraint("course_id", "name"),
        CheckConstraint(
            "session_duration_minutes IS NULL OR session_duration_minutes > 0",
            name="ck_group_duration_positive",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    schedule_description: Mapped[str | None] = mapped_column(String(500))
    session_duration_minutes: Mapped[int | None] = mapped_column(Integer)
    course: Mapped[Course] = relationship(back_populates="groups")
    progress: Mapped[list["GroupSessionProgress"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class Material(TimestampMixin, Base):
    __tablename__ = "materials"
    __table_args__ = (
        Index("ix_materials_course_status", "course_id", "status"),
        CheckConstraint("size_bytes >= 0", name="ck_material_size_nonnegative"),
        CheckConstraint(
            "status IN ('processed', 'partial', 'empty', 'unsupported', 'failed')",
            name="ck_material_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str | None] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    extracted_name: Mapped[str | None] = mapped_column(String(80), unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    error_message: Mapped[str | None] = mapped_column(String(500))
    course: Mapped[Course] = relationship(back_populates="materials")


class RoadmapVersion(TimestampMixin, Base):
    __tablename__ = "roadmap_versions"
    __table_args__ = (
        UniqueConstraint("course_id", "version_number"),
        UniqueConstraint("course_id", "idempotency_key"),
        Index("ix_roadmap_versions_course_state", "course_id", "state"),
        CheckConstraint(
            "state IN ('draft', 'approved', 'superseded')",
            name="ck_roadmap_version_state",
        ),
        Index(
            "uq_roadmap_approved_course",
            "course_id",
            unique=True,
            sqlite_where=text("state = 'approved'"),
            postgresql_where=text("state = 'approved'"),
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    course_id: Mapped[str] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    idempotency_key: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    warnings: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    course: Mapped[Course] = relationship(back_populates="roadmap_versions")
    topics: Mapped[list["Topic"]] = relationship(
        back_populates="roadmap_version", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["TeachingSession"]] = relationship(
        back_populates="roadmap_version", cascade="all, delete-orphan"
    )
    dependencies: Mapped[list["TopicDependency"]] = relationship(
        back_populates="roadmap_version", cascade="all, delete-orphan"
    )


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"
    __table_args__ = (UniqueConstraint("roadmap_version_id", "stable_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    roadmap_version_id: Mapped[str] = mapped_column(
        ForeignKey("roadmap_versions.id", ondelete="CASCADE"), index=True
    )
    stable_id: Mapped[str] = mapped_column(String(80), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objectives: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    support_note: Mapped[str | None] = mapped_column(String(500))
    roadmap_version: Mapped[RoadmapVersion] = relationship(back_populates="topics")
    sessions: Mapped[list["TeachingSession"]] = relationship(
        back_populates="topic", cascade="all, delete-orphan"
    )


class TeachingSession(TimestampMixin, Base):
    __tablename__ = "teaching_sessions"
    __table_args__ = (
        UniqueConstraint("roadmap_version_id", "stable_id"),
        UniqueConstraint("topic_id", "sequence_index"),
        CheckConstraint("duration_minutes > 0", name="ck_session_duration_positive"),
        CheckConstraint("sequence_index > 0", name="ck_session_sequence_positive"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    roadmap_version_id: Mapped[str] = mapped_column(
        ForeignKey("roadmap_versions.id", ondelete="CASCADE"), index=True
    )
    topic_id: Mapped[str] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), index=True
    )
    stable_id: Mapped[str] = mapped_column(String(80), nullable=False)
    sequence_index: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    supporting_material_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    roadmap_version: Mapped[RoadmapVersion] = relationship(back_populates="sessions")
    topic: Mapped[Topic] = relationship(back_populates="sessions")
    progress: Mapped[list["GroupSessionProgress"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class TopicDependency(Base):
    __tablename__ = "topic_dependencies"
    __table_args__ = (
        UniqueConstraint(
            "roadmap_version_id", "prerequisite_topic_id", "dependent_topic_id"
        ),
        Index("ix_topic_dependencies_dependent", "dependent_topic_id"),
        CheckConstraint(
            "prerequisite_topic_id != dependent_topic_id",
            name="ck_topic_dependency_not_self",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    roadmap_version_id: Mapped[str] = mapped_column(
        ForeignKey("roadmap_versions.id", ondelete="CASCADE"), index=True
    )
    prerequisite_topic_id: Mapped[str] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE")
    )
    dependent_topic_id: Mapped[str] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE")
    )
    roadmap_version: Mapped[RoadmapVersion] = relationship(back_populates="dependencies")


class GroupSessionProgress(TimestampMixin, Base):
    __tablename__ = "group_session_progress"
    __table_args__ = (
        UniqueConstraint("group_id", "session_id"),
        Index("ix_group_progress_group_state", "group_id", "state"),
        CheckConstraint(
            "state IN ('upcoming', 'in_progress', 'completed')",
            name="ck_group_progress_state",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    group_id: Mapped[str] = mapped_column(
        ForeignKey("instructor_groups.id", ondelete="CASCADE"), index=True
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("teaching_sessions.id", ondelete="CASCADE"), index=True
    )
    state: Mapped[str] = mapped_column(String(20), nullable=False, default="upcoming")
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    group: Mapped[InstructorGroup] = relationship(back_populates="progress")
    session: Mapped[TeachingSession] = relationship(back_populates="progress")
