# TeachFlow — Codex Operating Contract

Read this document and `reference/TeachFlow_Project_Brief.md` before starting any phase. If the source files are in a different path, locate them; if missing, STOP and request the brief. This contract is persistent across every milestone.

## ACTIVE OVERRIDE — D1 local demo (owner-approved 22 November 2026)

This is a single-user local presentation application. No authentication, account management, roles, tenant/owner isolation, hosted deployment, public release, production CI/CD, cloud backup/restore, or infrastructure hardening. These are **not P0** and must not block work. This override supersedes conflicting P0 definitions, architecture/security requirements, approval gates and milestone prompts below; retain them only as historical planning context. Build on the existing HTML/CSS/JS, FastAPI and SQLite. P0 now means a complete local course → import → roadmap → approval → group progress → synthetic transcript review → post-session package → grounded Instructor Agent walkthrough, including functional UI/navigation and honest retry/failure states. A lightweight local approval log is sufficient. Keep localhost-only use and basic safeguards: upload validation, no secrets in Git, no fabricated AI success, and no sensitive user recordings. External paid/recording providers still require approval.

## Mission and non-negotiable product rules
Build a **working six-week MVP** of TeachFlow, an AI-powered **instructor-only** course planning and management product. Its promise is: **Connect calendar → select/import materials → wait for processing → review one proposed plan → approve → manage by exception.** Instructors and optional admins only; no student login, messaging portal, or student-facing LMS. Use sessions as nodes in an editable **graph**, not only a linear timeline. Topics-to-sessions are many-to-many. A course plan may be shared across groups while schedule, benchmark evidence, and progress are group-specific. Never silently apply AI suggestions: roadmap plans, benchmarks, reviews, post-session packages and other consequential generated changes are **proposals** requiring human review/approval. Never auto-send messages or auto-reschedule classes. Use **one** Instructor Agent plus deterministic tools, not an unneeded multi-agent swarm. Prioritize practical file/calendar imports and uploaded transcripts. Live meeting bots, autonomous grading, student accounts and expansive integrations are P2 (out of scope).

## Priority semantics
- P0 = local end-to-end presentation: smart setup with schedule/material import and manual fallbacks; correct session graph and approval; per-group benchmarks/progress; functional instructor screens; synthetic transcript-text review and cited findings; approved follow-up package; grounded Instructor Agent; repeatable localhost demo. See D1 override; auth, ownership, enterprise audit and hosted deployment are excluded.
- P1 only after P0 passes: small assessment drafts, read-only version history, read-only GitHub links, FAQ drafts. Feature-flag and isolate.
- P2 not built: student portal, live meeting bot, automatic external delivery, autonomous grading, composite health score, cross-course analytics, broad integrations, fully automatic adaptive scheduling.
- Six-week delivery is a *scope constraint*, not a promise of labor/time estimates. Reduce P1 and nonessential automation first. Do not disguise missing P0 as complete.

## How to work in the repository
Follow the direct-to-main Git workflow in AGENTS.md for each authorized milestone. Git authorization does not change product, security, privacy, architecture, cost or migration gates.

1. Inspect `git status`, all `AGENTS.md` instructions, directory tree, manifests, README, env examples, schemas/migrations, tests, CI, existing components, and current working features. Avoid conflicting with unstaged user changes; do not delete/overwrite work without approval. Never rewrite the repository merely for stylistic preference.
2. Compare implemented behavior to canonical brief. Mark facts **EXISTING / PARTIAL / MISSING / UNKNOWN** with file paths and reproducible evidence.
3. Work on the current approved milestone **only**. Finish that milestone's code, docs, tests, and verification; stop at its gate and ask for the next prompt. No fake implementations, fictitious API calls, misleading UI success messages, or mock data presented as live. Demo/test fixtures must be labeled.
4. Prefer modular monolith and small vertical slices over microservices. Preserve separation of concerns: HTTP handlers thin; services/domain logic; repository/data access; adapters; background jobs; AI workflows; frontend components/views/data hooks; shared schemas/contracts.
5. Maintain: `docs/PROJECT_STATUS.md` (done vs missing), `docs/DECISIONS.md` (ADRs plus user approvals), `docs/REQUIREMENTS_TRACEABILITY.md` (requirement → implementation → test → status), `docs/RISKS.md`, `docs/TEST_REPORT.md`, and `docs/README.md` index. Create on first phase; update each phase. Record known limitations without hiding them.
6. After changes run applicable lint, type-check, formatting validation, unit/integration/e2e tests, migrations checks, accessibility checks and security checks. State exact commands and pass/fail; do not claim a check passed if not run. If tools/API keys unavailable, isolate the blocker and run offline contract tests with clearly flagged stubs.
7. Use realistic seed data for a Python course with multiple groups and sessions, plus test files and a synthetic transcript; never commit actual personal/recording data. Keep integration tests deterministic and repeatable.
8. Secrets only in environment/secret storage, never source or logs. No destructive DB migration, auth strategy switch, hosted deployment, billable service, paid API selection, external network upload of potentially sensitive files, or mass refactor without explicit approval.
9. Source hierarchy: approved `docs/DECISIONS.md` entries > canonical brief (for unmodified original expectations) > approved requirements > repo code. Surface conflicts instead of guessing.

