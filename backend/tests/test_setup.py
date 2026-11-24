from dataclasses import replace
from app.api.v1 import router
from app.ingestion import document_chunks
from test_api import StubGenerator, create_course, sample_proposal


def test_calendar_is_editable_preview_with_row_errors(client):
    csv = "name,weekday,start_time,duration_minutes,start_date\nSat,Saturday,09:30,45,2026-11-28\nBad,Someday,08:00,10,broken"
    preview = client.post("/api/v1/calendar/preview", files={"file":("test.csv", csv)}).json()
    assert len(preview["groups"]) == 1 and preview["errors"][0]["row"] == 3
    data = dict(preview["groups"][0], start_time="11:30")
    course = create_course(client)["id"]
    url = f"/api/v1/courses/{course}/groups"
    assert client.get(url).json() == []
    assert client.post(url, json=data).is_success
    assert client.get(url).json()[0]["start_time"] == "11:30"


def test_ics_weekly_and_bad_event(client):
    body = "BEGIN:VEVENT\nSUMMARY:Lab\nDTSTART:20261128T093000\nDTEND:20261128T101500\nRRULE:FREQ=WEEKLY;BYDAY=SA,MO\nEND:VEVENT\nBEGIN:VEVENT\nSUMMARY:Broken\nEND:VEVENT"
    result = client.post("/api/v1/calendar/preview", files={"file":("schedule.ics",body)}).json()
    assert [r["weekday"] for r in result["groups"]] == ["Saturday","Monday"]
    assert [r["start_date"] for r in result["groups"]] == ["2026-11-28","2026-11-30"]
    assert result["errors"][0]["row"] == 7


def test_chunk_locations():
    assert list(document_chunks("alpha\fbeta", ".pdf"))[1] == ("Page 2, chars 0–4","beta")
    assert list(document_chunks("# Intro\nLoops\n# End\n", ".md"))[0] == ("Intro, lines 1–2","# Intro\nLoops\n")
    assert list(document_chunks("abc", ".py")) == [("Chars 0–3","abc")]


def test_code_citations_and_visible_truncation(client, monkeypatch, tmp_path):
    monkeypatch.setattr(router,"settings",replace(router.settings, data_dir=tmp_path))
    monkeypatch.setattr(router,"MAX_EXTRACTED_CHARS",5)
    course = create_course(client)["id"]
    base = f"/api/v1/courses/{course}"
    m = client.post(base+"/materials",files={"file":("sample.py","print(123)","text/plain")}).json()
    chunk = m["chunks"][0]["id"]
    data = sample_proposal(m["id"])
    data["sessions"][0]["supporting_chunk_ids"] = [chunk]
    generator = StubGenerator(data)
    monkeypatch.setattr(router,"roadmap_generator",generator)
    result = client.post(base+"/roadmaps/generate").json()
    assert result["sessions"][0]["supporting_chunk_ids"] == [chunk]
    assert generator.context["chunks"][0]["text"] == "print"
    assert any("omitted" in warning for warning in result["warnings"])
    data["sessions"][0]["supporting_chunk_ids"] = ["missing"]
    assert client.put("/api/v1/roadmaps/"+result["id"],json=data).status_code == 422
