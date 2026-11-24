"""Local transcript evidence, editable proposals and explicit approval transitions."""

from pathlib import Path
from typing import Literal

import httpx
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.router import get_roadmap_generator
from app.db import get_db
from app.models import (
    ApprovalEvent,
    FollowUp,
    InstructorGroup,
    SessionReview,
    TeachingSession,
)
from app.services import GeneratorNotConfigured, InvalidRoadmap
from app.workspace import group_session

router = APIRouter(prefix="/api/v1")


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(Strict):
    start: int = Field(ge=0)
    end: int = Field(gt=0)
    snippet: str = Field(min_length=1, max_length=2000)


class Finding(Strict):
    objective_index: int = Field(ge=0)
    status: Literal["covered", "partial", "not observed", "unclear"]
    confidence: float = Field(ge=0, le=1)
    evidence: list[Evidence] = Field(max_length=10)


class Coverage(Strict):
    findings: list[Finding] = Field(max_length=20)


class PackageDraft(Strict):
    summary: str = Field(min_length=1, max_length=5000)
    recap: str = Field(min_length=1, max_length=5000)
    homework: str = Field(min_length=1, max_length=5000)
    group_message: str = Field(min_length=1, max_length=5000)


class ItemEdit(Strict):
    text: str = Field(max_length=5000)
    approve: bool = False


def begin_edit(db):
    # Serialize decisions before reading the current JSON fields in SQLite.
    if db.bind.dialect.name == "sqlite":
        db.execute(text("BEGIN IMMEDIATE"))


def get_record(db, model, key):
    row = db.get(model, key)
    if not row:
        raise HTTPException(404, "Record not found.")
    return row


def objectives(session):
    return session.learning_objectives or session.topic.learning_objectives


def verify_findings(result, goals, transcript):
    if sorted(f.objective_index for f in result.findings) != list(range(len(goals))):
        raise ValueError("Include one finding per planned objective.")
    for f in result.findings:
        if not f.evidence and f.status in ("covered", "partial"):
            raise ValueError("Coverage requires a transcript excerpt.")
        for evidence in f.evidence:
            if (
                evidence.end > len(transcript)
                or transcript[evidence.start : evidence.end] != evidence.snippet
            ):
                raise ValueError(
                    "Evidence must match the transcript at the specified character offsets."
                )
    return [
        f.model_dump() for f in sorted(result.findings, key=lambda f: f.objective_index)
    ]


def review_json(row, db):
    session = db.get(TeachingSession, row.session_id)
    return dict(
        id=row.id,
        group_id=row.group_id,
        session_id=row.session_id,
        title=session.title,
        objectives=objectives(session),
        filename=row.filename,
        transcript=row.transcript,
        mode=row.mode,
        findings=row.findings,
        state=row.state,
    )


def package_json(row):
    return dict(
        id=row.id,
        review_id=row.review_id,
        mode=row.mode,
        state=row.state,
        items=row.items,
    )


def log_change(db, review, entity, item, state):
    course = db.get(InstructorGroup, review.group_id).course_id
    db.add(ApprovalEvent(course_id=course, entity_id=entity, item=item, state=state))


async def structured(generator, context, schema, instructions):
    try:
        answer = await generator.generate_structured(context, schema, instructions)
        return schema.model_validate(answer)
    except GeneratorNotConfigured:
        return None
    except (httpx.HTTPError, InvalidRoadmap, ValidationError) as exc:
        raise HTTPException(
            502, "Provider response unavailable or invalid. Retry the request."
        ) from exc


@router.post("/groups/{group_id}/sessions/{session_id}/reviews", status_code=201)
async def upload_review(
    group_id: str,
    session_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    generator=Depends(get_roadmap_generator),
):
    _, session = group_session(db, group_id, session_id)
    if Path(file.filename or "").suffix.lower() not in {".txt", ".md"}:
        raise HTTPException(415, "Choose a synthetic TXT or Markdown transcript.")
    data = await file.read(100_001)
    if len(data) > 100_000:
        raise HTTPException(413, "Transcript exceeds 100 KB.")
    try:
        transcript = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(422, "Use UTF-8 transcript text.") from exc
    if not transcript.strip():
        raise HTTPException(422, "The transcript is empty.")
    goals = objectives(session)
    generated = await structured(
        generator,
        dict(objectives=goals, transcript=transcript),
        Coverage,
        "Assess observed coverage per objective using exact excerpts with zero-based character offsets, end exclusive. Report uncertainty.",
    )
    result = generated or Coverage(
        findings=[
            Finding(objective_index=i, status="unclear", confidence=0, evidence=[])
            for i in range(len(goals))
        ]
    )
    try:
        findings = verify_findings(result, goals, transcript)
    except ValueError as exc:
        raise HTTPException(502, str(exc)) from exc
    row = SessionReview(
        group_id=group_id,
        session_id=session_id,
        filename=Path(file.filename).name[:255],
        transcript=transcript,
        findings=findings,
        mode="ai" if generated else "manual",
    )
    db.add(row)
    db.flush()
    log_change(db, row, row.id, "review", "draft")
    db.commit()
    return review_json(row, db)


