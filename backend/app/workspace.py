"""Instructor dashboard facts scoped to the selected course and cohort."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.graph import HARD_EDGES
from app.ingestion import DAYS
from app.models import Benchmark, Course, GroupSessionProgress, InstructorGroup, RoadmapVersion, TeachingSession

router = APIRouter(prefix="/api/v1")


class BenchmarkEdit(BaseModel):
    target_date: date | None


def group_session(db, group_id, session_id):
    group = db.get(InstructorGroup, group_id)
    session = db.get(TeachingSession, session_id)
    if not group or not session or session.roadmap_version.course_id != group.course_id:
        raise HTTPException(404, "Session not found for this group.")
    if session.roadmap_version.state != "approved":
        raise HTTPException(409, "Choose a session in the current approved plan.")
    return group, session


@router.put("/groups/{group_id}/sessions/{session_id}/benchmark")
def save_benchmark(group_id: str, session_id: str, request: BenchmarkEdit, db: Session = Depends(get_db)):
    _, session = group_session(db, group_id, session_id)
    row = db.get(Benchmark, (group_id, session.stable_id))
    if request.target_date:
        db.merge(Benchmark(group_id=group_id, stable_id=session.stable_id, target_date=request.target_date))
    elif row:
        db.delete(row)
    db.commit()
    return request


def group_overview(db, group_id, today=None):
    group = db.get(InstructorGroup, group_id)
    if not group:
        raise HTTPException(404, "Group not found.")
    plan = db.scalar(select(RoadmapVersion).filter_by(course_id=group.course_id, state="approved"))
    if not plan:
        return {"sessions": [], "reminders": []}
    today = today or date.today()
    progress = {row.session_id: row for row in db.scalars(select(GroupSessionProgress).filter_by(group_id=group_id))}
    targets = {row.stable_id: row.target_date for row in db.scalars(select(Benchmark).filter_by(group_id=group_id))}
    start = group.start_date
    if start and group.weekday:
        start += timedelta(days=(DAYS.index(group.weekday)-start.weekday()) % 7)
    by_id = {s.id: s for s in plan.sessions}
    sessions, reminders = [], []
    for s in sorted(plan.sessions, key=lambda item: item.sort_order):
        row = progress.get(s.id)
        state = row.state if row else "upcoming"
        scheduled = None
        if start and group.weekday and (group.schedule_description != "One-time event" or s.sort_order == 0):
            scheduled = start + timedelta(weeks=s.sort_order)
        target = targets.get(s.stable_id, scheduled)
        status = "unscheduled"
        if target:
            assessed = row.completed_at.date() if row and row.completed_at else today
            status = "behind" if assessed > target else "on track"
            if state == "completed" and assessed < target:
                status = "ahead"
        sessions.append(dict(session_id=s.id, stable_id=s.stable_id,title=s.title, state=state,
                             target_date=target, scheduled=scheduled, status=status))
        if state == "completed" or (not scheduled and not target and state != "in_progress"):
            continue
        for e in plan.session_edges:
            if e.to_session_id != s.id or e.edge_type not in HARD_EDGES:
                continue
            prior = progress.get(e.from_session_id)
            if not prior or prior.state != "completed":
                missing = by_id[e.from_session_id]
                reminder = dict(session=s.title, session_id=s.stable_id, missing=missing.title, missing_id=missing.stable_id)
                if reminder not in reminders:
                    reminders.append(reminder)
    return dict(sessions=sessions, reminders=reminders)


@router.get("/groups/{group_id}/overview")
def overview(group_id: str, db: Session = Depends(get_db)):
    return group_overview(db, group_id)


@router.get("/courses/{course_id}/approvals")
def approvals(course_id: str, db: Session = Depends(get_db)):
    if not db.get(Course, course_id):
        raise HTTPException(404, "Course not found.")
    drafts = db.scalars(select(RoadmapVersion).filter_by(course_id=course_id,state="draft").order_by(RoadmapVersion.version_number.desc()))
    return [dict(kind="roadmap", id=row.id, title=f"Roadmap version {row.version_number}") for row in drafts]
