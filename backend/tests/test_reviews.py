from app.api.v1 import router
from app.services import GeneratorNotConfigured
from test_graph import setup_graph


class Manual:
    async def generate_structured(self, *args):
        raise GeneratorNotConfigured()


def test_transcript_evidence_and_individual_approval(client, monkeypatch):
    course, _, rid = setup_graph(client, monkeypatch)
    s = client.post(f"/api/v1/roadmaps/{rid}/approve").json()["sessions"][0]
    url = f"/api/v1/courses/{course}"
    group = client.post(url + "/groups", json={"name": "Saturday"}).json()["id"]
    monkeypatch.setattr(router, "roadmap_generator", Manual())
    route = f"/api/v1/groups/{group}/sessions/{s['id']}/reviews"
    assert client.post(route, files={"file": ("sample.md", "")}).status_code == 422
    review = client.post(
        route, files={"file": ("sample.md", "Functions accept arguments.")}
    ).json()
    assert review["mode"] == "manual" and review["findings"][0]["evidence"] == []
    path = "/api/v1/reviews/" + review["id"]
    assert client.post(path + "/package").status_code == 409
    finding = dict(
        objective_index=0,
        status="covered",
        confidence=0.9,
        evidence=[dict(start=0, end=9, snippet="Functions")],
    )
    assert (
        client.put(path, json={"findings": [dict(finding, evidence=[])]}).status_code
        == 422
    )
    assert (
        client.put(
            path,
            json={
                "findings": [
                    dict(finding, evidence=[dict(start=1, end=9, snippet="Functions")])
                ]
            },
        ).status_code
        == 422
    )
    client.put(path, json={"findings": [finding]}).raise_for_status()
    assert client.get(url + "/approvals").json()[0]["kind"] == "review"
    client.post(path + "/approve").raise_for_status()
    package = client.post(path + "/package").json()
    assert package["mode"] == "manual" and all(
        v["text"] == "" for v in package["items"].values()
    )
    assert client.get(url + "/approvals").json()[0]["kind"] == "package"
    for key in package["items"]:
        target = f"/api/v1/packages/{package['id']}/items/{key}"
        assert client.put(target, json={"text": "", "approve": True}).status_code == 422
        saved = client.put(
            target, json={"text": "Instructor draft", "approve": True}
        ).json()
    assert saved["state"] == "approved" and client.get(url + "/approvals").json() == []
    assert (
        len(
            [r for r in client.get(url + "/history").json() if r["state"] == "approved"]
        )
        == 7
    )