## Mandatory decision gates — STOP and ask user
Stop **before implementing** any irreversible/expensive/risky choice, notably: (A) Frappe Learning reuse versus custom React-based shell; (B) scope changes to P0 or product model; (C) auth/tenant isolation, data residency, hosting, file storage/retention, provider OAuth scopes, vendor choice or paid AI/transcription limits; (D) any recorded-session storage or third-party transcription without explicit consent/privacy design; (E) any broad rewrite or destructive migration; (F) scope/quality tradeoff that would miss a P0 acceptance criterion. If a noncritical decision is reversible, choose the simplest coherent default, record the assumption and proceed.

When blocked, output EXACTLY this structure, then **STOP**:

```
DECISION REQUIRED — <ID>: <one-sentence question>
Why now: <the concrete implementation blocker>
Options:
A. <option> — UX / implementation / cost / security / time tradeoffs
B. <option> — UX / implementation / cost / security / time tradeoffs
[Optional C]
Recommendation: <one option + rationale>
What I can complete without this decision: <bounded tasks>
Reply with: "APPROVE <ID>: <A|B|C>" or your alternative.
```

At the end of *every* milestone output:
```
MILESTONE <number> STATUS: PASS | BLOCKED | PARTIAL
Implemented: <paths and behaviors>
Documentation: <paths>
Verified: <exact commands/results>
Requirements covered: <IDs>
Known gaps / risks: <concrete list>
Decisions needing user approval: <IDs or None>
Next prompt: <number and file>
```
Stop after reporting, unless the current prompt expressly authorizes the next phase. Do not give a completion claim for the entire project until end-to-end criteria pass.

## Architecture engineering guardrails
- Time-box a Frappe Learning feasibility spike; it is a **candidate**, not an approved dependency. If not suitable, choose simple instructor-first UI. A possible custom default *after approval*: React + TypeScript + Vite, React Router, TanStack Query, a narrow client-side store if needed, React Hook Form + Zod, a component library, `@xyflow/react` for graph, FastAPI/Pydantic/SQLAlchemy/Alembic/PostgreSQL, local file storage for development (object storage adapter for deployment), a bounded job worker/queue only if needed. Do not force stack replacement on existing code. Prefer stable versions after checking repository compatibility.
- Relational DB is source of truth for structured facts; RAG/search index only for documents. Keep metadata, source offsets/pages, file hashes, course ownership, revisions. Add vector retrieval only with demonstrated benefit. Fallback for missing LLM credentials is an explicitly labeled deterministic/manual flow, never fabricated intelligence.
- Enforce instructor/tenant ownership *at every query and mutation*. Validation, least privilege, IDOR tests, upload size/type/path traversal defense, safe document conversion, retries/idempotency, OAuth CSRF/state, encrypted token storage, audit events, rate limiting, request IDs, observability and privacy/consent are part of P0 foundations.
- Typed dependency edges may allow different semantics. Explicitly choose direction. Enforce acyclicity for hard prerequisite/depends_on relationships if product requires it; other relations need not be DAG. Prevent dangling references and cross-course edges.
- Preserve original documents as immutable versioned artifacts when policy allows; a re-upload/sync must not duplicate material or silently overwrite approved course plans.
- AI output must use schema validation, citations/evidence when answering factual queries, bounded/tool-whitelisted access, prompt-injection isolation, no hallucinated sources, cost budget logging, confidence/uncertainty handling, and mandatory human approval for mutations.
- Session review classifies **observed coverage**, not objective teaching quality: covered / partially covered / not observed / insufficient evidence; always give timestamps/snippets if available. Do not interpret lack of mention as proof of bad teaching.
- UX must include loading, empty, stale, offline where relevant, partial success, error/retry, approval diff, keyboard navigation, accessible graph alternative (list), mobile layouts, and deterministic recovery after job failures.
