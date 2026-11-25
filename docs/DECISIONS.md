# Decision register

**22 November 2026 · Owner approved A1 option A.** The owner authorized Phase 00, a milestone branch, a push and a PR to main. The supplied rules and brief establish instructor-only use, a session graph, shared plans with group-specific evidence, one agent and human approval of generated changes. The baseline's technology selections describe current code. They do not authorize new providers, spending, data transfers or migration.

## A1 · Approved UI base

**Question.** Which frontend should later milestones use?

**Why now.** UX work and acceptance criteria depend on whether to extend working screen/API integrations or rebuild them.

- **A. Extend the current instructor shell and FastAPI backend.** Lowest near-term rework. Keep the working wizard, session detail and progress interactions. Consolidate tested UI functions incrementally. Identity, session-edge persistence and accessibility still need work. Low–medium integration risk.
- **B. Adopt Frappe Learning as the UI base.** Reuse roles, course authoring and batch scheduling. Budget for learner-flow restrictions, license review, DocType extensions, identity integration and additional operations. High integration risk.
- **C. Build a new custom React/TypeScript shell over the existing API.** More structure for complex screens, with a new build chain and parity work for every replaced workflow. Medium–high integration risk.

**Recommendation.** A. The existing shell is already instructor-oriented and exercises real endpoints. The [spike](https://github.com/mostfa-frg/TeachFlow/blob/580fac6c9c1da89d12e5ddf7483fbbc50d380dee/docs/architecture/UI_BASE_SPIKE.md) identifies a backend graph mismatch shared by all three choices.

**Owner decision, 22 November 2026.** `APPROVE A1: A`. Extend the existing instructor UI and FastAPI backend under these requirements.

1. Preserve working functionality and existing APIs.
2. Keep the current frontend. A full rewrite and migration to Frappe Learning are outside this approval.
3. Extract focused frontend modules during relevant milestones and keep additional complexity out of the monolithic HTML file.
4. Keep the API and rendering layers separate so React/TypeScript remains an option if maintainability and complexity justify it.
5. Prioritize the session-edge persistence defect. Preserve both endpoints, direction and relationship type through saving, loading, editing and approval.
6. Support session-to-session relationships, many-to-many session/topic membership and group-specific progress on shared plans.
7. Maintain accessibility, responsive behavior and comprehensive loading and error states.
8. Preserve all existing tests and add regression coverage for identified defects, including the complete session-edge round trip.

**Workflow amendment, 22 November 2026.** PR #5 merged at 58927ec. The owner superseded milestone branches and PRs with small verified commits pushed directly to main under AGENTS.md. Phase 01 is authorized. Phase 02 requires B1 approval. All A1 engineering requirements remain in effect.

## D1 — Owner-approved local-demo scope (22 November 2026)

TeachFlow is a **single-user local presentation application** using the existing instructor UI, FastAPI and SQLite. This decision supersedes older P0 requirements, milestone prompts, and historical audit statements that require authentication, owner/tenant isolation, admin accounts, hosting, public deployment, CI/CD, production backups, or production infrastructure. **Do not implement or block on those features.**

The completion goal is a convincing working local demo: create course/groups, import schedule and materials, generate/edit/approve a roadmap that saves relationships intact, show group-specific progress and benchmarks, navigate functional dashboard/list/materials/approvals, review a synthetic transcript, approve a post-session package, and ask the grounded Instructor Assistant questions. Keep human approval and small reversible commits.

Local safeguards still apply: keep the app on localhost; synthetic/non-sensitive demo content; no hard-coded/committed secrets; basic file validation; clear failures and honest AI fallback. Any new paid external provider or sending of sensitive recording data still requires approval.

**Acceptance replacement:** TF-01 (authentication and ownership) is OUT OF SCOPE. TF-13 is a repeatable **localhost end-to-end demonstration**, not production deployment. Simple local approval/version records suffice; no enterprise audit subsystem required.

## Later decisions

| When needed | Owner decision and bounded default proposed for discussion |
| --- | --- |
| Phase 01, scope gate | Confirm team availability, six-week target/demo audience, budget ceiling and P0 acceptance, including Office/legacy format expectations. Escalate any P0 trade-off. |
| Phase 02, UX gate | Confirm setup/review journey, group navigation, keyboard list, failure/recovery and minimal mobile flow. |
| Phase 03, before schema work | No authentication or ownership work per D1. Approve only destructive or broad graph-data changes. |
| Phase 03, storage | Local SQLite and local files only; no hosting/deployment decision. Ask before using real recordings or new external processing providers. |
| Before calendar integration | Select provider, scopes and token lifecycle if OAuth is required. Prefer ICS/CSV import and explicit refresh for the first demo. |
| Before external AI calls or sensitive uploads | Choose provider, eligible content, residency, model, per-run/monthly budget, logging and fallback. Existing Groq configuration is historical. No paid selection or live calls in Phase 00. |
| Before audio intake/transcription | Approve consent, retention, deletion, access and any third-party processor. Use synthetic uploaded transcript text for the first evaluation. |
| Before final presentation | Approve destructive changes separately, if any; test the localhost walkthrough with synthetic fixtures and report honest limitations. |

## B1 · Product baseline proposed for approval

Approve an instructor teaching multiple groups as the pilot user, the [P0 boundary and fallback modes](product/MVP_SCOPE.md), and a private local pilot using synthetic inputs? Option A adopts this baseline and validates the proposed metrics during the pilot. Option B requests specific revisions. Secure deployment remains a release criterion. Provider selection, hosting, consent and spending stay at their later gates. Phase 02 awaits the owner's decision.

## B1 approved · 24 November 2026

The owner approved option A and the six implementation priorities for the D1 local demo.
Keep the six relationship labels in the brief. Prerequisite and depends_on point from
required session to dependent session and share a cycle check. Reinforces, extends,
introduces and applies point from acting session to referenced session. Optional notes
describe the link. An empty explicit link list is meaningful. Older proposals without
a link list inherit within-topic sequence and last-to-first topic prerequisites.
Historical data cannot reconstruct links lost before this change. Keep topic_dependencies
for older clients. A later removal would require a separate owner decision.
