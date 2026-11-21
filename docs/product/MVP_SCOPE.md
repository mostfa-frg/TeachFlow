# Approved local TeachFlow presentation scope

**Decision D1 (22 November 2026).** Build a **single-user, local working app** with the existing FastAPI/SQLite backend and TeachFlow UI. Use synthetic/non-sensitive demonstration content. **Authentication, ownership/tenant isolation, admin roles, hosting, deployment, CI/CD, PostgreSQL operations and production backups are not required.** Never expose the unauthenticated service publicly.

## What must work for the demonstration (P0)

1. **Smart Setup:** create course and groups, editable schedules, ICS/CSV calendar import or direct manual fallback.
2. **Materials:** upload/extract documents and code with status, references and an understandable unsupported-file fallback.
3. **Roadmap:** generate a real AI proposal when configured, edit sessions and graph links, save/reload all directed typed relationships, approve explicitly.
4. **Instructor UI:** functioning dashboard, serpentine graph, equivalent session list, progress view, material view and approvals navigation.
5. **Group progress:** separate objectives/benchmarks for two groups, clear status and actionable dependency reminders.
6. **Review:** upload synthetic transcript text and evaluate observed session coverage with source snippets, edit/approve findings.
7. **Follow-up package:** edit/approve recap, homework/activity, summary and group message; copy manually, no automatic external sending.
8. **Instructor Assistant:** grounded Q&A over course plans, material text and current group facts, with references and safe insufficient-evidence handling.
9. **Verification:** all P0 flows work in a repeatable localhost walkthrough using example data; relevant automated regression tests pass and missing-provider behavior is truthful.

**Simple local approval history** is enough; an immutable production audit service is not required. Use a clearly labeled manual drafting fallback when AI credentials are absent, not simulated AI output.

**P1 (later):** assessment drafts, richer history, optional GitHub links, automatic folder synchronization, FAQ drafts. **Out of scope:** student portals, live meeting bots, autonomous grading, public deployment, account management and production operations.

## Local demo acceptance

Start FastAPI on `127.0.0.1:8000` with SQLite. Create one course and two groups; import calendar/materials; generate/edit/approve a saved roadmap; reload and inspect exact session relationships; update different group progress; review a synthetic transcript; approve follow-up content; ask the Instructor Assistant for a cited answer. Verify empty/error/retry states and persisted progress after refresh. **No login, ownership checks, hosting, multi-user test or deployment drill.**
