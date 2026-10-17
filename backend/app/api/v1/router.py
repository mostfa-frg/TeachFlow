"""Versioned API endpoints for courses, materials, roadmaps, and progress."""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import anyio
import httpx
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.db import get_db
from app.models import (
    Course,
    GroupSessionProgress,
    InstructorGroup,
    Material,
    RoadmapVersion,
    TeachingSession,
    Topic,
    TopicDependency,
)
from app.schemas import (
    CourseCreate,
    CourseOut,
    DependencyOut,
    GroupCreate,
    GroupOut,
    MaterialOut,
    ProgressOut,
    ProgressUpdate,
    RoadmapProposal,
    RoadmapVersionOut,
    SessionOut,
    TopicOut,
)
from app.services import (
    GeneratorNotConfigured,
    InvalidRoadmap,
    MaterialExtractionError,
    OpenAICompatibleRoadmapGenerator,
    RoadmapGenerator,
    extract_document,
    validate_roadmap,
)

logger = logging.getLogger("teachflow")
router = APIRouter()
roadmap_generator: RoadmapGenerator = OpenAICompatibleRoadmapGenerator()
ALLOWED_TYPES = {
    ".pdf": {"application/pdf", "application/octet-stream"},
    ".txt": {"text/plain", "application/octet-stream"},
    ".md": {"text/markdown", "text/plain", "application/octet-stream"},
}
MAX_EXTRACTED_CHARS = 20_000
MAX_CONTEXT_CHARS = 100_000
MAX_CONTEXT_MATERIALS = 30


def get_roadmap_generator() -> RoadmapGenerator:
    """Dependency seam for provider configuration and deterministic tests."""
    return roadmap_generator


