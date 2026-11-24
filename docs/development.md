# Local development

Use the [README](../README.md) to install and start the application. The supported presentation configuration is one FastAPI process bound to 127.0.0.1 with a SQLite database. The browser and API use the same origin. The [fixture runner](../scripts/demo_walkthrough.py) starts an isolated instance and overrides the generator only in that process.

## Configuration

| Setting | Local behavior |
| --- | --- |
| DATABASE_URL | Defaults to `sqlite:///./data/teachflow.db`, relative to the server working directory. Run migration and server from `backend/`. |
| TEACHFLOW_DATA_DIR | Defaults to `./data`. Original files and text exports are stored in its materials directory. |
| MAX_UPLOAD_BYTES | Default material limit is 10 MiB. Calendar previews accept up to 512,000 bytes, transcripts up to 100,000 bytes. |
| LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_API_STYLE | Existing provider adapter settings. Leave credentials unset for the offline and manual flows. |
| LLM_TIMEOUT_SECONDS | Default request timeout is 60 seconds. |
| TEACHFLOW_CHROMIUM | Optional path to a Chromium executable for the browser checks. |

## API outline

Interactive request/response schemas are at `/docs`. Health endpoints are `/health` and `/health/ready`. Paths below are relative to `/api/v1`. Braces mark path parameters.

| Area | Routes |
| --- | --- |
| Course | GET/POST `/courses`; GET/PUT/DELETE `/courses/{course}` |
| Group | GET/POST `/courses/{course}/groups`; PUT/DELETE `/courses/{course}/groups/{group}` |
| Schedule | POST multipart file to `/calendar/preview`; confirm edited records with the group endpoints |
| Materials | GET/POST `/courses/{course}/materials`; DELETE `/courses/{course}/materials/{material}`. Results contain extraction status, warnings and chunk IDs with locators. |
| Roadmaps | POST `/courses/{course}/roadmaps/generate` with Idempotency-Key. GET `/courses/{course}/roadmaps` for versions. GET `/courses/{course}/roadmaps/approved`. POST `/courses/{course}/roadmaps/draft-from-approved`. |
| Draft and history | GET/PUT `/roadmaps/{version}`; POST `/roadmaps/{version}/approve`; GET `/roadmaps/{old}/diff/{new}` |
| Progress | PUT `/groups/{group}/sessions/{session}/progress` or `/benchmark`; GET `/groups/{group}/progress` or `/overview`. A null target clears the explicit date. |
| Reviews | GET/POST multipart `/groups/{group}/sessions/{session}/reviews`; GET/PUT `/reviews/{id}`; POST `/reviews/{id}/approve` |
| Packages | POST `/reviews/{id}/package`; GET `/packages/{id}`; PUT `/packages/{id}/items/{item}` with text and approve |
| Instructor workspace | GET `/courses/{course}/approvals` and `/history`; POST `/courses/{course}/assistant` with group_id and question |

### Frontend modules

The FastAPI process serves `frontend/index.html`. The page handles navigation and mounts the instructor screens. `frontend/js/api.js` owns HTTP paths, the fetch call, JSON decoding and response errors. It emits the recorded-demo event. `courses.js` maps the API records into course state and saves setup data. `workspace.js` renders lists, benchmarks, approvals and the demo banner. `graph.js` maps stable IDs and renders citations. Setup, review and assistant interactions live in their own modules. The Node tests exercise the HTTP client without a browser. Playwright covers the mounted UI against the fixture server.

### Roadmap contract

Use stable identifiers matching `^[A-Za-z0-9_-]{1,80}$` in proposals. Session edges carry from_session_id, to_session_id, edge_type and optional note. Primary topic_id in a GET identifies the database record, while topic_ids and edge endpoints are stable identifiers. Proposal topic references use stable identifiers. Topic and session array order is saved explicitly.

Prerequisite and depends_on point from required to dependent session. The combined hard-edge graph must be acyclic. Reinforces, extends, introduces and applies run from acting to referenced session. Link identity is the directed endpoints plus type. A note edit appears under changed in a diff. Changing direction or type removes one identity and adds another.

Existing topic dependencies and within-topic order provide the legacy graph backfill. An explicitly empty session_edges array saves an empty graph. Stable session identity carries cohort progress across versions. Changing the objective list resets its completion indexes. Recorded links lost before the migration cannot be recovered.

### Schedule and material formats

CSV uses one header and one group per row:

```csv
name,weekday,start_time,duration_minutes,start_date
Saturday group,Saturday,10:00,60,2026-11-28
```

Use an English weekday, a 24-hour wall-clock time and an ISO date. ICS supports timed VEVENTs with SUMMARY, DTSTART, DTEND, and basic weekly RRULE with optional BYDAY. Check the displayed wall-clock time and date. Unsupported recurrence rules produce preview errors. Direct group entry is always available.

UTF-8 TXT, Markdown, PY, JS, TS, JAVA and JSON, and text-based PDFs, produce chunks with source locations. Source code is read as text. Export Office documents and scanned PDFs to readable text. Legacy exports use character offsets when original page boundaries are unavailable. Generation is bounded to 30 materials, 20,000 characters per material and 100,000 total source characters. The proposal carries warnings for omissions and sessions lacking source citations. For a session that cites materials, every listed source must resolve to a chunk in the course. A legacy material-only reference resolves automatically when exactly one passage is available. For an ambiguous source, an editor PUT returns 422 until the instructor selects a passage. A chunk from a different material cannot satisfy that requirement. The detail panel lists the filename and selected locations for every cited file.

An unsupported Office file returns material status `unsupported` and instructions to export to text or text-based PDF. The browser also explains the conversion at file selection. A PDF with no extractable text returns `empty` and requests a text export. No OCR is performed.

### Review and assistant contracts

Evidence offsets are zero-based Unicode code points with an exclusive end. Each objective receives one finding. Covered and partial findings require matching transcript text. Review and package editors identify manual drafts when AI is unavailable. The package uses the approved review, and each of its four items has an individual approval state.

The Assistant uses local keyword matching over material chunks, approved sessions/links and the selected group's facts. Its response contains a status, answer and reference list. The generated answer uses validated excerpts so its passages can be checked against their sources. An unsupported quotation produces an insufficient-evidence response. There are no assistant write tools.

## Reproduce verification

From the repository root, after activating the environment and installing Chromium for Playwright, run the following commands.

```sh
python -m pytest -q
node --test frontend/tests/roadmap-layout.test.cjs frontend/tests/session-graph.test.cjs frontend/tests/workspace.test.cjs
python scripts/demo_walkthrough.py --browser
```

On 24 November 2026 these commands passed 54 backend tests, 20 frontend tests and the full HTTP/browser walkthrough on port 8000. The independent graph refresh check and migration commands are in the [test report](TEST_REPORT.md). Live AI output quality remains unverified.
