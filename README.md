# TeachFlow

TeachFlow is an instructor-only course planning platform. The repository retains its standalone HTML/CSS/JavaScript prototype and adds a FastAPI modular-monolith backend. It has no student portal and does not depend on an external LMS.

## Current implementation

- The backend persists courses, instructor groups, materials, versioned roadmaps, topics, sessions, dependency edges, and group-specific progress with SQLAlchemy 2.x.
- Alembic provides the initial database migration. SQLite is the local default; PostgreSQL is supported by setting `DATABASE_URL`.
- TXT, Markdown, and text-based PDF uploads are size-limited, stored under generated filenames, and extracted before they can be used as generation context.
- Roadmap generation defaults to Groq's OpenAI-compatible Chat Completions endpoint and `openai/gpt-oss-20b`; the provider, model, and API style are configurable. Without credentials, generation responds with a clear `503`; no example or simulated AI response is substituted.
- Proposed roadmaps are validated and saved as drafts. Editing a draft and explicit approval are separate API actions; approving a newer version supersedes the previous approved roadmap.
- The browser prototype remains recognizable and is served from the API at `/`. Its local sample course is clearly labelled demonstration data.

The browser prototype loads saved courses, groups, materials, approved roadmaps, and group-specific session-goal progress from the API; progress changes are written back and restored after reload. When a new roadmap version is approved, progress follows sessions with unchanged stable IDs; objective completion is preserved only when that session's goal list is unchanged. Progress for removed sessions remains historical and is excluded from the active-group progress response. Draft recovery still uses browser storage. Authentication and instructor ownership checks, calendar integration, OCR, and the broader workflow are not production-ready. The API currently has no instructor identity boundary: keep it local/trusted and do not expose this service publicly until authentication and per-instructor authorization are implemented.

## Project layout

```text
frontend/
  index.html             Existing instructor UI prototype
backend/
  app/                   FastAPI application, API, domain, and services
  migrations/            Alembic schema migrations
  tests/                 Backend tests
docs/                    Architecture, data model, development, and status
requirements.txt         Single dependency list
pytest.ini               Single test configuration
.env.example             Shared local configuration template
```

## Local development

Use Python 3.10 or later. In PowerShell from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
Set-Location backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/` for the prototype, `/docs` for API documentation, `/health` for liveness, and `/health/ready` for database readiness.

Run automated checks from the repository root:

```powershell
python -m pytest
```

Configuration is read from process environment variables and the repository-root `.env` file. See [`.env.example`](.env.example). SQLite data and uploaded documents are stored in `backend/data` when the server is started from `backend`; the directory is ignored by Git. Set `TEACHFLOW_DATA_DIR` to move uploaded material storage. PostgreSQL may be configured with a SQLAlchemy URL such as `postgresql+psycopg://...`; install the appropriate PostgreSQL driver when using it.

## Documentation

- [Architecture and workflow](docs/architecture.md)
- [Domain model](docs/data-model.md)
- [Development, configuration, and limitations](docs/development.md)
- [Implementation status and next steps](docs/implementation-status.md)
