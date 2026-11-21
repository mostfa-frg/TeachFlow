# PROMPT 03 — Architecture, threat model, data model and API contracts (HARD STOP GATE D)

Read the rules, brief, accepted product/UX docs and existing implementation. Design the *simplest production-minded modular monolith* that can satisfy the approved P0. This phase is contracts and scaffolding plan, NOT a sweeping rewrite.

Produce `docs/architecture/` including:
- Context/container/component diagrams (Mermaid), request flows and background-job sequence diagrams; frontend, FastAPI/backend or approved alternative, PostgreSQL, job runner, document/object storage, search/index, LLM/STT adapters, calendar integration, audit service; identify ownership and failure boundaries.
- Frontend ADR: approved framework, routing, server cache vs local state, forms, API client, graph renderer, reusable components, error boundaries, testing; modular layout & accessibility support.
- Backend ADR: endpoint/controller, service/domain, repository/transaction, integration adapters, ingestion pipeline, workers and outbox patterns where needed, error taxonomy, validation, observability, API documentation.
- Relational logical model and **Mermaid ERD**, cardinalities + constraints for tenant/instructor, course, group, session, group_session occurrence, topic, session_topic, objective, material/file version, source chunk, typed session relationship edge, benchmark, group benchmark status + evidence, calendar connection/event mapping, import job, session review and observation, post-session package, proposal/approval, audit event, plan revision; include owner IDs, timezones, timestamps, unique keys, foreign keys, multi-tenant isolation and lifecycle/retention.
- Service and domain state machines: import, AI proposal, review/approve/reject/modify, benchmark, plan version, review, job errors/retry. Define optimistic locking/idempotency for approvals, dependency direction/cycle rules, UTC storage plus user timezone, canceled or rescheduled calendars, group progress formula, out-of-date AI proposals on source changes.
- OpenAPI-first request/response/error/pagination/async-job contracts + endpoint authorization matrix, event schemas, import limits and search response provenance. Explicit versioning and backwards compatibility strategy.
- Security/privacy threat model: auth/RBAC, tenant boundary, object ACL, OAuth scopes/state/token encryption/revocation, untrusted file parsing, prompt injection, transcripts and recording consent, data deletion, export, rate limiting, secrets, SSRF, audit events.
- Deployment/topology (local/hosted options), CI/migrations/rollback, cost controls, observability SLO candidates and test architecture; required vs optional cloud services.

Add ADRs for alternatives instead of choosing based on hype. Compare custom UI vs Frappe decision, auth solution, hosting and object storage, calendar provider/ICS, model and STT vendor/budget. Proposed defaults are **not** approval for paid/sensitive services.

**Gate D1:** Present critical choices as a concise decision table and explicitly request approval of deployment, auth, data/privacy/OAuth, provider/cost and DB changes if relevant. No production migrations or external integrations until approved. **STOP.**
