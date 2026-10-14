from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class MaterialReference(BaseModel):
    """Metadata only; uploaded file bytes and extracted text are not accepted here yet."""

    filename: str = Field(min_length=1, max_length=255)
    content_type: str | None = None
    source_id: str | None = None


class GroupInput(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    schedule_description: str | None = Field(default=None, max_length=500)
    session_duration_minutes: int | None = Field(default=None, ge=1, le=720)


class RoadmapPreviewRequest(BaseModel):
    course_name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    learner_level: Literal["beginner", "intermediate", "advanced", "mixed"] | None = None
    learning_goals: list[str] = Field(default_factory=list, max_length=30)
    groups: list[GroupInput] = Field(default_factory=list, max_length=30)
    materials: list[MaterialReference] = Field(default_factory=list, max_length=100)


class RoadmapGenerationStatus(BaseModel):
    status: Literal["not_configured", "draft"]
    message: str
    approval_required: bool = True


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
