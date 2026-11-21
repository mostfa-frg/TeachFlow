# Decision register

**22 November 2026 · Owner approved A1 option A.** The owner authorized Phase 00, a milestone branch, a push and a PR to main. The supplied rules and brief establish instructor-only use, a session graph, shared plans with group-specific evidence, one agent and human approval of generated changes. The baseline's technology selections describe current code. They do not authorize new providers, spending, data transfers or migration.

## A1 · Approved UI base

**Question.** Which frontend should later milestones use?

**Why now.** UX work and acceptance criteria depend on whether to extend working screen/API integrations or rebuild them.

- **A. Extend the current instructor shell and FastAPI backend.** Lowest near-term rework. Keep the working wizard, session detail and progress interactions. Consolidate tested UI functions incrementally. Identity, session-edge persistence and accessibility still need work. Low–medium integration risk.
- **B. Adopt Frappe Learning as the UI base.** Reuse roles, course authoring and batch scheduling. Budget for learner-flow restrictions, license review, DocType extensions, identity integration and additional operations. High integration risk.
- **C. Build a new custom React/TypeScript shell over the existing API.** More structure for complex screens, with a new build chain and parity work for every replaced workflow. Medium–high integration risk.

**Recommendation.** A. The existing shell is already instructor-oriented and exercises real endpoints. The [spike](architecture/UI_BASE_SPIKE.md) identifies a backend graph mismatch shared by all three choices.

**Owner decision, 22 November 2026.** `APPROVE A1: A`. Extend the existing instructor UI and FastAPI backend under these requirements.

1. Preserve working functionality and existing APIs.
2. Keep the current frontend. A full rewrite and migration to Frappe Learning are outside this approval.
3. Extract focused frontend modules during relevant milestones and keep additional complexity out of the monolithic HTML file.
4. Keep the API and rendering layers separate so React/TypeScript remains an option if maintainability and complexity justify it.
5. Prioritize the session-edge persistence defect. Preserve both endpoints, direction and relationship type through saving, loading, editing and approval.
6. Support session-to-session relationships, many-to-many session/topic membership and group-specific progress on shared plans.
7. Maintain accessibility, responsive behavior and comprehensive loading and error states.
8. Preserve all existing tests and add regression coverage for identified defects, including the complete session-edge round trip.

**Milestone gate.** Begin Phase 01 only after the owner merges PR #5 into main. Use a fresh milestone branch from merged main, open a separate PR and follow the remaining approval gates.

## Later decisions

| When needed | Owner decision and bounded default proposed for discussion |
| --- | --- |
| Phase 01, scope gate | Confirm team availability, six-week target/demo audience, budget ceiling and P0 acceptance, including Office/legacy format expectations. Escalate any P0 trade-off. |
| Phase 02, UX gate | Confirm setup/review journey, group navigation, keyboard list, failure/recovery and minimal mobile flow. |
| Phase 03, before auth/schema work | Approve instructor identity source, optional admin power and tenant boundary. Agree ownership and migration/backfill for existing unowned courses. |
| Phase 03, before deployment/storage design | Confirm local demo vs managed or self-hosted target, region, database, backups, storage, encryption, retention/deletion and access to transcript evidence. |
| Before calendar integration | Select provider, scopes and token lifecycle if OAuth is required. Prefer ICS/CSV import and explicit refresh for the first demo. |
| Before external AI calls or sensitive uploads | Choose provider, eligible content, residency, model, per-run/monthly budget, logging and fallback. Existing Groq configuration is historical. No paid selection or live calls in Phase 00. |
| Before audio intake/transcription | Approve consent, retention, deletion, access and any third-party processor. Use synthetic uploaded transcript text for the first evaluation. |
| Before migration/release | Approve destructive changes separately, if any. Confirm license/distribution intent, deployment target, release criteria and rollback/restore owner. |
