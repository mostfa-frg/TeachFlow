# TeachFlow Backend

AI-first backend foundation for the instructor-only TeachFlow platform. This service is independent of Frappe LMS.

## Stack direction

- Python + FastAPI for HTTP APIs
- Pydantic for validated request/response contracts
- PostgreSQL for durable course, group, session, dependency, material, and approval data (not wired in this foundation commit)
- A document-ingestion pipeline for extracting text/metadata before any LLM call
- One Instructor Agent with explicit tools; add LangGraph only when a workflow needs durable state or human approval
- A model-provider adapter behind the roadmap-generation service, so model/vendor choices do not leak into API routes

## Run locally

From this directory:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `/docs` for the API contract and `/health` for a health check.

## Current scope

This commit establishes the API and generation boundary only. It does not claim to parse uploaded files, call an LLM, persist data, connect a calendar, or generate a real roadmap. The roadmap endpoint validates the request and returns a clear service-unavailable response until a generator is configured.

## Next vertical slice

1. Add SQLAlchemy models and Alembic migrations for courses, groups, materials, topics/sessions, dependency edges, and plan versions.
2. Add a material ingestion interface (extract text/metadata first; OCR only when needed).
3. Implement a provider-backed roadmap generator that returns schema-validated JSON.
4. Persist proposed roadmaps as drafts and require instructor approval before activation.
5. Add evaluation fixtures for topic coverage, dependency validity, and unsupported claims.
