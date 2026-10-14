from typing import Protocol

from app.schemas import RoadmapPreviewRequest


class RoadmapGenerator(Protocol):
    """Provider-independent interface for a real, schema-validated AI generator."""

    async def generate(self, request: RoadmapPreviewRequest) -> dict:
        """Return a proposed roadmap; never apply it directly to active course data."""
        ...


class GeneratorNotConfigured(RuntimeError):
    pass


class UnconfiguredRoadmapGenerator:
    """Explicit placeholder used until a model provider and evaluation are selected."""

    async def generate(self, request: RoadmapPreviewRequest) -> dict:
        raise GeneratorNotConfigured(
            "Roadmap generation is not configured yet. The request was validated, "
            "but no AI provider has been called and no roadmap was created."
        )
