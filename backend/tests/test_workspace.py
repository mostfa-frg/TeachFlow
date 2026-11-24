from test_graph import setup_graph


def test_real_drafts_and_scoped_prerequisites(client, monkeypatch):
    course, _, rid = setup_graph(client, monkeypatch)
    url = f"/api/v1/courses/{course}"
    assert client.get(url + "/approvals").json()[0]["id"] == rid
    plan = client.post(f"/api/v1/roadmaps/{rid}/approve").json()
    assert client.get(url + "/approvals").json() == []
    groups = [
        client.post(url + "/groups", json={"name": name}).json()["id"]
        for name in ("Sat", "Mon")
    ]
    start, next_session = plan["sessions"][:2]
    for group in groups:
        base = f"/api/v1/groups/{group}"
        client.put(
            base + f"/sessions/{next_session['id']}/benchmark",
            json={"target_date": "2020-01-01"},
        ).raise_for_status()
        overview = client.get(base + "/overview").json()
        assert overview["sessions"][1]["status"] == "behind"
        assert overview["reminders"][0]["missing_id"] == start["stable_id"]
    client.put(
        f"/api/v1/groups/{groups[0]}/sessions/{start['id']}/progress",
        json={"state": "completed"},
    ).raise_for_status()
    assert not client.get(f"/api/v1/groups/{groups[0]}/overview").json()["reminders"]
    assert client.get(f"/api/v1/groups/{groups[1]}/overview").json()["reminders"]