@router.get("/reviews/{key}")
def get_review(key: str, db: Session = Depends(get_db)):
    return review_json(get_record(db, SessionReview, key), db)


@router.put("/reviews/{key}")
def update_review(key: str, payload: Coverage, db: Session = Depends(get_db)):
    begin_edit(db)
    row = get_record(db, SessionReview, key)
    if row.state != "draft":
        raise HTTPException(409, "This review is already approved.")
    try:
        row.findings = verify_findings(
            payload, objectives(db.get(TeachingSession, row.session_id)), row.transcript
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    log_change(db, row, key, "review", "edited")
    db.commit()
    return review_json(row, db)


@router.post("/reviews/{key}/approve")
def approve_review(key: str, db: Session = Depends(get_db)):
    begin_edit(db)
    row = get_record(db, SessionReview, key)
    if row.state == "draft":
        row.state = "approved"
        log_change(db, row, key, "review", "approved")
        db.commit()
    return review_json(row, db)


@router.post("/reviews/{key}/package")
async def create_package(
    key: str, db: Session = Depends(get_db), generator=Depends(get_roadmap_generator)
):
    row = get_record(db, SessionReview, key)
    if row.state != "approved":
        raise HTTPException(409, "Approve the review before drafting follow-up.")
    existing = db.scalar(select(FollowUp).filter_by(review_id=key))
    if existing:
        return package_json(existing)
    session = db.get(TeachingSession, row.session_id)
    generated = await structured(
        generator,
        dict(
            session=session.title, objectives=objectives(session), findings=row.findings
        ),
        PackageDraft,
        "Draft four instructor-editable items using the approved evidence. Do not claim unobserved topics were covered.",
    )
    values = (
        generated.model_dump()
        if generated
        else dict.fromkeys(PackageDraft.model_fields, "")
    )
    package = FollowUp(
        review_id=key,
        mode="ai" if generated else "manual",
        items={k: dict(text=v, state="draft") for k, v in values.items()},
    )
    db.add(package)
    try:
        db.flush()
        log_change(db, row, package.id, "package", "draft")
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(select(FollowUp).filter_by(review_id=key))
        if not existing:
            raise
        return package_json(existing)
    return package_json(package)


@router.get("/packages/{key}")
def get_package(key: str, db: Session = Depends(get_db)):
    return package_json(get_record(db, FollowUp, key))


@router.put("/packages/{key}/items/{item}")
def edit_item(key: str, item: str, request: ItemEdit, db: Session = Depends(get_db)):
    begin_edit(db)
    row = get_record(db, FollowUp, key)
    if item not in row.items:
        raise HTTPException(404, "Unknown package item.")
    if row.items[item]["state"] == "approved":
        if request.approve and request.text == row.items[item]["text"]:
            return package_json(row)
        raise HTTPException(409, "This item is already approved.")
    if request.approve and not request.text.strip():
        raise HTTPException(422, "Enter a draft before approving it.")
    review = db.get(SessionReview, row.review_id)
    state = "approved" if request.approve else "draft"
    row.items = {**row.items, item: dict(text=request.text, state=state)}
    log_change(db, review, key, item, "approved" if request.approve else "edited")
    if all(v["state"] == "approved" for v in row.items.values()):
        row.state = "approved"
        log_change(db, review, key, "package", "approved")
    db.commit()
    return package_json(row)


@router.get("/groups/{group_id}/sessions/{session_id}/reviews")
def session_reviews(group_id: str, session_id: str, db: Session = Depends(get_db)):
    group_session(db, group_id, session_id)
    rows = db.scalars(
        select(SessionReview)
        .filter_by(group_id=group_id, session_id=session_id)
        .order_by(SessionReview.created_at.desc())
    )
    return [dict(id=r.id, state=r.state, filename=r.filename) for r in rows]


@router.get("/courses/{course_id}/history")
def history(course_id: str, db: Session = Depends(get_db)):
    rows = db.scalars(
        select(ApprovalEvent)
        .filter_by(course_id=course_id)
        .order_by(ApprovalEvent.timestamp)
    )
    return [
        dict(id=r.entity_id, item=r.item, state=r.state, timestamp=r.timestamp)
        for r in rows
    ]
