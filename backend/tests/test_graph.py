import pytest
from app.api.v1 import router
from app.db import engine
from sqlalchemy import text
from test_api import StubGenerator, create_course, sample_proposal


def proposal():
    data = sample_proposal()
    a, b, c = [s["id"] for s in data["sessions"]]
    data["sessions"][0]["topic_ids"] = ["foundations", "practice"]
    data["session_edges"] = [
        dict(from_session_id=a, to_session_id=b, edge_type="prerequisite", note=None),
        dict(from_session_id=a, to_session_id=c, edge_type="depends_on", note=None),
        dict(
            from_session_id=b, to_session_id=c, edge_type="reinforces", note="Exercise"
        ),
    ]
    return data


def setup_graph(client, monkeypatch):
    data = proposal()
    monkeypatch.setattr(router, "roadmap_generator", StubGenerator(data))
    course = create_course(client)["id"]
    response = client.post(f"/api/v1/courses/{course}/roadmaps/generate")
    assert response.status_code == 201, response.text
    return course, data, response.json()["id"]


def test_graph_across_edit_approval_reload_copy_and_diff(client, monkeypatch):
    course, data, version = setup_graph(client, monkeypatch)
    root = "/api/v1/roadmaps/"
    assert client.post(root + version + "/approve").is_success
    copied = client.post(
        f"/api/v1/courses/{course}/roadmaps/draft-from-approved"
    ).json()["id"]
    data["session_edges"][2]["note"] = "New exercise"
    data["sessions"].reverse()
    assert client.put(root + copied, json=data).is_success
    assert client.post(root + copied + "/approve").is_success
    saved = client.get(f"/api/v1/courses/{course}/roadmaps/approved").json()
    assert sorted(saved["session_edges"], key=str) == sorted(
        data["session_edges"], key=str
    )
    assert [s["stable_id"] for s in saved["sessions"]] == [
        s["id"] for s in data["sessions"]
    ]
    assert saved["sessions"][-1]["topic_ids"] == ["foundations", "practice"]
    diff = client.get(root + version + "/diff/" + copied).json()
    assert diff["links"]["changed"][0]["after"]["note"] == "New exercise"
    assert len(client.get(f"/api/v1/courses/{course}/roadmaps").json()) == 2


@pytest.mark.parametrize(
    "case", ["cycle", "dangling", "self", "duplicate", "membership", "id", "sequence"]
)
def test_rejected_edits_are_atomic(client, monkeypatch, case):
    _, data, version = setup_graph(client, monkeypatch)
    first = data["session_edges"][0]
    if case == "cycle":
        data["session_edges"].append(
            dict(
                first,
                from_session_id=first["to_session_id"],
                to_session_id=first["from_session_id"],
            )
        )
    elif case == "dangling":
        first["from_session_id"] = "missing"
    elif case == "self":
        first["from_session_id"] = first["to_session_id"]
    elif case == "duplicate":
        data["session_edges"].append(first)
    elif case == "membership":
        data["sessions"][0]["topic_ids"].append("missing")
    elif case == "sequence":
        data["sessions"][1]["sequence_index"] = 1
    else:
        data["sessions"][0]["id"] = "contains spaces"
    url = "/api/v1/roadmaps/" + version
    assert client.put(url, json=data).status_code == 422
    assert len(client.get(url).json()["session_edges"]) == 3


def test_foreign_keys_enabled():
    with engine.connect() as connection:
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1


def test_generation_race_returns_winner_or_retryable_conflict(client, monkeypatch):
    course, _, version = setup_graph(client, monkeypatch)
    from app.graph import write_graph
    from app.models import RoadmapVersion
    from sqlalchemy.exc import IntegrityError

    def losing_write(db, roadmap, proposal):
        key = roadmap.idempotency_key
        db.rollback()
        if key == "shared":
            db.get(RoadmapVersion, version).idempotency_key = key
            db.commit()
        raise IntegrityError("concurrent insert", {}, Exception("unique key"))

    monkeypatch.setattr(router, "write_graph", losing_write)
    url = f"/api/v1/courses/{course}/roadmaps/generate"
    assert (
        client.post(url, headers={"Idempotency-Key": "shared"}).json()["id"] == version
    )
    assert client.post(url, headers={"Idempotency-Key": "other"}).status_code == 409
    monkeypatch.setattr(router, "write_graph", write_graph)
    assert (
        client.post(url, headers={"Idempotency-Key": "other"}).json()["id"] != version
    )


def test_cross_version_diff_reports_new_and_removed_links(client, monkeypatch):
    course, data, original = setup_graph(client, monkeypatch)
    client.post(f"/api/v1/roadmaps/{original}/approve").raise_for_status()
    copy = client.post(f"/api/v1/courses/{course}/roadmaps/draft-from-approved").json()[
        "id"
    ]
    removed = data["session_edges"].pop()
    added = dict(
        removed,
        from_session_id=removed["to_session_id"],
        to_session_id=removed["from_session_id"],
    )
    data["session_edges"].append(added)
    data["sessions"][0]["title"] = "New title"
    client.put("/api/v1/roadmaps/" + copy, json=data).raise_for_status()
    diff = client.get(f"/api/v1/roadmaps/{original}/diff/{copy}").json()
    assert diff["links"]["added"] == [added] and diff["links"]["removed"] == [removed]
    assert diff["sessions"]["changed"][0]["after"]["title"] == "New title"


def test_overlapping_generations_share_one_key(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db import Base, get_db
    from app.main import app
    from app.schemas import RoadmapProposal

    db_engine = create_engine("sqlite:///" + str(tmp_path / "overlap.db"))
    Base.metadata.create_all(db_engine)
    sessions = sessionmaker(db_engine, expire_on_commit=False)
    barrier = Barrier(2, timeout=10)

    def connection():
        with sessions() as session:
            yield session

    class ConcurrentFixture:
        async def generate(self, context):
            barrier.wait()
            return RoadmapProposal.model_validate(proposal())

    monkeypatch.setitem(app.dependency_overrides, get_db, connection)
    monkeypatch.setattr(router, "roadmap_generator", ConcurrentFixture())
    try:
        with TestClient(app) as api:
            course = create_course(api)["id"]
            root = f"/api/v1/courses/{course}/roadmaps"

            def create(_):
                return api.post(
                    root + "/generate", headers={"Idempotency-Key": "replayed"}
                )

            with ThreadPoolExecutor(max_workers=2) as pool:
                first, second = pool.map(create, range(2))
            assert first.status_code == second.status_code == 201
            assert first.json()["id"] == second.json()["id"]
            assert len(api.get(root).json()) == 1
    finally:
        db_engine.dispose()
