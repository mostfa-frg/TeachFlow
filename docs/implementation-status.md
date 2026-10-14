# Development status and next steps

## Delivered in this stage

- Split FastAPI bootstrap, versioned API routes, domain models, configuration, persistence, and generation/ingestion services.
- Added Alembic persistence for courses, instructor groups, materials, versioned roadmaps, topics, sessions, directed topic dependencies, and group-specific progress.
- Implemented bounded TXT/Markdown/PDF ingestion and explicit extraction outcomes.
- Implemented configurable structured roadmap generation, schema/reference/DAG validation, idempotent draft creation, draft editing, explicit approval, and version supersession.
- Connected the setup wizard's course, group, upload, generation, edit, and approval actions to the API; removed fabricated generation output and progress.
- Improved schedule preview review, upload drag/drop and status messaging, and fit/zoom behavior.

## Remaining, in priority order

1. Add instructor authentication and authorization before network exposure.
2. Add browser/API integration tests and complete group-specific progress controls in the interface.
3. Add model-provider fixtures/evaluations for material grounding, unsupported claims, and dependency quality.
4. Add background processing for larger material libraries and provider requests if real usage requires it.
5. Add calendar synchronization, more document formats, and OCR only for demonstrated scanned-document demand.

This remains a local-development foundation, not a production-ready hosted service. Provider-backed roadmap generation requires `LLM_API_KEY` and `LLM_MODEL`; no paid-provider call was made in local validation.