@router.get("/health", tags=["operations"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "teachflow-api"}


@router.get("/health/ready", tags=["operations"])
def readiness(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "connected"}


@router.post("/api/v1/courses", response_model=CourseOut, status_code=201, tags=["courses"])
def create_course(request: CourseCreate, db: Session = Depends(get_db)) -> Course:
    course = Course(**request.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/api/v1/courses", response_model=list[CourseOut], tags=["courses"])
def list_courses(db: Session = Depends(get_db)) -> list[Course]:
    return list(db.scalars(select(Course).options(selectinload(Course.groups))).all())


@router.get("/api/v1/courses/{course_id}", response_model=CourseOut, tags=["courses"])
def get_course(course_id: str, db: Session = Depends(get_db)) -> Course:
    course = db.scalar(
        select(Course)
        .where(Course.id == course_id)
        .options(selectinload(Course.groups))
    )
    if not course:
        raise HTTPException(404, "Course not found.")
    return course


@router.put("/api/v1/courses/{course_id}", response_model=CourseOut, tags=["courses"])
def update_course(
    course_id: str, request: CourseCreate, db: Session = Depends(get_db)
) -> Course:
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found.")
    for key, value in request.model_dump().items():
        setattr(course, key, value)
    db.commit()
    return get_course(course_id, db)


@router.post(
    "/api/v1/courses/{course_id}/groups",
    response_model=GroupOut,
    status_code=201,
    tags=["groups"],
)
def create_group(
    course_id: str, request: GroupCreate, db: Session = Depends(get_db)
) -> InstructorGroup:
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    group = InstructorGroup(course_id=course_id, **request.model_dump())
    db.add(group)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "A group with this name already exists in the course.") from exc
    db.refresh(group)
    return group


@router.get(
    "/api/v1/courses/{course_id}/groups",
    response_model=list[GroupOut],
    tags=["groups"],
)
def list_groups(course_id: str, db: Session = Depends(get_db)) -> list[InstructorGroup]:
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    return list(
        db.scalars(
            select(InstructorGroup)
            .where(InstructorGroup.course_id == course_id)
            .order_by(InstructorGroup.created_at)
        ).all()
    )


@router.put(
    "/api/v1/courses/{course_id}/groups/{group_id}",
    response_model=GroupOut,
    tags=["groups"],
)
def update_group(
    course_id: str,
    group_id: str,
    request: GroupCreate,
    db: Session = Depends(get_db),
) -> InstructorGroup:
    group = db.get(InstructorGroup, group_id)
    if not group or group.course_id != course_id:
        raise HTTPException(404, "Group not found for this course.")
    for key, value in request.model_dump().items():
        setattr(group, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(409, "A group with this name already exists in the course.") from exc
    db.refresh(group)
    return group


def _clean_filename(filename: str | None) -> str:
    name = Path((filename or "unnamed").replace("\\", "/")).name
    return re.sub(r"[\x00-\x1f\x7f]", "", name)[:255] or "unnamed"


def _has_pdf_signature(path: Path) -> bool:
    with path.open("rb") as stream:
        return stream.read(5) == b"%PDF-"


@router.post(
    "/api/v1/courses/{course_id}/materials",
    response_model=MaterialOut,
    status_code=201,
    tags=["materials"],
)
def upload_material(
    course_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Material:
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    filename = _clean_filename(file.filename)
    extension = Path(filename).suffix.lower()
    media_type = file.content_type
    storage_root = settings.data_dir / "materials"
    storage_root.mkdir(parents=True, exist_ok=True)
    ident = str(uuid4())
    storage_name = f"{ident}{extension if extension in ALLOWED_TYPES else '.bin'}"
    destination = storage_root / storage_name
    size = 0
    try:
        with destination.open("wb") as output:
            while chunk := file.file.read(64 * 1024):
                size += len(chunk)
                if size > settings.max_upload_bytes:
                    raise HTTPException(
                        status.HTTP_413_CONTENT_TOO_LARGE,
                        f"File exceeds the {settings.max_upload_bytes}-byte upload limit.",
                    )
                output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        file.file.close()

    content_type_ok = extension in ALLOWED_TYPES and (
        not media_type or media_type in ALLOWED_TYPES[extension]
    )
    extracted_name: str | None = None
    error_message: str | None = None
    if not content_type_ok:
        destination.unlink(missing_ok=True)
        storage_name = f"rejected-{ident}"
        processing_state = "unsupported"
        error_message = "Supported formats are PDF, TXT, and Markdown."
    elif size == 0:
        destination.unlink(missing_ok=True)
        processing_state = "empty"
        error_message = "The uploaded file is empty."
    elif extension == ".pdf" and _has_pdf_signature(destination) is False:
        destination.unlink(missing_ok=True)
        storage_name = f"rejected-{ident}"
        processing_state = "failed"
        error_message = "The uploaded file is not a valid PDF."
    else:
        try:
            extracted, partial = extract_document(destination, extension)
            if not extracted.strip():
                processing_state = "empty"
                error_message = "No extractable text was found in the document."
                destination.unlink(missing_ok=True)
            else:
                extracted_name = f"{ident}.txt"
                extracted_path = storage_root / extracted_name
                extracted_path.write_text(extracted, encoding="utf-8")
                processing_state = "partial" if partial else "processed"
                if partial:
                    error_message = "PDF extraction was partial; some pages may be missing."
        except (MaterialExtractionError, OSError, ValueError) as exc:
            destination.unlink(missing_ok=True)
            storage_name = f"rejected-{ident}"
            processing_state = "failed"
            error_message = str(exc)[:500]
        except Exception:
            logger.exception("Unexpected document extraction failure (material_id=%s)", ident)
            destination.unlink(missing_ok=True)
            storage_name = f"rejected-{ident}"
            processing_state = "failed"
            error_message = "Document extraction failed unexpectedly."

    material = Material(
        id=ident,
        course_id=course_id,
        filename=filename,
        media_type=media_type,
        size_bytes=size,
        storage_name=storage_name,
        extracted_name=extracted_name,
        status=processing_state,
        error_message=error_message,
    )
    db.add(material)
    try:
        db.commit()
    except Exception:
        db.rollback()
        destination.unlink(missing_ok=True)
        if extracted_name:
            (storage_root / extracted_name).unlink(missing_ok=True)
        raise
    db.refresh(material)
    return material


@router.delete(
    "/api/v1/courses/{course_id}/materials/{material_id}",
    status_code=204,
    tags=["materials"],
)
def delete_material(
    course_id: str, material_id: str, db: Session = Depends(get_db)
) -> None:
    material = db.get(Material, material_id)
    if not material or material.course_id != course_id:
        raise HTTPException(404, "Material not found for this course.")
    material_dir = settings.data_dir / "materials"
    stored_names = (material.storage_name, material.extracted_name)
    db.delete(material)
    db.commit()
    for storage_name in stored_names:
        if storage_name and Path(storage_name).name == storage_name:
            try:
                (material_dir / storage_name).unlink(missing_ok=True)
            except OSError as exc:
                logger.exception("Material file cleanup failed after metadata deletion")
                raise HTTPException(
                    500,
                    "Material metadata was removed, but stored-file cleanup failed.",
                ) from exc


@router.get(
    "/api/v1/courses/{course_id}/materials",
    response_model=list[MaterialOut],
    tags=["materials"],
)
def list_materials(course_id: str, db: Session = Depends(get_db)) -> list[Material]:
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    return list(
        db.scalars(
            select(Material)
            .where(Material.course_id == course_id)
            .order_by(Material.created_at)
        ).all()
    )


def _roadmap_response(version: RoadmapVersion) -> RoadmapVersionOut:
    topics = sorted(version.topics, key=lambda item: item.created_at)
    topic_order = {topic.id: position for position, topic in enumerate(topics)}
    sessions = sorted(
        version.sessions,
        key=lambda item: (topic_order[item.topic_id], item.sequence_index),
    )
    by_internal_id = {topic.id: topic.stable_id for topic in topics}
    return RoadmapVersionOut(
        id=version.id,
        course_id=version.course_id,
        version_number=version.version_number,
        state=version.state,
        warnings=version.warnings,
        approved_at=version.approved_at,
        topics=[TopicOut.model_validate(topic) for topic in topics],
        sessions=[SessionOut.model_validate(session) for session in sessions],
        dependencies=[
            DependencyOut(
                prerequisite_topic_id=by_internal_id[edge.prerequisite_topic_id],
                dependent_topic_id=by_internal_id[edge.dependent_topic_id],
            )
            for edge in version.dependencies
        ],
    )


def _get_roadmap(db: Session, roadmap_id: str) -> RoadmapVersion:
    roadmap = db.scalar(
        select(RoadmapVersion)
        .where(RoadmapVersion.id == roadmap_id)
        .options(
            selectinload(RoadmapVersion.topics),
            selectinload(RoadmapVersion.sessions),
            selectinload(RoadmapVersion.dependencies),
        )
    )
    if not roadmap:
        raise HTTPException(404, "Roadmap version not found.")
    return roadmap


@router.post(
    "/api/v1/courses/{course_id}/roadmaps/generate",
    response_model=RoadmapVersionOut,
    status_code=201,
    tags=["roadmaps"],
)
def generate_roadmap(
    course_id: str,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    generator: RoadmapGenerator = Depends(get_roadmap_generator),
) -> RoadmapVersionOut:
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(404, "Course not found.")
    if idempotency_key:
        if len(idempotency_key) > 120:
            raise HTTPException(400, "Idempotency-Key cannot exceed 120 characters.")
        existing = db.scalar(
            select(RoadmapVersion).where(
                RoadmapVersion.course_id == course_id,
                RoadmapVersion.idempotency_key == idempotency_key,
            )
        )
        if existing:
            return _roadmap_response(_get_roadmap(db, existing.id))
    material_records = list(
        db.scalars(
            select(Material).where(
                Material.course_id == course_id,
                Material.status.in_(("processed", "partial")),
                Material.extracted_name.is_not(None),
            )
            .order_by(Material.created_at.desc())
            .limit(MAX_CONTEXT_MATERIALS + 1)
        ).all()
    )
    material_context = []
    material_dir = settings.data_dir / "materials"
    context_chars = 0
    for material in material_records[:MAX_CONTEXT_MATERIALS]:
        assert material.extracted_name is not None
        extracted_path = material_dir / material.extracted_name
        if extracted_path.exists() and context_chars < MAX_CONTEXT_CHARS:
            text_limit = min(
                MAX_EXTRACTED_CHARS, MAX_CONTEXT_CHARS - context_chars
            )
            with extracted_path.open(encoding="utf-8") as source:
                text = source.read(text_limit)
            context_chars += len(text)
            material_context.append(
                {
                    "id": material.id,
                    "filename": material.filename,
                    "text": text,
                }
            )
    groups = list(
        db.scalars(select(InstructorGroup).where(InstructorGroup.course_id == course_id)).all()
    )
    context: dict[str, object] = {
        "course": {
            "name": course.name,
            "description": course.description,
            "learner_level": course.learner_level,
            "learning_goals": course.learning_goals,
        },
        "groups": [
            {
                "name": group.name,
                "schedule_description": group.schedule_description,
                "session_duration_minutes": group.session_duration_minutes,
            }
            for group in groups
        ],
        "materials": material_context,
        "instructions": (
            "Ground topics in supplied material. Mark inferred topics. Use material "
            "ids only from the supplied materials. Topic dependencies form a DAG."
        ),
    }
    try:
        known_material_ids = {material["id"] for material in material_context}
        proposal: RoadmapProposal | None = None
        for attempt in range(2):
            try:
                candidate = anyio.run(generator.generate, context)
                validate_roadmap(candidate, known_material_ids)
            except InvalidRoadmap as exc:
                if attempt == 1:
                    raise
                logger.info(
                    "Retrying invalid roadmap proposal with validation feedback: %s",
                    exc,
                )
                context["validation_feedback"] = str(exc)
            else:
                proposal = candidate
                break
        if proposal is None:
            raise InvalidRoadmap(
                "The model response could not be validated after one correction attempt."
            )
        required_warnings = []
        if not material_context:
            required_warnings.append(
                "No extracted teaching materials were available; verify coverage manually."
            )
        if not groups:
            required_warnings.append(
                "No instructor groups were provided; confirm session timing after setup."
            )
        if any(material.status == "partial" for material in material_records):
            required_warnings.append(
                "At least one material was only partially extracted; confirm omitted pages."
            )
        if len(material_records) > MAX_CONTEXT_MATERIALS:
            required_warnings.append(
                f"Only the {MAX_CONTEXT_MATERIALS} most recently processed materials were included."
            )
        proposal.warnings = (proposal.warnings + required_warnings)[:30]
    except GeneratorNotConfigured as exc:
        raise HTTPException(503, str(exc)) from exc
    except InvalidRoadmap as exc:
        raise HTTPException(502, f"Roadmap proposal was rejected: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        upstream_status = exc.response.status_code
        guidance = {
            400: (
                "check the model name, API style, and structured-output support"
            ),
            401: "check that LLM_API_KEY is a valid key for the configured provider",
            403: "check that the API key and project can access this model",
            404: "check the provider base URL and model name",
            429: "check provider quota, billing, and rate limits",
        }.get(upstream_status, "check the provider status and configuration")
        logger.warning(
            "Roadmap provider rejected the request: upstream_status=%s",
            upstream_status,
        )
        raise HTTPException(
            502,
            f"AI provider returned HTTP {upstream_status}; {guidance}. "
            "Provider response details were omitted.",
        ) from exc
    except httpx.HTTPError as exc:
        logger.warning("Roadmap provider request failed: %s", type(exc).__name__)
        raise HTTPException(
            502,
            "The configured AI provider could not be reached. Check LLM_BASE_URL "
            "and network connectivity.",
        ) from exc

    previous = db.scalar(
        select(RoadmapVersion.version_number)
        .where(RoadmapVersion.course_id == course_id)
        .order_by(RoadmapVersion.version_number.desc())
    )
    roadmap = RoadmapVersion(
        course_id=course_id,
        version_number=(previous or 0) + 1,
        state="draft",
        warnings=proposal.warnings,
        idempotency_key=idempotency_key,
    )
    topic_by_stable_id = {
        item.id: Topic(
            stable_id=item.id,
            title=item.title,
            description=item.description,
            learning_objectives=item.learning_objectives,
            support_note=item.support_note,
        )
        for item in proposal.topics
    }
    roadmap.topics.extend(topic_by_stable_id.values())
    db.add(roadmap)
    db.flush()
    for item in proposal.sessions:
        roadmap.sessions.append(
            TeachingSession(
                topic=topic_by_stable_id[item.topic_id],
                stable_id=item.id,
                sequence_index=item.sequence_index,
                title=item.title,
                description=item.description,
                learning_objectives=(item.learning_objectives or next(t for t in proposal.topics if t.id == item.topic_id).learning_objectives),
                duration_minutes=item.duration_minutes,
                supporting_material_ids=item.supporting_material_ids,
            )
        )
    for edge in proposal.dependencies:
        roadmap.dependencies.append(
            TopicDependency(
                prerequisite_topic_id=topic_by_stable_id[
                    edge.prerequisite_topic_id
                ].id,
                dependent_topic_id=topic_by_stable_id[edge.dependent_topic_id].id,
            )
        )
    db.commit()
    return _roadmap_response(_get_roadmap(db, roadmap.id))


@router.get(
    "/api/v1/courses/{course_id}/roadmaps/approved",
    response_model=RoadmapVersionOut,
    tags=["roadmaps"],
)
def get_approved_course_roadmap(
    course_id: str, db: Session = Depends(get_db)
) -> RoadmapVersionOut:
    """Return the active approved roadmap for a course, if one exists."""
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    roadmap = db.scalar(
        select(RoadmapVersion)
        .where(
            RoadmapVersion.course_id == course_id,
            RoadmapVersion.state == "approved",
        )
        .order_by(RoadmapVersion.version_number.desc())
    )
    if not roadmap:
        raise HTTPException(404, "No approved roadmap exists for this course.")
    return _roadmap_response(_get_roadmap(db, roadmap.id))


@router.post(
    "/api/v1/courses/{course_id}/roadmaps/draft-from-approved",
    response_model=RoadmapVersionOut,
    status_code=201,
    tags=["roadmaps"],
)
def create_draft_from_approved(course_id: str, db: Session = Depends(get_db)) -> RoadmapVersionOut:
    """Create an editable draft copied from the current approved roadmap."""
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    source = db.scalar(
        select(RoadmapVersion).where(RoadmapVersion.course_id == course_id, RoadmapVersion.state == "approved")
        .order_by(RoadmapVersion.version_number.desc())
        .options(selectinload(RoadmapVersion.topics), selectinload(RoadmapVersion.sessions), selectinload(RoadmapVersion.dependencies))
    )
    if not source:
        raise HTTPException(404, "No approved roadmap exists for this course.")
    latest = db.scalar(select(RoadmapVersion.version_number).where(RoadmapVersion.course_id == course_id).order_by(RoadmapVersion.version_number.desc()).limit(1)) or source.version_number
    draft = RoadmapVersion(course_id=course_id, version_number=latest + 1, state="draft", warnings=list(source.warnings or []))
    db.add(draft)
    db.flush()
    topic_map = {}
    for old in source.topics:
        new_topic = Topic(roadmap_version_id=draft.id, stable_id=old.stable_id, title=old.title, description=old.description, learning_objectives=list(old.learning_objectives or []), support_note=old.support_note)
        db.add(new_topic)
        topic_map[old.id] = new_topic
    db.flush()
    for old in source.sessions:
        db.add(TeachingSession(roadmap_version_id=draft.id, topic_id=topic_map[old.topic_id].id, stable_id=old.stable_id, sequence_index=old.sequence_index, title=old.title, description=old.description, learning_objectives=list(old.learning_objectives or []), duration_minutes=old.duration_minutes, supporting_material_ids=list(old.supporting_material_ids or [])))
    for edge in source.dependencies:
        db.add(TopicDependency(roadmap_version_id=draft.id, prerequisite_topic_id=topic_map[edge.prerequisite_topic_id].id, dependent_topic_id=topic_map[edge.dependent_topic_id].id))
    db.commit()
    return _roadmap_response(_get_roadmap(db, draft.id))


@router.get(
    "/api/v1/roadmaps/{roadmap_id}",
    response_model=RoadmapVersionOut,
    tags=["roadmaps"],
)
def get_roadmap(roadmap_id: str, db: Session = Depends(get_db)) -> RoadmapVersionOut:
    return _roadmap_response(_get_roadmap(db, roadmap_id))


@router.put(
    "/api/v1/roadmaps/{roadmap_id}",
    response_model=RoadmapVersionOut,
    tags=["roadmaps"],
)
def edit_roadmap(
    roadmap_id: str, proposal: RoadmapProposal, db: Session = Depends(get_db)
) -> RoadmapVersionOut:
    roadmap = _get_roadmap(db, roadmap_id)
    if roadmap.state != "draft":
        raise HTTPException(409, "Only draft roadmaps can be edited.")
    course_material_ids = set(
        db.scalars(
            select(Material.id).where(
                Material.course_id == roadmap.course_id,
                Material.status.in_(("processed", "partial")),
            )
        ).all()
    )
    try:
        validate_roadmap(proposal, course_material_ids)
    except InvalidRoadmap as exc:
        raise HTTPException(422, str(exc)) from exc
    db.query(TopicDependency).filter_by(roadmap_version_id=roadmap.id).delete()
    db.query(TeachingSession).filter_by(roadmap_version_id=roadmap.id).delete()
    db.query(Topic).filter_by(roadmap_version_id=roadmap.id).delete()
    topic_by_id = {
        item.id: Topic(
            roadmap_version_id=roadmap.id,
            stable_id=item.id,
            title=item.title,
            description=item.description,
            learning_objectives=item.learning_objectives,
            support_note=item.support_note,
        )
        for item in proposal.topics
    }
    db.add_all(topic_by_id.values())
    db.flush()
    for item in proposal.sessions:
        db.add(
            TeachingSession(
                roadmap_version_id=roadmap.id,
                topic_id=topic_by_id[item.topic_id].id,
                stable_id=item.id,
                sequence_index=item.sequence_index,
                title=item.title,
                description=item.description,
                learning_objectives=(item.learning_objectives or next(t for t in proposal.topics if t.id == item.topic_id).learning_objectives),
                duration_minutes=item.duration_minutes,
                supporting_material_ids=item.supporting_material_ids,
            )
        )
    for edge in proposal.dependencies:
        db.add(
            TopicDependency(
                roadmap_version_id=roadmap.id,
                prerequisite_topic_id=topic_by_id[edge.prerequisite_topic_id].id,
                dependent_topic_id=topic_by_id[edge.dependent_topic_id].id,
            )
        )
    roadmap.warnings = proposal.warnings
    db.commit()
    db.expire_all()
    return _roadmap_response(_get_roadmap(db, roadmap.id))


@router.post(
    "/api/v1/roadmaps/{roadmap_id}/approve",
    response_model=RoadmapVersionOut,
    tags=["roadmaps"],
)
def approve_roadmap(roadmap_id: str, db: Session = Depends(get_db)) -> RoadmapVersionOut:
    roadmap = _get_roadmap(db, roadmap_id)
    if roadmap.state != "draft":
        raise HTTPException(409, "Only draft roadmaps can be approved.")
    db.scalar(
        select(Course)
        .where(Course.id == roadmap.course_id)
        .with_for_update()
    )
    approved = db.scalars(
        select(RoadmapVersion)
        .where(
            RoadmapVersion.course_id == roadmap.course_id,
            RoadmapVersion.state == "approved",
        )
        .with_for_update()
        .options(
            selectinload(RoadmapVersion.sessions).selectinload(TeachingSession.topic),
        )
    ).all()

    # Keep group progress attached to unchanged sessions when a new roadmap
    # version is approved. Stable IDs are the cross-version identity contract.
    new_sessions = {session.stable_id: session for session in roadmap.sessions}
    for previous in approved:
        for old_session in previous.sessions:
            new_session = new_sessions.get(old_session.stable_id)
            if new_session is None:
                continue
            rows = db.scalars(
                select(GroupSessionProgress).where(
                    GroupSessionProgress.session_id == old_session.id
                )
            ).all()
            old_goals = old_session.learning_objectives or old_session.topic.learning_objectives or []
            new_goals = new_session.learning_objectives or new_session.topic.learning_objectives or []
            for progress in rows:
                # Preserve objective indexes only when the goal list is exactly
                # unchanged. If goals changed, keep the session identity but
                # require the instructor to review progress for the new goals.
                if old_goals != new_goals:
                    progress.completed_objective_indexes = []
                    progress.state = "upcoming"
                    progress.completed_at = None
                progress.session_id = new_session.id
        previous.state = "superseded"
    db.flush()
    roadmap.state = "approved"
    roadmap.approved_at = datetime.now(timezone.utc)
    db.commit()
    return _roadmap_response(_get_roadmap(db, roadmap.id))


@router.put(
    "/api/v1/groups/{group_id}/sessions/{session_id}/progress",
    response_model=ProgressOut,
    tags=["progress"],
)
def update_group_progress(
    group_id: str,
    session_id: str,
    request: ProgressUpdate,
    db: Session = Depends(get_db),
) -> GroupSessionProgress:
    group = db.get(InstructorGroup, group_id)
    session = db.get(TeachingSession, session_id)
    roadmap = db.get(RoadmapVersion, session.roadmap_version_id) if session else None
    if not group or not session or not roadmap or group.course_id != roadmap.course_id:
        raise HTTPException(404, "Group or session not found for this course.")
    if roadmap.state != "approved":
        raise HTTPException(409, "Progress can only be recorded for an approved roadmap.")
    objectives = session.learning_objectives or session.topic.learning_objectives or []
    indexes = request.completed_objective_indexes
    if indexes is None and request.state is None:
        raise HTTPException(422, "Provide a state or completed objective indexes.")
    if indexes is not None:
        if any(index >= len(objectives) for index in indexes):
            raise HTTPException(422, "A completed objective index is outside this session's goals.")
        state_value = "upcoming" if not indexes else ("completed" if len(indexes) == len(objectives) else "in_progress")
    else:
        state_value = request.state
    progress = db.scalar(
        select(GroupSessionProgress).where(
            GroupSessionProgress.group_id == group_id,
            GroupSessionProgress.session_id == session_id,
        )
    )
    if progress is None:
        progress = GroupSessionProgress(
            group_id=group_id, session_id=session_id, state=state_value
        )
        db.add(progress)
    if indexes is not None:
        progress.completed_objective_indexes = indexes
    elif state_value == "completed":
        progress.completed_objective_indexes = list(range(len(objectives)))
    elif state_value == "upcoming":
        progress.completed_objective_indexes = []
    progress.state = state_value
    progress.completed_at = datetime.now(timezone.utc) if state_value == "completed" else None
    db.commit()
    db.refresh(progress)
    return progress


@router.get(
    "/api/v1/groups/{group_id}/progress",
    response_model=list[ProgressOut],
    tags=["progress"],
)
def list_group_progress(
    group_id: str, db: Session = Depends(get_db)
) -> list[GroupSessionProgress]:
    if not db.get(InstructorGroup, group_id):
        raise HTTPException(404, "Group not found.")
    active_session_ids = select(TeachingSession.id).join(
        RoadmapVersion, TeachingSession.roadmap_version_id == RoadmapVersion.id
    ).where(RoadmapVersion.state == "approved")
    return list(
        db.scalars(
            select(GroupSessionProgress)
            .where(
                GroupSessionProgress.group_id == group_id,
                GroupSessionProgress.session_id.in_(active_session_ids),
            )
            .order_by(GroupSessionProgress.created_at)
        ).all()
    )
