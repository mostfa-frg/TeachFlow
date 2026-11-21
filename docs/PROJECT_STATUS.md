# Project status · Phase 00

**Phase 00 discovery delivered for review. MVP incomplete.** The baseline, branch and inventory appear in the [audit](00_AUDIT.md). The deliverable is the audit, feasibility experiment, decision record, prompt pack and repository instructions. A1 awaits the owner.

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
