# Phase 00 verification · 21 November 2026

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

## Phase 01 · 22 November 2026

On the merged baseline with the Git workflow amendment, the existing offline suite passed: python -m pytest -q produced 29 passed and one upstream Starlette TestClient deprecation warning in 3.22 s. Phase 01 changes are documentation only. Catalogue validation checked 13 requirement/story/acceptance mappings, case anchors, six nonfunctional requirements, six business rules and local document links. Git diff whitespace validation passed. No configured project lint runner. Product acceptance cases and pilot targets await implementation and evaluation.
