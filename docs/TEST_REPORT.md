# Local demo verification · 24 November 2026

Tests ran on Linux with Python 3.12.14, Node 24.22.3, SQLite and headless Chromium. HTTP and browser runs used disposable databases and synthetic files. Provider responses came from stubs or labelled fixtures.

| Check from repository root | Observed result |
| --- | --- |
| `python -m pytest -q` | **54 passed**, one upstream Starlette TestClient/httpx deprecation warning. Includes the original 29 regressions. |
| `node --test frontend/tests/roadmap-layout.test.cjs frontend/tests/session-graph.test.cjs frontend/tests/workspace.test.cjs` | **20 passed**, zero failures or skips. Includes all 13 original frontend checks. |
| `python scripts/demo_walkthrough.py --browser` | HTTP workflow and instructor browser workflow passed on `127.0.0.1:8000`. The walkthrough exits on any failed expectation. |
| `PYTHONPATH=backend python backend/tests/graph_browser.py` | Independent Chromium edit/approve/refresh test passed. The fresh approved-roadmap GET matched all three typed, directed links including their notes. |
| `python -m alembic upgrade head`, `python -m alembic current`, `python -m alembic check` from `backend/` | Fresh temporary SQLite database reached `0007_session_reviews (head)`. Alembic reported no new upgrade operations. |

The normal entry point (`python -m uvicorn app.main:app --host 127.0.0.1 --port 8000` from `backend/`) was also exercised against a fresh database with credentials empty. The root page and readiness check returned 200. Roadmap generation returned 503. The Assistant returned unavailable status and locally retrieved references.

The commands above use the active Python environment. For the browser runs here, `TEACHFLOW_CHROMIUM` pointed to an installed headless executable. The [walkthrough](DEMO_WALKTHROUGH.md) includes installation, free-port and PowerShell commands.

## Milestones and regression coverage

Each commit link opens its file-by-file diff. Counts in the first five rows record the offline suite at that milestone. The table above gives the final totals.

