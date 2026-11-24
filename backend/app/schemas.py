"""Validated API and roadmap-generation contracts."""

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=4000)
    learner_level: Literal["beginner", "intermediate", "advanced", "mixed"] | None = None
    learning_goals: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Course name must not be blank.")
        return value


Weekday = Literal["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    weekday: Weekday | None = None
    start_time: str | None = Field(default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    start_date: date | None = None
    schedule_description: str | None = Field(default=None, max_length=500)
    session_duration_minutes: int | None = Field(default=None, ge=1, le=720)

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Group name must not be blank.")
        return value


class GroupOut(ORMModel):
    id: str
    course_id: str
    name: str
    weekday: Weekday | None = None
    start_time: str | None = Field(default=None, pattern=r"^(?:[01][0-9]|2[0-3]):[0-5][0-9]$")
    start_date: date | None = None
    schedule_description: str | None
    session_duration_minutes: int | None


class CourseOut(ORMModel):
    id: str
    name: str
    description: str | None
    learner_level: str | None
    learning_goals: list[str]
    groups: list[GroupOut] = Field(default_factory=list)


class ChunkRef(ORMModel):
    id: str
    locator: str


class MaterialOut(ORMModel):
    chunks: list[ChunkRef] = Field(default_factory=list)
    id: str
    course_id: str
    filename: str
    media_type: str | None
    size_bytes: int
    status: Literal["processed", "partial", "empty", "unsupported", "failed"]
    error_message: str | None
    created_at: datetime


StableId = Annotated[str, Field(pattern=r"^[A-Za-z0-9_-]{1,80}$")]
EdgeType = Literal["prerequisite", "depends_on", "reinforces", "extends", "introduces", "applies"]


class SessionEdgeProposal(BaseModel):
    from_session_id: StableId
    to_session_id: StableId
    edge_type: EdgeType
    note: str | None = Field(default=None, max_length=500)


class TopicProposal(BaseModel):
    id: StableId
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=4000)
    learning_objectives: list[str] = Field(min_length=1, max_length=20)
    support_note: str | None = Field(default=None, max_length=500)


class SessionProposal(BaseModel):
    id: StableId
    topic_ids: list[StableId] = Field(default_factory=list, max_length=100)
    topic_id: StableId
    sequence_index: int = Field(ge=1, le=500)
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=4000)
    duration_minutes: int = Field(ge=1, le=720)
    learning_objectives: list[str] = Field(default_factory=list, max_length=20)
    supporting_chunk_ids: list[str] = Field(default_factory=list, max_length=50)
    supporting_material_ids: list[str] = Field(default_factory=list, max_length=50)


class DependencyProposal(BaseModel):
    prerequisite_topic_id: StableId
    dependent_topic_id: StableId


class RoadmapProposal(BaseModel):
    topics: list[TopicProposal] = Field(min_length=1, max_length=100)
    sessions: list[SessionProposal] = Field(min_length=1, max_length=200)
    session_edges: list[SessionEdgeProposal] | None = Field(default=None, max_length=1200)
    dependencies: list[DependencyProposal] = Field(default_factory=list, max_length=300)
    warnings: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("topics")
    @classmethod
    def unique_topic_ids(cls, topics: list[TopicProposal]) -> list[TopicProposal]:
        ids = [topic.id for topic in topics]
        if len(ids) != len(set(ids)):
            raise ValueError("Topic identifiers must be unique.")
        return topics

    @field_validator("sessions")
    @classmethod
    def unique_session_ids(cls, sessions: list[SessionProposal]) -> list[SessionProposal]:
        ids = [session.id for session in sessions]
        if len(ids) != len(set(ids)):
            raise ValueError("Session identifiers must be unique.")
        return sessions


class SessionOut(ORMModel):
    id: str
    stable_id: str
    topic_ids: list[str]
    sort_order: int
    topic_id: str
    sequence_index: int
    title: str
    description: str
    learning_objectives: list[str]
    duration_minutes: int
    supporting_chunk_ids: list[str] = Field(default_factory=list, max_length=50)
    supporting_material_ids: list[str]


class TopicOut(ORMModel):
    sort_order: int
    id: str
    stable_id: str
    title: str
    description: str
    learning_objectives: list[str]
    support_note: str | None


class DependencyOut(ORMModel):
    prerequisite_topic_id: str
    dependent_topic_id: str


class RoadmapVersionOut(ORMModel):
    id: str
    course_id: str
    version_number: int
    state: Literal["draft", "approved", "superseded"]
    warnings: list[str]
    approved_at: datetime | None
    topics: list[TopicOut]
    sessions: list[SessionOut]
    session_edges: list[SessionEdgeProposal]
    dependencies: list[DependencyOut]


class ProgressUpdate(BaseModel):
    state: Literal["upcoming", "in_progress", "completed"] | None = None
    completed_objective_indexes: list[int] | None = Field(default=None, max_length=20)

    @field_validator("completed_objective_indexes")
    @classmethod
    def unique_nonnegative_indexes(cls, indexes: list[int] | None) -> list[int] | None:
        if indexes is None:
            return None
        if any(index < 0 for index in indexes) or len(indexes) != len(set(indexes)):
            raise ValueError("Objective indexes must be unique and nonnegative.")
        return sorted(indexes)


class ProgressOut(ORMModel):
    id: str
    group_id: str
    session_id: str
    state: str
    completed_objective_indexes: list[int]
    completed_at: datetime | None
