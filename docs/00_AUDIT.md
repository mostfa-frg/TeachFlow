# Phase 00 · Repository audit

**Baseline, 21 November 2026.** The source is [mostfa-frg/TeachFlow at 5a9658c](https://github.com/mostfa-frg/TeachFlow/tree/5a9658c7bd053e0952e32b8317dc5ee5aa971d97). A fresh checkout reported `## main...origin/main` with no edits before branching. The audit branch is `codex/phase-00-repository-audit`. An instructor can already save a course, approve a draft plan and record different progress for two groups. The largest release risks are lack of instructor identity, loss of session-edge semantics on save, and lack of an attributable approval history.

## Inventory at the baseline

| Location | What was present |
| --- | --- |
| Root | 30 tracked files across the tree. README, .gitignore, requirements.txt and pytest.ini at root. No tracked AGENTS.md at any level, CODEX_RULES.md, canonical brief, prompt pack, decision register, project license, dependency lock, CI workflow, deployment manifest or .env.example. The README's copy-template step therefore fails in a fresh checkout. No secret was needed for the offline audit. |
| frontend/index.html | HTML, CSS, state, SVG graph layout, DOM handlers, API client, sample data and draft recovery in one file. FastAPI serves it at the root. No JS package manifest or browser test harness. |
| backend/app | FastAPI router, Pydantic contracts, SQLAlchemy tables/sessions, environment settings, logging, document extraction and a configurable generation adapter. Route handlers also coordinate storage, SQL, provider calls and approval transactions. |
| backend/migrations | Alembic config and three ordered revisions for the foundation, legacy session ordering and per-group goal completion. SQLite local default. PostgreSQL driver declared, production behavior unverified. |
| backend/tests | Isolated SQLite API tests, mocked model responses and a legacy migration test. No browser or tenant boundary suite. |
| docs | architecture.md, data-model.md, development.md and implementation-status.md. The earlier status note lists progress controls as future work. The current shell and API already save goal indexes. |

The owner supplied the operating contract, canonical brief and twelve milestone prompts outside the baseline. This branch imports those inputs. The inherited custom shell and Groq defaults are implementation evidence. No prior product sign-off record was found in the tracked tree. Dependency ranges and the actual test environment are recorded in [the test report](TEST_REPORT.md).

## Gap matrix

Status rates the whole area against the brief. EXISTING means the named artifact or behavior is present, PARTIAL means a material requirement remains, MISSING means absent in this checkout, and UNKNOWN means evidence was unavailable. H/M/L indicate relative implementation complexity. All implementation judgments below refer to the pinned revision.

| Area | Status | Evidence and material gap | Complexity | Depends on | Main risk |
| --- | --- | --- | --- | --- | --- |
| 1. Product/business | PARTIAL | README.md and brief §§1–3 agree on instructor-only planning. Staffing, spend, target installation and demo owner remain unknown. | M | Owner decisions | Six-week scope exceeds capacity |
| 2. Requirements | PARTIAL | Brief §§5,11 sets P0 and nine demo outcomes. Earlier docs/implementation-status.md lacks acceptance links. This PR supplies the first traceability baseline. | M | Phase 01 sign-off | Objective ticks mistaken for benchmarks |
| 3. UI | PARTIAL | frontend/index.html renders a wizard, SVG session nodes, detail panel and group selector. List, Approvals and Assistant controls lead to a prototype notice. | M | A1 and session contract | Visible controls suggest unavailable workflows |
| 4. UX | PARTIAL | safeLoad, extractSchedule and toggleGoal support recovery, preview and rollback. Setup still needs forms. Group selector replaces the specified sidebar. Keyboard-complete graph alternative, stale states and approval diffs lack acceptance evidence. | H | Personas, errors, data contracts | A keyboard user cannot use the advertised List tab |
| 5. System architecture | PARTIAL | backend/app/main.py, db.py and services.py form a modular monolith. Synchronous upload/generation and a large api/v1/router.py couple orchestration to requests. Job recovery, request correlation and production operations remain open. | M | Hosting, privacy and workload | Timeouts or partial processing under load |
| 6. Frontend | PARTIAL | apiRequest, hydrateApiCourse, approve and toggleGoal use the API. proposalForSave collapses session edges. Draft state in localStorage lacks identity scoping. | H | A1, auth, graph endpoints | Reload changes instructor intent |
| 7. Backend | PARTIAL | api/v1/router.py implements course/group/material, plan lifecycle and progress endpoints. Authentication and owner checks, reviews, packages, audit and grounded queries are missing. | H | Tenancy, schema | Course data exposed across instructors |
| 8. Data model | PARTIAL | models.py has shared versions and per-group progress. TeachingSession has one topic_id. TopicDependency carries topic prerequisites. Missing session-topic join, typed session edges, group meeting instances, benchmark evidence and approval events. | H | Migration strategy | Migrating approved plans breaks identifiers/history |
| 9. Business rules | PARTIAL | validate_roadmap checks references/cycles. approve_roadmap supersedes versions and carries compatible progress. No shared edit/reject/approve history with actor, or evidence-driven benchmark lifecycle. | H | Identity and audit model | An edited proposal cannot be reconstructed |
| 10. AI | PARTIAL | services.py and generation route validate a provider proposal and constrain material context. No Instructor Agent, cited retrieval, transcript review, package workflow, quality evaluations or cost ledger. | H | Approved provider, provenance | Unsupported facts appear authoritative |
| 11. Document processing | PARTIAL | extract_document and upload_material handle text-based PDF, TXT and Markdown with outcomes and byte limits. No Office/code adapters, version hashes, page/chunk locators or idempotent refresh. | H | Format policy, storage | Duplicate imports or untraceable citations |
| 12. Integrations | PARTIAL | Configurable model HTTP adapter and local uploads exist. No calendar import/sync, OAuth lifecycle or external folder adapter. extractSchedule accepts free text. Live provider compatibility is UNKNOWN. | H | Calendar/provider scopes | Consent and provider setup delay initial import |

## Smallest six-week P0 sequence for approval

These are proposed delivery windows. The numbered prompts still govern execution and their respective gates.

| Week / prompts | Vertical slice and demonstration | Cut line |
| --- | --- | --- |
| 1 · 00–04 | Settle A1 and subsequent scope, UX and architecture gates. Establish instructor identity, owner-scoped course read/write and CI. Preserve the working approval/progress flow. Exercise two instructors, a legacy plan and representative imports before broad schema changes. | Time-box provider feasibility to one working day per integration. If access is unavailable, use synthetic calendar/material samples. Keep isolation mandatory. |
| 2 · 05–06 | Import a calendar plus selected files, show provenance and failures, produce one editable roadmap proposal and activate it only on approval. Introduce session-topic and typed session-edge mappings with legacy round-trip tests. | By end of week 2, use ICS or calendar CSV plus manual upload/refresh if OAuth or continuous sync is unproven. Provide one-line setup and explicit manual drafting without a model key. |
| 3 · 06–07 | Show the same approved graph and equivalent list for two groups. Open session details, update group-specific benchmark evidence and surface an unmet prerequisite in the dashboard. | Use deterministic alerts from approved facts. Defer cosmetic graph polish and optional automation. |
| 4 · 08 | Upload a synthetic timestamped transcript, inspect per-objective coverage, correct a finding and record approval. Verify insufficient evidence and group privacy. | Start with text. Defer audio unless consent, retention and provider limits are approved and tested. |
| 5 · 08–09 | From reviewed evidence draft the summary, recap, homework, group message and unresolved questions. Edit/approve once. Ask one Instructor Agent for a sourced passage and current group state. | Use relational queries and document search first. Defer vector search unless retrieval evaluations justify it. |
| 6 · 10 | Replay setup through audit with two instructors and groups. Verify accessibility, retries, authorization, production migrations, backup/restore and the approved deployment path. | Defer all P1. Escalate a threatened P0 before cutting acceptance criteria or declaring release readiness. |

See the [risk register](RISKS.md), [source-linked UI comparison](architecture/UI_BASE_SPIKE.md), and [decisions awaiting the owner](DECISIONS.md).
