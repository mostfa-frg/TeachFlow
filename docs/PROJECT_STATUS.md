# TeachFlow project status

**24 November 2026 · Ready to rehearse the single-instructor localhost demo.** The synthetic instructor workflow passes on FastAPI and SQLite, from course setup through a cited assistant answer. Verification passed 54 backend tests, 20 frontend tests and two Chromium workflows. The demo uses recorded responses. Live AI output quality remains unverified.

| Instructor capability | What has been verified |
| --- | --- |
| Setup and materials | Direct group entry and local ICS/CSV import produce editable schedules. PDF, Markdown, text and supported code files expose extraction status and located chunks. Office files and scanned PDFs give export guidance. Truncation produces a warning. |
| Roadmap | Sessions can belong to multiple topics. Six directed link types and optional notes survive draft creation, editing, approval, a fresh GET and browser refresh. The version list and diff report session and link changes, including order changes. SQLite retains the original topic dependency table. |
| Citations | Each cited material must resolve to at least one passage. The editor lets the instructor choose the passage. Session details display every cited material with its available locators. |
| Dashboard and progress | Dashboard, keyboard-accessible session list, group targets and prerequisite reminders use saved course data. Changing group changes the progress and missing prerequisites. |
| Approvals and review | The queue opens draft roadmaps, transcript findings and follow-up packages. Findings have checked evidence offsets or an explicit absence of evidence. Four individual approvals finish a package. The queue count and timestamped history reflect saved decisions. |
| Assistant | Local retrieval uses the approved plan, material chunks and the selected group's facts. Responses carry references. With no provider, the UI identifies the unavailable answer and shows the retrieved sources. |

The next instructor step is the [manual rehearsal](DEMO_WALKTHROUGH.md), including clipboard use and accessibility on the presentation machine. A live quality evaluation requires separate provider and budget approval. Optional assessments, richer history and folder synchronization belong to the later scope. [Approved scope](product/MVP_SCOPE.md) · [Decisions](DECISIONS.md) · [Current test report](TEST_REPORT.md)

The entries below describe earlier revisions. Use the table above for the current local demo.

## Historical audit · 21–22 November 2026

**Phase 00 discovery delivered for review. MVP incomplete.** The baseline, branch and inventory appear in the [audit](https://github.com/mostfa-frg/TeachFlow/blob/580fac6c9c1da89d12e5ddf7483fbbc50d380dee/docs/00_AUDIT.md). The branch fills the root instructions file and adds the audit, feasibility experiment, decision and verification records. The reconciled base already contains the canonical brief, project rules and all twelve prompts. The owner approved A1 option A on 22 November 2026. PR #5 merged at 58927ec.

| Workflow at the audited revision | Status | What an instructor can rely on |
| --- | --- | --- |
| Course, group, material and plan lifecycle | PARTIAL | Backend endpoints persist these records. The shell calls them. The tests exercise edits, approval, supersession and group progress. Model generation requires configuration. |
| Session graph and group progress | PARTIAL | Nodes, goals and completion exist. Only topic prerequisites survive persistence. Benchmark evidence and typed session edges remain outstanding. |
| Smart Setup | PARTIAL | Free-text group schedule preview and direct file upload exist. Calendar events, provenance and reliable refresh remain outstanding. |
| Instructor auth, immutable approval audit | MISSING | Plan version state and approval time exist. Actor-scoped access, edit/reject events and immutable audit are absent. Keep the inherited service local/trusted. |
| Transcript review, package, grounded assistant | MISSING | No persisted workflows or corresponding API tools. The Assistant navigation entry is a placeholder. |
| Attention dashboard | PARTIAL | Group completion is available. The approvals badge is hard-coded. A reliable approvals queue, upcoming occurrences and evidence-driven alerts remain outstanding. |
| Deployment | PARTIAL | Local FastAPI/SQLite and Alembic path exists. PostgreSQL operations, production isolation, release pipeline and restore drill remain unverified. |

[Tests and limits](TEST_REPORT.md) · [Requirement-by-requirement status](https://github.com/mostfa-frg/TeachFlow/blob/580fac6c9c1da89d12e5ddf7483fbbc50d380dee/docs/REQUIREMENTS_TRACEABILITY.md) · [Gate A1](DECISIONS.md)

## Historical roadmap UI follow-up · 22 November 2026

The existing instructor shell has been retained. The serpentine roadmap now places session status, title and duration below the path line, reserves outside lanes for curved row transitions, highlights progress-aware sequential segments, and uses a legible zoom floor with horizontal scrolling on narrow viewports. The existing click-to-open session detail panel, accessible dropdowns and approval/progress APIs remain unchanged. This is a presentation update, not a fix for typed session-edge persistence or unfinished MVP features. Visual browser acceptance and the full backend suite are still required.
