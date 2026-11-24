# TeachFlow

TeachFlow helps one instructor plan a course, track each group's progress, review a transcript and prepare a follow-up. The presentation app runs on localhost with FastAPI, SQLite and the existing browser interface.

## Try the synthetic demonstration

From the repository root in Windows PowerShell, with Python installed, run the following commands.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/demo_walkthrough.py --serve
```

Open http://127.0.0.1:8000. The command creates a temporary database, applies migrations, loads the sample Python course, exercises the full API workflow and leaves the app open. The banner identifies recorded synthetic responses. Ctrl+C closes the demo and releases its temporary data. Use `--empty --serve` to perform the setup yourself.

## Run with persistent local data

```powershell
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

This entry point stores local data under `backend/data`. Without provider credentials, roadmap generation returns 503, review and package editors offer manual drafting, and the Assistant shows locally retrieved references. Provider selection and live quality evaluation require an owner decision.

## Instructor workflow

1. Create a course and groups. Enter schedules directly or edit and confirm an ICS/CSV preview.
2. Upload materials and inspect extraction status and source locations.
3. Review the proposed sessions, edit topics and typed links, then approve the roadmap.
4. Switch between groups to update objectives, set target dates and open incomplete prerequisites.
5. Upload a synthetic TXT/MD transcript from session details. Review evidence and approve the findings.
6. Edit and approve each follow-up item. Copy approved text when ready.
7. Ask the Assistant a question about the selected course or group and inspect its references.

## Verification and reference

- [Demo commands and manual browser checklist](docs/DEMO_WALKTHROUGH.md)
- [Test results, milestone commits and verification limits](docs/TEST_REPORT.md)
- [Project status](docs/PROJECT_STATUS.md) and [approved local scope](docs/product/MVP_SCOPE.md)
- [API outline, file formats and configuration](docs/development.md)
- [Engineering decisions](docs/DECISIONS.md)

On 24 November 2026 the local suite passed 54 backend tests, 20 frontend tests and both Chromium acceptance checks. The automated run used synthetic data and recorded responses. Live AI output quality remains unverified.

From the repository root, run the backend and frontend suites with these commands. Chromium setup and commands are in the walkthrough.

```sh
python -m pytest -q
node --test frontend/tests/roadmap-layout.test.cjs frontend/tests/session-graph.test.cjs frontend/tests/workspace.test.cjs
```