| Priority | Implementation and tests | Verified at milestone |
| --- | --- | --- |
| 1 · Roadmap persistence | Additive graph migration, models, validators, version/diff API and instructor editor. Backend and Chromium regressions cover three edges, direction, note, cycle, dangling and duplicate links, secondary topic membership and fresh reads. [Storage and API](https://github.com/mostfa-frg/TeachFlow/commit/5dc715a) · [Editor and refresh](https://github.com/mostfa-frg/TeachFlow/commit/4afdec9) | 40 backend, 13 frontend |
| 2 · Smart Setup | Schedule preview, per-row errors, source chunks, ingestion status and citations. [Implementation and tests](https://github.com/mostfa-frg/TeachFlow/commit/76181e5) | 44 backend, 13 frontend |
| 3 · Group progress | Real dashboard and queue data, group-specific benchmarks and prerequisite reminders. [Implementation and tests](https://github.com/mostfa-frg/TeachFlow/commit/fcabdc2) | 45 backend, 13 frontend |
| 4 · Review and follow-up | Transcript evidence, editable findings, individual approvals and local history. [Implementation and tests](https://github.com/mostfa-frg/TeachFlow/commit/9d7791e) | 46 backend, 13 frontend |
| 5 · Assistant | Local retrieval, checked quotations, group scope, missing-provider and untrusted-document cases. [Implementation and tests](https://github.com/mostfa-frg/TeachFlow/commit/f67f3e5) | 47 backend, 13 frontend |
| 6 · Walkthrough and regression checks | Synthetic course, schedules, materials, transcript and recorded responses. HTTP and Playwright workflows cover setup through the cited answer. [Walkthrough](https://github.com/mostfa-frg/TeachFlow/commit/be8fa88) · [Concurrency and legacy sources](https://github.com/mostfa-frg/TeachFlow/commit/3abb6af) | HTTP and Chromium passed |

## Resumed work

At pickup the checkout had three uncommitted documents and one unpublished code change after matching equivalent commits by patch. The pending change kept typed edges and secondary memberships in legacy draft edits and reported changes in session order in version diffs. The recovered baseline passed 53 backend and 15 frontend tests. [Compatibility fixes and two backend regressions](https://github.com/mostfa-frg/TeachFlow/commit/0a3b12e)

- Added one backend regression for a session citing two materials. The API requires a located passage for each source, rejects an ambiguous source and persists the selected chunks through approval. [Test and validation](https://github.com/mostfa-frg/TeachFlow/commit/3caded3)
- Finished separating HTTP calls from rendering. Three Node tests check the recorded-mode event and generation keys, validation errors, and queue actions. [Frontend split and tests](https://github.com/mostfa-frg/TeachFlow/commit/a57ede2)
- Removed the session detail panel's three-material limit. A Node regression renders four cited files, including only each file's selected passages. [Citation rendering and test](https://github.com/mostfa-frg/TeachFlow/commit/2dc28d8)
- Added a Node regression for benchmark loading. Chromium checks switching between groups, opening the named prerequisite, setting a target and reading it after refresh. The Materials screen recovers from a forced request failure. Office upload guidance and the text-export message for a textless PDF both appeared in the browser. The test opens all three proposal types directly from Approvals and verifies the count after the last item is approved. [UI fix and browser regressions](https://github.com/mostfa-frg/TeachFlow/commit/6a640f4)

## Verification limits

**Live AI output quality remains unverified.** Recorded responses exercise integration, evidence provenance and approval rules. The run used no live provider calls, spend or real recordings. Windows desktop execution, clipboard contents and a full screen-reader audit remain manual checks. No database table was removed. Older session links that had already collapsed to topic dependencies cannot be reconstructed beyond the documented backfill.

## Historical Phase 00 verification · 21 November 2026

Baseline `6e3c7fa0a7f23211dd583abda62860907238ac2e`. Windows, CPython 3.14.0, Node v24.21.0, clean isolated checkout. Product code and tests came directly from the baseline.

| Check | Exact command or reproduction | Result |
| --- | --- | --- |
| Baseline | `git status --short --branch`, `git rev-parse HEAD`, `git ls-files` | Initial clean checkout at 5a9658c had 30 tracked files. Reconciled against 6e3c7fa, with 47 tracked files on main (git ls-tree -r --name-only origin/main). |
| Environment | `python -m venv .venv`, then `.\.venv\Scripts\python.exe -m pip install --disable-pip-version-check -r requirements.txt` | Installed declared dependencies. The host Python alone lacked pytest. An initial restricted package lookup returned no candidates. |
| Dependency consistency | `.\.venv\Scripts\python.exe -m pip check` | No broken requirements. Resolved FastAPI 0.165.0, Starlette 1.10.0, Pydantic 2.14.4, SQLAlchemy 2.1.9, Alembic 1.20.1, pypdf 6.21.4, httpx 0.28.1 and pytest 8.4.2. No lockfile or advisory scan at this milestone. |
| Existing regression suite | `.\.venv\Scripts\python.exe -m pytest -q` | **29 passed, 1 warning** in 2.76 s on the reconciled branch (1.59 s on the initial baseline). Starlette warns its httpx TestClient integration is deprecated. The first sandboxed run stalled creating the Windows asyncio local socket pair. A targeted traceback identified the fixture startup; the same suite completed with local socket access. |
| Migration chain | From backend, `..\.venv\Scripts\python.exe -m alembic upgrade head`, then `..\.venv\Scripts\python.exe -m alembic current` and `..\.venv\Scripts\python.exe -m alembic check` | Rechecked with DATABASE_URL=sqlite:///./data/phase00-reconciled.db. Fresh disposable SQLite DB applied all three revisions. Current head 0003_session_goal_progress. No new upgrade operations detected. |
| Shell syntax and graph save | From root, pipe the JavaScript block in [UI_BASE_SPIKE.md](architecture/UI_BASE_SPIKE.md) to `node` | Passed compilation and all four assertions. The result confirms a defect in representation: three displayed session links yield one saved topic dependency. |
| Frappe schema fit | Inspect the four v16.1.0 JSON field_order arrays listed in the [spike](architecture/UI_BASE_SPIKE.md) | Course/batch/time anchors present. The tested lesson definition lacks the four TeachFlow-specific fields. Source compatibility assessed. Server install, login and deployment untested. |
| Audit deliverables | SHA-256 comparison with the supplied files, relative link resolution and matrix row count | All 14 rules/brief/prompt files matched byte for byte in the working tree. All 33 local links across the nine new instruction/audit records resolved, and the matrix contains 12 areas. |

The suite uses SQLite and synthetic/mock AI results. It covers persistence, uploads and error handling, proposal validation, retry, edit/approval, version transitions, group isolation and legacy sequence ordering. It does not establish live model quality, instructor isolation, accessibility, browser end-to-end behavior, PostgreSQL operation or deployment readiness. No project lint, format, type-check, accessibility or security runner was configured. No provider keys, paid calls or external document uploads were needed.

## Historical Phase 01 · 22 November 2026

On the merged baseline with the Git workflow amendment, the existing offline suite passed: python -m pytest -q produced 29 passed and one upstream Starlette TestClient deprecation warning in 3.22 s. Phase 01 changes are documentation only. Catalogue validation checked 13 requirement/story/acceptance mappings, case anchors, six nonfunctional requirements, six business rules and local document links. Git diff whitespace validation passed. No configured project lint runner. Product acceptance cases and pilot targets await implementation and evaluation.
