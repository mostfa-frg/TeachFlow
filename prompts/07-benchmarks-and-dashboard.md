# PROMPT 07 — Benchmarks, per-group progress, dashboard and reminders

Implement P0 instructor operational workflow using live DB and approved plan (not placeholder widgets).

- Proposed benchmarks come from session objectives/materials and remain untrusted until approved. Each benchmark has measurable definition, evidence type, due condition, source/plan version and state. Define explicit transitions (not started / in progress / met / needs attention / waived / unknown or approved variants), who can change them, override reason and audit trail.
- Model group-specific evidence and statuses independently of the shared session/topic graph. Calculate group/session progress transparently from approved benchmarks and attended/completed sessions, with documented denominator and behavior for not-yet-scheduled, waived, unknown, extra or canceled sessions. Avoid a single opaque "Course Health Score".
- Show actionable dashboard: upcoming sessions, prerequisite gaps, delayed groups, failed imports/reviews, pending approvals; filter by course/group and link to exact action. Add lightweight context-sensitive reminders from dependencies, not a complex automation engine. No external notifications/sends unless separately approved.
- Data services: aggregate efficiently without N+1 queries, use pagination and indexes, cache invalidation on plan/progress changes, UTC+instructor timezone, accurate same-session cross-group isolation. Recompute upon relevant approved edits (idempotent).
- UX: dashboard skeleton, empty no-groups/no-approvals, stale data, progress recalculation, retry, accessibility including screen reader labels.
- Test tricky cases: group A changes must not affect B; overdue/blocked logic around reschedules, ambiguous unknown, deleted benchmarks, approval rejection, cross-tenant access, no double-count on refresh, transparent numbers and deterministic alerts.

Update docs, demo two groups at different progress levels, run checks, stop at checkpoint report.
