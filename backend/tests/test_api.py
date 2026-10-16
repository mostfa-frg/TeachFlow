from dataclasses import replace
import asyncio
import json

import httpx
import pytest
from pydantic import ValidationError

from app.api.v1 import router as api_router
from app.core.config import Settings
from app.schemas import RoadmapProposal
from app.services import (
    InvalidRoadmap,
    OpenAICompatibleRoadmapGenerator,
    validate_roadmap,
)


class StubGenerator:
    def __init__(self, proposal: dict | None = None, error: Exception | None = None):
        self.proposal = proposal
        self.error = error
        self.context = None

    async def generate(self, context):
        self.context = context
        if self.error:
            raise self.error
        return RoadmapProposal.model_validate(self.proposal)


def sample_proposal(material_id: str | None = None) -> dict:
    return {
        "topics": [
            {
                "id": "foundations",
                "title": "Foundations",
                "description": "Build core knowledge.",
                "learning_objectives": ["Explain the key concepts"],
                "support_note": None,
            },
            {
                "id": "practice",
                "title": "Applied practice",
                "description": "Apply the course concepts.",
                "learning_objectives": ["Complete a practical exercise"],
                "support_note": "Includes a suggested extension.",
            },
        ],
        "sessions": [
            {
                "id": "foundation-session",
                "topic_id": "foundations",
                "sequence_index": 1,
                "title": "Core ideas",
                "description": "Discuss and practice core ideas.",
                "duration_minutes": 90,
                "supporting_material_ids": [material_id] if material_id else [],
            },
            {
                "id": "foundation-practice",
                "topic_id": "foundations",
                "sequence_index": 2,
                "title": "Practice the core ideas",
                "description": "Reinforce the foundations with examples.",
                "duration_minutes": 45,
                "supporting_material_ids": [],
            },
            {
                "id": "practice-session",
                "topic_id": "practice",
                "sequence_index": 1,
                "title": "Guided practice",
                "description": "Practice in a small project.",
                "duration_minutes": 120,
                "supporting_material_ids": [],
            },
        ],
        "dependencies": [
            {
                "prerequisite_topic_id": "foundations",
                "dependent_topic_id": "practice",
            }
        ],
        "warnings": ["Confirm that the course duration suits the group schedule."],
    }


def create_course(client, name="Python Development") -> dict:
    response = client.post(
        "/api/v1/courses",
        json={"name": name, "description": "An instructor-led Python course."},
    )
    assert response.status_code == 201, response.text
    return response.json()


def use_generator(monkeypatch, generator: StubGenerator) -> None:
    monkeypatch.setattr(api_router, "roadmap_generator", generator)


def test_health_readiness_and_validation(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/health/ready").json()["database"] == "connected"
    response = client.post("/api/v1/courses", json={"description": "Missing name"})
    assert response.status_code == 422
    assert response.json()["error"]["message"] == "Request validation failed."
    assert client.get("/").status_code == 200
    assert "TeachFlow" in client.get("/").text


def test_course_and_group_persistence(client):
    course = create_course(client)
    response = client.post(
        f"/api/v1/courses/{course['id']}/groups",
        json={
            "name": "Saturday",
            "schedule_description": "Saturdays at 10:00",
            "session_duration_minutes": 90,
        },
    )
    assert response.status_code == 201
    assert response.json()["course_id"] == course["id"]
    assert client.get(f"/api/v1/courses/{course['id']}").json()["groups"][0]["name"] == "Saturday"
    assert client.post(
        f"/api/v1/courses/{course['id']}/groups", json={"name": "Saturday"}
    ).status_code == 409


def test_material_text_ingestion_success_and_status(client, monkeypatch, tmp_path):
    monkeypatch.setattr(api_router, "settings", replace(api_router.settings, data_dir=tmp_path))
    course = create_course(client)
    response = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("outline.txt", b"Functions and reusable code.", "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "processed"
    assert response.json()["filename"] == "outline.txt"
    assert list((tmp_path / "materials").glob("*.txt"))


def test_pdf_material_extraction(client, monkeypatch, tmp_path):
    monkeypatch.setattr(api_router, "settings", replace(api_router.settings, data_dir=tmp_path))
    course = create_course(client)
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length 53 >>\nstream\nBT /F1 12 Tf 50 700 Td (TeachFlow PDF extraction) Tj ET\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(body + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010} 00000 n \n".encode())
    pdf.extend(
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )
    response = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("lesson.pdf", bytes(pdf), "application/pdf")},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "processed"
    text_file = next((tmp_path / "materials").glob("*.txt"))
    assert "TeachFlow PDF extraction" in text_file.read_text(encoding="utf-8")


def test_material_unsupported_empty_and_oversized(client, monkeypatch, tmp_path):
    monkeypatch.setattr(api_router, "settings", replace(api_router.settings, data_dir=tmp_path))
    course = create_course(client)
    unsupported = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("slides.pptx", b"not supported", "application/octet-stream")},
    )
    assert unsupported.json()["status"] == "unsupported"
    empty = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert empty.json()["status"] == "empty"
    monkeypatch.setattr(
        api_router,
        "settings",
        replace(api_router.settings, max_upload_bytes=3),
    )
    oversized = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("large.txt", b"1234", "text/plain")},
    )
    assert oversized.status_code == 413
    assert len(client.get(f"/api/v1/courses/{course['id']}/materials").json()) == 2


