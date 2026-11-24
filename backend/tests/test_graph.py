import pytest
from sqlalchemy import text

from app.api.v1 import router
from app.db import engine
from test_api import StubGenerator, create_course, sample_proposal


def proposal():
    data = sample_proposal()
    a, b, c = [s["id"] for s in data["sessions"]]
    data["sessions"][0]["topic_ids"] = ["foundations", "practice"]
    data["session_edges"] = [
        dict(from_session_id=a, to_session_id=b, edge_type="prerequisite", note=None),
        dict(from_session_id=a, to_session_id=c, edge_type="depends_on", note=None),
        dict(from_session_id=b, to_session_id=c, edge_type="reinforces", note="Exercise"),
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
    copied = client.post(f"/api/v1/courses/{course}/roadmaps/draft-from-approved").json()["id"]
    data["session_edges"][2]["note"] = "New exercise"
    data["sessions"].reverse()
    assert client.put(root + copied, json=data).is_success
    assert client.post(root + copied + "/approve").is_success
    saved = client.get(f"/api/v1/courses/{course}/roadmaps/approved").json()
    assert sorted(saved["session_edges"], key=str) == sorted(data["session_edges"], key=str)
    assert [s["stable_id"] for s in saved["sessions"]] == [s["id"] for s in data["sessions"]]
    assert saved["sessions"][-1]["topic_ids"] == ["foundations","practice"]
    diff = client.get(root + version + "/diff/" + copied).json()
    assert diff["links"]["changed"][0]["after"]["note"] == "New exercise"
    assert len(client.get(f"/api/v1/courses/{course}/roadmaps").json()) == 2


@pytest.mark.parametrize("case", ["cycle","dangling","self","duplicate","membership","id","sequence"])
def test_rejected_edits_are_atomic(client, monkeypatch, case):
    _, data, version = setup_graph(client, monkeypatch)
    first = data["session_edges"][0]
    if case == "cycle":
        data["session_edges"].append(dict(first, from_session_id=first["to_session_id"], to_session_id=first["from_session_id"]))
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
