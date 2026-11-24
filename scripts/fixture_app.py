"""Synthetic, explicitly marked replay app. Production startup never imports this module."""

import json
import os
from pathlib import Path

from app.api.v1.router import get_roadmap_generator
from app.main import app
from app.schemas import RoadmapProposal
from app.services import InvalidRoadmap

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def recorded(name):
    return json.loads(
        (EXAMPLES / "responses" / (name + ".json")).read_text(encoding="utf-8")
    )


class Replay:
    async def generate(self, context):
        data = recorded("roadmap")
        files = {m["filename"]: m["id"] for m in context["materials"]}
        for session in data["sessions"]:
            material = files.get(session.pop("source_filename"))
            session["supporting_material_ids"] = [material] if material else []
            session["supporting_chunk_ids"] = [
                c["id"] for c in context["chunks"] if c["material_id"] == material
            ][:1]
        return RoadmapProposal.model_validate(data)

    async def generate_structured(self, context, schema, instructions):
        if schema.__name__ == "Coverage":
            return schema.model_validate(recorded("review"))
        if schema.__name__ == "PackageDraft":
            return schema.model_validate(recorded("package"))
        if schema.__name__ == "Answer":
            answer = recorded("assistant")
            quote = answer["citations"][0]["quote"]
            source = next(
                (
                    s
                    for s in context["sources"]
                    if s["kind"] == "material" and quote in s["text"]
                ),
                None,
            )
            if not source:
                return schema(sufficient=False, citations=[])
            answer["citations"][0]["ref"] = source["ref"]
            return schema.model_validate(answer)
        raise InvalidRoadmap("Unknown fixture type.")


app.dependency_overrides[get_roadmap_generator] = Replay


@app.middleware("http")
async def label_replay(request, call_next):
    response = await call_next(request)
    response.headers["X-TeachFlow-Run"] = os.environ.get(
        "TEACHFLOW_REPLAY_RUN", "manual"
    )
    response.headers["X-TeachFlow-Demo"] = "recorded"
    return response