def test_invalid_text_and_invalid_pdf_are_recorded_as_failed(client, monkeypatch, tmp_path):
    monkeypatch.setattr(api_router, "settings", replace(api_router.settings, data_dir=tmp_path))
    course = create_course(client)
    invalid_text = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("bad.txt", b"\xff", "text/plain")},
    )
    invalid_pdf = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("bad.pdf", b"not a pdf", "application/pdf")},
    )
    corrupt_pdf = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("corrupt.pdf", b"%PDF-1.4\ncorrupt content", "application/pdf")},
    )
    assert invalid_text.json()["status"] == "failed"
    assert invalid_pdf.json()["status"] == "failed"
    assert corrupt_pdf.json()["status"] == "failed"
    assert "could not be read" in corrupt_pdf.json()["error_message"]


def test_generator_unavailable_is_explicit_and_creates_nothing(client, monkeypatch):
    course = create_course(client)
    use_generator(
        monkeypatch,
        OpenAICompatibleRoadmapGenerator(Settings(llm_api_key=None, llm_model="")),
    )
    response = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate")
    assert response.status_code == 503
    assert "LLM_API_KEY" in response.json()["error"]["message"]


@pytest.mark.parametrize(
    ("upstream_status", "expected_guidance"),
    [
        (400, "API style"),
        (401, "LLM_API_KEY"),
        (403, "access this model"),
        (404, "base URL and model name"),
        (429, "quota, billing"),
    ],
)
def test_provider_http_errors_explain_safe_next_steps(
    client, monkeypatch, upstream_status, expected_guidance
):
    course = create_course(client)
    request = httpx.Request("POST", "https://provider.invalid/v1/responses")
    response = httpx.Response(
        upstream_status,
        text="private provider detail that must not be exposed",
        request=request,
    )
    use_generator(
        monkeypatch,
        StubGenerator(error=httpx.HTTPStatusError("provider error", request=request, response=response)),
    )

    result = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate")

    assert result.status_code == 502
    message = result.json()["error"]["message"]
    assert f"HTTP {upstream_status}" in message
    assert expected_guidance in message
    assert "private provider detail" not in message


@pytest.mark.parametrize(
    ("api_style", "endpoint"),
    [("responses", "/responses"), ("chat_completions", "/chat/completions")],
)
def test_generator_supports_openai_api_styles(monkeypatch, api_style, endpoint):
    captured = {}
    proposal_json = json.dumps(sample_proposal())

    class MockAsyncClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, url, **kwargs):
            captured["url"] = url
            captured["payload"] = kwargs["json"]
            body = (
                {"output_text": proposal_json}
                if api_style == "responses"
                else {"choices": [{"message": {"content": proposal_json}}]}
            )
            return httpx.Response(
                200, json=body, request=httpx.Request("POST", url)
            )

    monkeypatch.setattr("app.services.httpx.AsyncClient", MockAsyncClient)
    generator = OpenAICompatibleRoadmapGenerator(
        Settings(
            llm_api_key="test-key",
            llm_model="gpt-oss-20b",
            llm_api_style=api_style,
        )
    )
    result = asyncio.run(generator.generate({"course": {"name": "Example"}}))

    assert result.topics[0].id == "foundations"
    assert captured["url"] == f"https://api.groq.com/openai/v1{endpoint}"
    prompt = (
        captured["payload"]["messages"][0]["content"]
        if api_style == "chat_completions"
        else captured["payload"]["input"][0]["content"]
    )
    assert "JSON Schema:" in prompt
    assert '"learning_objectives"' in prompt
    assert "without Markdown fences" in prompt


def test_schema_and_dependency_cycles_are_rejected():
    with pytest.raises(ValidationError):
        RoadmapProposal.model_validate({"topics": [], "sessions": []})
    proposal = sample_proposal()
    proposal["dependencies"].append(
        {"prerequisite_topic_id": "practice", "dependent_topic_id": "foundations"}
    )
    with pytest.raises(InvalidRoadmap, match="cycle"):
        validate_roadmap(RoadmapProposal.model_validate(proposal))


