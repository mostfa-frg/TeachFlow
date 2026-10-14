from fastapi import FastAPI, HTTPException, status

from app.schemas import HealthResponse, RoadmapGenerationStatus, RoadmapPreviewRequest
from app.services import GeneratorNotConfigured, UnconfiguredRoadmapGenerator

app = FastAPI(
    title="TeachFlow API",
    description=(
        "Instructor-only course planning API. AI-generated plans remain proposals "
        "until an instructor explicitly approves them."
    ),
    version="0.1.0",
)

roadmap_generator = UnconfiguredRoadmapGenerator()


@app.get("/health", response_model=HealthResponse, tags=["operations"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="teachflow-api")


@app.post(
    "/api/v1/roadmaps/preview",
    response_model=RoadmapGenerationStatus,
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    tags=["roadmaps"],
)
async def preview_roadmap(
    request: RoadmapPreviewRequest,
) -> RoadmapGenerationStatus:
    """Validate setup input; returns 503 until a real generator is configured."""
    try:
        await roadmap_generator.generate(request)
    except GeneratorNotConfigured as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    # A configured generator must be integrated with a strict output schema before
    # this endpoint can return a successful preview.
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="The configured generator has no validated response adapter yet.",
    )
