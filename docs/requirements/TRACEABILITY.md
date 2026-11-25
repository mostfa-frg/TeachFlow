# P0 requirements and verification catalogue

Under scope decision D1, TF-01 (authentication/ownership) is out of scope and TF-13 is replaced with a localhost end-to-end demo; the original acceptance text remains as historical planning where explicitly labeled. This indexed catalogue combines functional requirements, stories, business rules, acceptance criteria and traceability. Each row links the Phase 00 TF identifier to the detailed case below. Planned checks describe future implementation acceptance. Current evidence remains in the [baseline](https://github.com/mostfa-frg/TeachFlow/blob/580fac6c9c1da89d12e5ddf7483fbbc50d380dee/docs/REQUIREMENTS_TRACEABILITY.md).

| Baseline | Requirement / story / acceptance | Phase | Test type |
| --- | --- | --- | --- |
| TF-01 | [Historical access requirement — out of scope D1](#case-001) | — | Not a local-demo acceptance gate |
| TF-02 | [TF-FR-002 · TF-US-002 · TF-AC-002](#case-002) | 05 | Importer integration |
| TF-03 | [TF-FR-003 · TF-US-003 · TF-AC-003](#case-003) | 05 | Parser fixtures + integration |
| TF-04 | [TF-FR-004 · TF-US-004 · TF-AC-004](#case-004) | 06 | API + browser |
| TF-05 | [TF-FR-005 · TF-US-005 · TF-AC-005](#case-005) | 06 | Legacy migration + round-trip regression |
| TF-06 | [TF-FR-006 · TF-US-006 · TF-AC-006](#case-006) | 06 | Browser + accessibility |
| TF-07 | [TF-FR-007 · TF-US-007 · TF-AC-007](#case-007) | 07 | Domain + API |
| TF-08 | [TF-FR-008 · TF-US-008 · TF-AC-008](#case-008) | 08 | Evidence evaluation + integration |
| TF-09 | [TF-FR-009 · TF-US-009 · TF-AC-009](#case-009) | 08 | Workflow integration |
| TF-10 | [TF-FR-010 · TF-US-010 · TF-AC-010](#case-010) | 09 | Tool contracts + evaluation |
| TF-11 | [TF-FR-011 · TF-US-011 · TF-AC-011](#case-011) | 07 | Query integration + browser |
| TF-12 | [TF-FR-012 · TF-US-012 · TF-AC-012](#case-012) | 06–09 | Transaction + concurrency |
| TF-13 | [Local demo replacement](#case-013) | Final | Repeatable localhost E2E |

<a id="case-001"></a>

## Access — historical and OUT OF SCOPE under D1

Do not implement or test the original login/ownership requirements for this local single-user demo.


**TF-FR-001.** Restrict every course read, file, search, job and mutation to the authorized owner. Limit optional admin actions to approved configuration.

**TF-US-001.** As an instructor, I want to open my courses privately.

**TF-AC-001.** Given two authenticated owners, when one opens their course, then only their data appears.

Given an expired session or another owner’s identifier, when any read or write is attempted, then disclose no data and change no state. Given a configuration-only admin, when opening course content, then deny access.

<a id="case-002"></a>

## Calendar setup

**TF-FR-002.** Preview group schedules and time zones from calendar input, with editable fallback.

**TF-US-002.** As an instructor, I want to reuse my timetable.

**TF-AC-002.** Given recurring events for two groups, when I import and confirm group mappings, then dated occurrences appear under the intended groups.

Given the same calendar, when refreshed twice, then occurrences retain identity. Given an ambiguous time or missing file, when previewing, then flag it and offer correction or one-line setup. Cancelling preview leaves no confirmed schedule.

<a id="case-003"></a>

## Materials

**TF-FR-003.** Extract scoped sources with revision hashes, locators and per-file outcomes.

**TF-US-003.** As an instructor, I want to import a mixed folder once.

**TF-AC-003.** Given a PDF, deck, document, code and a corrupt file, when I upload them together, then successful items expose locatable text and the failed item has a reason and retry.

Given an ongoing batch, when reopened, then show individual processing states. Reimporting identical bytes adds no revision. Changed bytes create a new revision. Empty/oversize files produce actionable errors. Cancelling pending work never alters an approved plan.

<a id="case-004"></a>

## Plan drafting

**TF-FR-004.** Generate one editable draft with proposed objectives and provenance from selected inputs.

**TF-US-004.** As an instructor, I want to review the plan once.

**TF-AC-004.** Given a processed source and schedule, when I generate, edit and submit one proposal, then the draft stays inactive until my explicit approval.

Given duplicate requests, when retried, then return one proposal. Given a provider failure or missing key, when generation ends, then show retry or labeled manual drafting. Cancelling generation or review leaves the approved version active.

<a id="case-005"></a>

## Graph persistence

**TF-FR-005.** Persist directed typed session edges and many-to-many topic membership independently of display order.

**TF-US-005.** As an instructor, I want to keep exact session relationships.

**TF-AC-005.** Given three sessions, two sharing a topic and one linked to two topics, when I save three distinct edges, reload, edit one type, approve and reload again, then compare endpoint IDs, directions, types and topic memberships at each step; only my explicit edit changes.

Given dangling or cross-course endpoints or a hard prerequisite cycle, when saving, then reject atomically. Duplicate identical edges add nothing. Cancelling an edit retains the previous graph. Existing plans and API clients remain readable.

<a id="case-006"></a>

## Session detail

**TF-FR-006.** Offer a group sidebar, session-node graph and equivalent keyboard list with detail and editing.

**TF-US-006.** As an instructor, I want to prepare a session from either view.

**TF-AC-006.** Given an approved session with objectives, related sessions and source links, when I open it from graph and list, then both show identical plan, relationships, materials and group context.

Given an empty group or missing source, when opening details, then explain the gap. Given a slow or failed read, when navigating, then show loading or retry without displaying the prior group as current.

<a id="case-007"></a>

## Benchmarks

**TF-FR-007.** Suggest benchmarks from objectives as proposals and track completion with evidence per group occurrence.

**TF-US-007.** As an instructor, I want to see which group met an objective.

**TF-AC-007.** Given two groups share one approved session, when I approve a benchmark and record Saturday’s evidence, then Monday retains its prior state and both keep the same plan.

Given no evidence, when viewing status, then show unknown. Duplicate evidence submissions count once. Given a rejected suggestion or mismatched occurrence, when saving, then no benchmark progress changes.

<a id="case-008"></a>

## Coverage review

**TF-FR-008.** Compare uploaded transcript evidence to planned objectives and benchmarks, including unanswered questions.

**TF-US-008.** As an instructor, I want to correct an evidence-backed review.

**TF-AC-008.** Given a synthetic transcript with a timestamped partial explanation, when I request a review, then the draft distinguishes coverage levels and cites the passage for the proposed finding.

Given an empty transcript or absent timestamps, when reviewing, then report insufficient evidence or cite snippet offsets. Given a processing failure, when retried, then retain a single draft for the same request. Rejection or cancellation does not change progress.

<a id="case-009"></a>

## Package

**TF-FR-009.** Draft summary, recap, homework, message and unresolved items from approved review evidence.

**TF-US-009.** As an instructor, I want to prepare follow-up for one group.

**TF-AC-009.** Given an approved review, when I generate and edit its package, then a single approval records the edited version for manual use.

Given no approved review, when drafting, then identify the prerequisite. Given duplicate approval, rejection, cancellation or provider failure, then never send externally or apply partial text.

<a id="case-010"></a>

## Instructor Agent

**TF-FR-010.** Use one orchestrator with scoped course context, upcoming sessions, session details, group progress, benchmarks, related sessions and material search tools.

**TF-US-010.** As an instructor, I want to ask what to teach next and why.

**TF-AC-010.** Given a scheduled session and a source passage, when I ask for its date and supporting explanation, then the answer uses structured schedule data and a verifiable material citation.

Given insufficient evidence, when asked a factual question, then abstain. Given instructions embedded in material, then treat them as data. A requested change produces only a proposal. Failed retrieval exposes uncertainty and retry.

<a id="case-011"></a>

## Dashboard

**TF-FR-011.** Show upcoming sessions, pending decisions and explainable prerequisite or schedule alerts.

**TF-US-011.** As an instructor, I want to manage by exception.

**TF-AC-011.** Given a due session with an incomplete prerequisite in one group, when I open the dashboard, then the alert names the evidence, group and session and links to the relevant action.

Given no exceptions, when the dashboard loads, then show an empty queue. Duplicate triggers yield one current alert. Failed refresh shows stale status and retry. Reminders never reschedule a class.

<a id="case-012"></a>

## Approval history

**TF-FR-012.** Apply authoritative changes only through an attributable decision on a specific proposal revision.

**TF-US-012.** As an instructor, I want to inspect exactly what I approved.

**TF-AC-012.** Given a draft and a prior approved version, when I review a diff and approve the edited revision, then activation and immutable actor/time/version/decision evidence are recorded together.

Given stale edits, when approving, then require renewed review. Duplicate approvals produce one effect. Rejection records the decision. Cancellation keeps the draft, and a failed transaction leaves the prior version active.

<a id="case-013"></a>

## Local end-to-end demo (TF-13 replaced by D1)

**TF-FR-013.** Demonstrate the core instructor workflow locally using FastAPI and SQLite.

**TF-US-013.** As a project evaluator, I can start the app and complete course, import, roadmap, approval, progress, review and assistant tasks without signing in.

**TF-AC-013.** A reproducible synthetic localhost demonstration completes all P0 interactions, preserves graph and group state across reloads, and provides clear errors/manual fallback when external AI is unavailable. No hosted deployment, two-owner isolation or production backup/restore is required.

## Cross-cutting acceptance

Apply TF-NFR-001 to every story. For every write, repeat the request after a simulated disconnect and check for duplicate effects. For each long-running operation, cover pending, partial, cancelled and failed states. If completion races cancellation, show the actual terminal outcome. A disconnected client must reconcile before retrying.

| ID | Requirement and verification |
| --- | --- |
| TF-NFR-001 | D1 local replacement: keep localhost access and synthetic demo data; do not commit secrets. No identity/tenant tests. |
| TF-NFR-002 | Complete setup, graph/list editing, review and approval by keyboard, with visible focus, named controls, announced errors and text equivalents for color. At 320 CSS pixels verify access to all actions and readable detail. |
| TF-NFR-003 | Measure p95 reads and import reliability on the [pilot fixture](../product/SUCCESS_METRICS.md). Display loading, empty, partial, stale, offline and retry feedback wherever applicable. |
| TF-NFR-004 | Bound upload bytes and parsing resources. Exercise invalid content, path-like filenames and interrupted imports. Keep supported originals versioned under the approved retention policy. |
| TF-NFR-005 | Enforce schema validation, scoped tool access, source checks, bounded retries and approved spending limits. With the provider unavailable, verify no fabricated success or irreversible action. |
| TF-NFR-006 | Re-run local SQLite/API and frontend tests; validate the complete localhost demonstration and preserve existing API behavior. No hosted restore/deployment requirement. |

## Business rules and glossary

- **TF-BR-001.** A course is an owner-scoped shared plan. A group is a cohort taking that plan. A session template is its reusable instructional node. An occurrence is that node scheduled for one group at a specific time. Editing group evidence affects only that group.
- **TF-BR-002.** A topic is a concept linked to any number of sessions. An objective is an intended learning outcome. A benchmark is an observable criterion for an objective. Checking off a goal alone supplies no evidence of mastery.
- **TF-BR-003.** Proposed edge convention: store prerequisite → dependent for hard dependencies and reject cycles in their combined subgraph. For descriptive links such as reinforces, store acting session → referenced session and allow reciprocal links. Persist type and direction explicitly. Confirm relation labels during UX review.
- **TF-BR-004.** A material is an imported artifact. A source points to its exact revision and page, slide, timestamp or offset. Observed coverage describes transcript evidence as covered, partial, not observed or insufficient evidence. Distinguish absent mention in a usable transcript from an unusable or incomplete transcript.
- **TF-BR-005.** A proposal is editable suggested content with a revision. Approval is an explicit instructor decision on that revision. A version identifies an approved snapshot. The audit records immutable proposal, edit, reject and approve events with actor and time. All consequential AI outputs follow this lifecycle.
- **TF-BR-006.** Optional admin privileges cover approved installation operations. Access to course evidence requires explicit authorization. Retention length, consent, deployment topology, cost caps and identity provider stay at their respective gates.
