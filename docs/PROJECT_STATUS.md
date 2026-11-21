# Current project status — local presentation scope

**D1 approved (22 November 2026):** one-instructor localhost demo only. **Authentication, multi-user ownership and deployment are OUT OF SCOPE**, not active blockers. The Phase 00 table below is retained as historical audit evidence. Active missing functionality: session relationship persistence, complete navigation, calendar/material ingestion, group-specific benchmarks, transcript review, follow-up package and Instructor Assistant. See [current P0 definition](product/MVP_SCOPE.md).

## Phase 00 baseline

**Phase 00 discovery delivered for review. MVP incomplete.** The baseline, branch and inventory appear in the [audit](00_AUDIT.md). The branch fills the root instructions file and adds the audit, feasibility experiment, decision and verification records. The reconciled base already contains the canonical brief, project rules and all twelve prompts. The owner approved A1 option A on 22 November 2026. PR #5 merged at 58927ec.

| Workflow at the audited revision | Status | What an instructor can rely on |
| --- | --- | --- |
| Course, group, material and plan lifecycle | PARTIAL | Backend endpoints persist these records. The shell calls them. The tests exercise edits, approval, supersession and group progress. Model generation requires configuration. |
| Session graph and group progress | PARTIAL | Nodes, goals and completion exist. Only topic prerequisites survive persistence. Benchmark evidence and typed session edges remain outstanding. |
| Smart Setup | PARTIAL | Free-text group schedule preview and direct file upload exist. Calendar events, provenance and reliable refresh remain outstanding. |
| Instructor auth, immutable approval audit | MISSING | Plan version state and approval time exist. Actor-scoped access, edit/reject events and immutable audit are absent. Keep the inherited service local/trusted. |
| Transcript review, package, grounded assistant | MISSING | No persisted workflows or corresponding API tools. The Assistant navigation entry is a placeholder. |
| Attention dashboard | PARTIAL | Group completion is available. The approvals badge is hard-coded. A reliable approvals queue, upcoming occurrences and evidence-driven alerts remain outstanding. |
| Deployment | PARTIAL | Local FastAPI/SQLite and Alembic path exists. PostgreSQL operations, production isolation, release pipeline and restore drill remain unverified. |

[Tests and limits](TEST_REPORT.md) · [Requirement-by-requirement status](REQUIREMENTS_TRACEABILITY.md) · [Gate A1](DECISIONS.md)

## Focused roadmap UI follow-up · 22 November 2026

The existing instructor shell has been retained. The serpentine roadmap now places session status, title and duration below the path line, reserves outside lanes for curved row transitions, highlights progress-aware sequential segments, and uses a legible zoom floor with horizontal scrolling on narrow viewports. The existing click-to-open session detail panel, accessible dropdowns and approval/progress APIs remain unchanged. This is a presentation update, not a fix for typed session-edge persistence or unfinished MVP features. Visual browser acceptance and the full backend suite are still required.