def test_invalid_generated_cycle_creates_no_draft_and_can_safely_retry(client, monkeypatch):
    course = create_course(client)
    invalid = sample_proposal()
    invalid["dependencies"].append(
        {"prerequisite_topic_id": "practice", "dependent_topic_id": "foundations"}
    )
    use_generator(monkeypatch, StubGenerator(invalid))
    headers = {"Idempotency-Key": "safe-provider-retry"}
    failed = client.post(
        f"/api/v1/courses/{course['id']}/roadmaps/generate", headers=headers
    )
    assert failed.status_code == 502
    use_generator(monkeypatch, StubGenerator(sample_proposal()))
    retried = client.post(
        f"/api/v1/courses/{course['id']}/roadmaps/generate", headers=headers
    )
    assert retried.status_code == 201
    assert retried.json()["version_number"] == 1


def test_generation_saves_versioned_draft_idempotently_and_approval(client, monkeypatch):
    course = create_course(client)
    use_generator(monkeypatch, StubGenerator(sample_proposal()))
    headers = {"Idempotency-Key": "first-roadmap-proposal"}
    first = client.post(
        f"/api/v1/courses/{course['id']}/roadmaps/generate", headers=headers
    )
    assert first.status_code == 201, first.text
    draft = first.json()
    assert draft["state"] == "draft"
    assert len(draft["topics"]) == 2
    assert len(draft["sessions"]) == 3
    assert draft["dependencies"] == [
        {
            "prerequisite_topic_id": "foundations",
            "dependent_topic_id": "practice",
        }
    ]
    repeated = client.post(
        f"/api/v1/courses/{course['id']}/roadmaps/generate", headers=headers
    )
    assert repeated.status_code == 201
    assert repeated.json()["id"] == draft["id"]
    edited = sample_proposal()
    edited["sessions"][0]["title"] = "Instructor-edited core ideas"
    update = client.put(f"/api/v1/roadmaps/{draft['id']}", json=edited)
    assert update.status_code == 200
    assert next(
        session for session in update.json()["sessions"]
        if session["stable_id"] == "foundation-session"
    )["title"] == "Instructor-edited core ideas"
    approved = client.post(f"/api/v1/roadmaps/{draft['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["state"] == "approved"
    assert client.put(f"/api/v1/roadmaps/{draft['id']}", json=sample_proposal()).status_code == 409


def test_approved_roadmap_can_be_loaded_by_course_id(client, monkeypatch):
    course = create_course(client)
    group = client.post(
        f"/api/v1/courses/{course['id']}/groups",
        json={"name": "Saturday Group", "schedule_description": "Saturday"},
    )
    assert group.status_code == 201

    use_generator(monkeypatch, StubGenerator(sample_proposal()))
    generated = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate")
    assert generated.status_code == 201, generated.text
    roadmap_id = generated.json()["id"]
    approved = client.post(f"/api/v1/roadmaps/{roadmap_id}/approve")
    assert approved.status_code == 200, approved.text

    response = client.get(f"/api/v1/courses/{course['id']}/roadmaps/approved")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == roadmap_id
    assert data["course_id"] == course["id"]
    assert data["state"] == "approved"
    assert len(data["sessions"]) == 3
    assert data["dependencies"] == [
        {
            "prerequisite_topic_id": "foundations",
            "dependent_topic_id": "practice",
        }
    ]

    no_roadmap = create_course(client, name="Course without roadmap")
    missing = client.get(f"/api/v1/courses/{no_roadmap['id']}/roadmaps/approved")
    assert missing.status_code == 404
    assert "No approved roadmap" in missing.json()["error"]["message"]

    missing_course = client.get("/api/v1/courses/not-a-course/roadmaps/approved")
    assert missing_course.status_code == 404
    assert missing_course.json()["error"]["message"] == "Course not found."


def test_generation_retries_invalid_proposal_with_validation_feedback(client, monkeypatch):
    course = create_course(client)
    incomplete = sample_proposal()
    incomplete["sessions"] = [
        session
        for session in incomplete["sessions"]
        if session["topic_id"] == "foundations"
    ]

    class CorrectingGenerator:
        def __init__(self):
            self.contexts = []

        async def generate(self, context):
            self.contexts.append(context.copy())
            proposal = incomplete if len(self.contexts) == 1 else sample_proposal()
            return RoadmapProposal.model_validate(proposal)

    generator = CorrectingGenerator()
    use_generator(monkeypatch, generator)

    response = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate")

    assert response.status_code == 201, response.text
    assert len(generator.contexts) == 2
    assert "validation_feedback" not in generator.contexts[0]
    assert generator.contexts[1]["validation_feedback"] == (
        "Every topic must contain at least one session."
    )


def test_generation_context_includes_only_extracted_document_text(client, monkeypatch, tmp_path):
    monkeypatch.setattr(api_router, "settings", replace(api_router.settings, data_dir=tmp_path))
    course = create_course(client)
    material = client.post(
        f"/api/v1/courses/{course['id']}/materials",
        files={"file": ("outline.txt", b"Evidence: functions and APIs.", "text/plain")},
    ).json()
    generator = StubGenerator(sample_proposal(material["id"]))
    use_generator(monkeypatch, generator)
    response = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate")
    assert response.status_code == 201, response.text
    assert generator.context["materials"] == [
        {
            "id": material["id"],
            "filename": "outline.txt",
            "text": "Evidence: functions and APIs.",
        }
    ]


def test_failed_generation_preserves_approved_roadmap(client, monkeypatch):
    course = create_course(client)
    use_generator(monkeypatch, StubGenerator(sample_proposal()))
    approved = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate").json()
    client.post(f"/api/v1/roadmaps/{approved['id']}/approve")
    use_generator(monkeypatch, StubGenerator(error=InvalidRoadmap("bad graph")))
    failed = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate")
    assert failed.status_code == 502
    assert client.get(f"/api/v1/roadmaps/{approved['id']}").json()["state"] == "approved"
    use_generator(monkeypatch, StubGenerator(sample_proposal()))
    replacement = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate").json()
    activated = client.post(f"/api/v1/roadmaps/{replacement['id']}/approve")
    assert activated.status_code == 200
    assert client.get(f"/api/v1/roadmaps/{approved['id']}").json()["state"] == "superseded"


def test_group_session_progress_is_isolated(client, monkeypatch):
    course = create_course(client)
    groups = [
        client.post(
            f"/api/v1/courses/{course['id']}/groups", json={"name": name}
        ).json()
        for name in ("Saturday", "Monday")
    ]
    use_generator(monkeypatch, StubGenerator(sample_proposal()))
    proposal = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate").json()
    client.post(f"/api/v1/roadmaps/{proposal['id']}/approve")
    session_id = proposal["sessions"][0]["id"]
    response = client.put(
        f"/api/v1/groups/{groups[0]['id']}/sessions/{session_id}/progress",
        json={"state": "completed"},
    )
    assert response.status_code == 200
    assert client.get(f"/api/v1/groups/{groups[0]['id']}/progress").json()[0]["state"] == "completed"
    assert client.get(f"/api/v1/groups/{groups[1]['id']}/progress").json() == []
    assert client.put(
        f"/api/v1/groups/{groups[1]['id']}/sessions/{session_id}/progress",
        json={"state": "completed"},
    ).status_code == 200


def test_session_goal_progress_derives_state_and_persists_indexes(client, monkeypatch):
    course = create_course(client)
    group = client.post(
        f"/api/v1/courses/{course['id']}/groups", json={"name": "Saturday"}
    ).json()
    proposal_input = sample_proposal()
    proposal_input["sessions"][0]["learning_objectives"] = [
        "Explain the concept",
        "Apply it in an example",
    ]
    use_generator(monkeypatch, StubGenerator(proposal_input))
    proposal = client.post(f"/api/v1/courses/{course['id']}/roadmaps/generate").json()
    assert client.post(f"/api/v1/roadmaps/{proposal['id']}/approve").status_code == 200
    session = proposal["sessions"][0]
    assert session["learning_objectives"] == [
        "Explain the concept",
        "Apply it in an example",
    ]
    url = f"/api/v1/groups/{group['id']}/sessions/{session['id']}/progress"
    partial = client.put(url, json={"completed_objective_indexes": [0]})
    assert partial.status_code == 200, partial.text
    assert partial.json()["state"] == "in_progress"
    assert partial.json()["completed_objective_indexes"] == [0]
    saved = client.get(f"/api/v1/groups/{group['id']}/progress").json()[0]
    assert saved["completed_objective_indexes"] == [0]
    complete = client.put(url, json={"completed_objective_indexes": [0, 1]})
    assert complete.status_code == 200, complete.text
    assert complete.json()["state"] == "completed"
    assert complete.json()["completed_objective_indexes"] == [0, 1]
    invalid = client.put(url, json={"completed_objective_indexes": [2]})
    assert invalid.status_code == 422
