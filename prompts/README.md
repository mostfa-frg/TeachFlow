# TeachFlow — Codex Prompt Pack

This is a **milestone-based execution system**, not a one-shot instruction to generate a giant unfinished app. Every phase contains a verifiable result, test requirement and stop point. It is based on the provided canonical TeachFlow project brief.

## Setup for an existing repository
1. Copy `CODEX_RULES.md`, the `prompts/` directory, and `reference/TeachFlow_Project_Brief.md` into the TeachFlow repository. If it already has a canonical brief, verify differences before replacing anything. Respect any existing `AGENTS.md` instructions.
2. Open Codex **at the repository root** on a clean or intentionally controlled branch with access to the code. Paste the message below (replace the path only if you organized the pack differently):

   `Read CODEX_RULES.md and reference/TeachFlow_Project_Brief.md completely, then execute prompts/00-repo-audit-and-ui-spike.md. Do not advance to the next phase. Stop for every critical user decision and show the requested options.`

3. Answer the first UI-base decision in the form `APPROVE A1: A` or choose the recommended option with adjustments.
4. Paste each next prompt after you inspect its milestone report. For example: `Read CODEX_RULES.md, reference/TeachFlow_Project_Brief.md, docs/DECISIONS.md and execute prompts/01-product-and-requirements.md. Stop at its gate.`
5. Review demo/results and checkpoints; do not just respond “continue everything”. Explicitly approve blocking architecture/consent/cost decisions before Codex invokes providers or runs destructive migrations.

## Phase schedule (suggested, can adapt to existing implementation)

| Phase | Objective | Required checkpoint | Proposed project window |
|---|---|---|---|
| 00 | Repository audit & UI-base comparison | Gate A1 | Week 1 |
| 01 | Product + requirements baseline | Gate B1 | Week 1 |
| 02 | Complete UX/UI specification | Gate C1 | Week 1 |
| 03 | Architecture, ERD, API contracts, security | Gate D1 | Week 1 |
| 04 | Auth, database, frontend shell, CI | Verified real vertical slice | Week 1–2 |
| 05 | Setup, calendar/ICS, files, import jobs | Verified import pipeline | Week 2 |
| 06 | AI draft roadmap, graph, approvals | Verified review/approve plan | Week 2–3 |
| 07 | Benchmarks, group progress, dashboard | Two-cohort isolation & alerts | Week 3 |
| 08 | Transcript review + post-session drafts | Evidence-based review/package | Week 4–5 |
| 09 | Grounded assistant and RAG | Evaluation, safe tool calls | Week 5 |
| 10 | E2E QA, security, a11y, release | Gate R1 | Week 6 |
| 11 | Optional P1 | Separate scope approval | Only after P0 |

Week allocation is a **prioritization guide**, not a guarantee. If a time constraint hits, reduce polish, automation and P1 scope before removing approval, privacy or cross-group isolation safeguards.

## Important baseline recommendations (not pre-approved commitments)
- Prefer adapting existing working code. Run a **time-boxed Frappe Learning vs custom frontend spike**, then ask user before committing.
- Candidate simple stack if current repo has no meaningful frontend/backend: React + TypeScript + Vite, React Router, TanStack Query, React Hook Form + Zod, `@xyflow/react`; Python FastAPI + Pydantic + SQLAlchemy + Alembic + PostgreSQL. Add a worker only for jobs needing independent retries. Keep search simple initially; add vectors if tests show benefit.
- Offer ICS calendar and manual file import early; OAuth and external storage/provider choices are decision-gated. **Uploaded transcripts must work** without third-party speech recognition. All AI changes are proposals until approved.
- Store approved decisions and status in-repo so restarting Codex doesn't erase context.

## Completion checklist
The P0 is complete **only if** a real instructor can import calendar and materials, approve a session graph, view different group progress, inspect session plans, upload transcript and check coverage evidence, approve a post-session draft, ask source-grounded questions, see next-step alerts, and inspect an audit log — with tests, authentication, privacy and reproducible setup. The final gate can be NO-GO; that is correct if core criteria have not been met.
