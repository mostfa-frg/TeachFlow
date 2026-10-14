# Architecture

TeachFlow is a single FastAPI modular monolith. The browser prototype is served by FastAPI and communicates with versioned JSON endpoints. API handlers validate requests and coordinate persistence and application services; document extraction and roadmap generation live behind replaceable service interfaces. SQLAlchemy 2.x uses synchronous sessions through FastAPI dependency injection. Alembic owns schema changes. SQLite provides a simple local setup and PostgreSQL is the target persistent database.

## Roadmap workflow

1. Create a course, its instructor groups, and materials.
2. Upload TXT, Markdown, or PDF files. The API enforces the byte limit, stores content at generated paths, extracts text, and records `processed`, `partial`, `empty`, `unsupported`, or `failed`.
3. Request `POST /api/v1/courses/{course_id}/roadmaps/generate`. Only successfully extracted text is passed to the configured provider. The provider result is parsed into a Pydantic proposal, checked for valid references and an acyclic topic dependency graph, then persisted as a new draft version.
4. Review with `GET /api/v1/roadmaps/{roadmap_id}` and optionally replace a draft with a validated edit using `PUT`.
5. Explicitly activate the draft with `POST /api/v1/roadmaps/{roadmap_id}/approve`. Approval supersedes the former approved version in a database transaction.

The provider consumes untrusted material as evidence only; it has no tools or authority to mutate application state. Missing provider configuration fails clearly instead of synthesizing a roadmap. A request idempotency key prevents duplicate versions when a caller safely retries.

The course-setup wizard now calls the API for course/group persistence, material uploads, generation, draft editing, and approval. Existing sample-course exploration and some non-core dashboard/navigation behavior remain browser-local.

## Deployment boundary

The service has no instructor authentication yet. Treat it as local development software only; add identity and per-instructor authorization before exposing course or material data to a network. There is no student-facing interface, Frappe LMS dependency, task queue, Redis, or microservice boundary.
