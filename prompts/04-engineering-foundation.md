# PROMPT 04 — Foundation: frontend, backend, database, auth, CI

Read the contract, brief, approved ADRs/contracts, all existing code and `git status`. Implement the smallest vertical slice without replacing functioning code unnecessarily.

- Arrange repo/workspace into clear frontend/backend/shared-contracts/docs/test areas consistent with the approved base. Build an instructor-only authenticated app shell with routing, responsive sidebar, dashboard placeholder with correct states, graph route, session route, approvals route, setup route, assistant drawer; do not fake functionality. Add design tokens and base components from UX spec.
- Build backend app entry point, typed settings/env example, request validation, OpenAPI, health/readiness endpoint, structured errors, request IDs and redacted logs, CORS/CSRF appropriate to chosen auth, authorization guards and tenancy checks.
- Implement approved DB model with forward and rollback-aware Alembic migrations, constraints, indexes and relationships; repository/service boundaries, transactional approval and audit primitives; seed synthetic Python course/multiple groups (no user data).
- Implement actual auth flow/adapter (instructor/admin only), permission matrix at query and resource level, no student endpoints. Provide robust local dev bootstrap (Docker Compose optional if approved) and env example, scripts, CI commands.
- Write tests: auth/IDOR, invalid inputs, migration on blank DB, rollback strategy, API contract, navigation and frontend component smoke; run lint/types/tests. Define minimum coverage targets as *proposed*, not invent success.
- Update traceability/status/risk/decision docs; add working README quickstart and exact commands. **No external paid APIs needed for this phase.**

Checkpoint: demo an instructor login (or approved secure dev auth), create/read own course and groups through real DB APIs, forbidden access to another owner's course, migration from clean DB, working shell. Stop and provide milestone verification report. Ask before next prompt.
