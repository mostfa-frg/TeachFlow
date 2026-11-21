# PROMPT 01 — Product definition and complete requirement baseline (HARD STOP GATE B)

Read `CODEX_RULES.md`, canonical brief, audited repo and approved decisions. This phase is **product/requirements engineering**, not feature development.

Produce an engineer-ready, internally consistent MVP spec:
- `docs/product/PRD.md`: precise problem, instructor pain points, vision/value proposition, personas and stakeholder matrix, key jobs-to-be-done, target contexts, competitor/alternatives assumptions (no fabricated research), core workflows, benefits, business risks, critical assumptions, tradeoffs and six-week scope.
- `docs/product/MVP_SCOPE.md`: P0/P1/P2, in/out boundaries, P0 non-goals, dependency map, explicit fallback modes and acceptance demo; do not silently upgrade P1/P2 to P0.
- `docs/product/SUCCESS_METRICS.md`: North Star, activation, instructor setup effort, time-to-roadmap, approval/correction rate, ingestion completion, coverage-review usefulness, assistant grounded-answer quality, latency/reliability, recurring instructor usage, cost per course; include numerator/denominator, event instrumentation and sensible **proposed** pilot targets needing validation.
- `docs/requirements/FR.md`, `NFR.md`, `BUSINESS_RULES.md`, `USER_STORIES.md`, `ACCEPTANCE_CRITERIA.md`, `TRACEABILITY.md` (or one well-indexed set). Assign stable IDs (e.g., `TF-FR-001`, `TF-NFR-001`, `TF-US-001`, `TF-BR-001`). For every P0 user story write testable Given/When/Then acceptance criteria covering happy, empty, invalid, duplicate, cancellation, processing, failure and authorization paths when relevant.
- Domain glossary: course, group, session template vs scheduled occurrence, topic, objective, benchmark, observed coverage, proposal, approval, audit, version, material/source. Identify ambiguities and recommended resolution.
- Requirements across all 12 areas, including setup, imports, graph, benchmarks, progress, dashboard, AI assistant, transcript review, post-session draft, approvals/audit, accessibility, latency, security, admin and deployment.

Review for contradictions: e.g. P0 calendar ingestion vs background watching limitation; no student accounts; no automatic message sending; no live meeting bots. Cross-link each P0 FR to story + acceptance criterion + planned phase + test type. Create risk/assumption register.

**Gate B1:** Summarize scope and any required decisions in a single concise approval question (MVP boundary, target instructor, deployment assumptions); if material disagreements exist, issue formal DECISION REQUIRED. **STOP before implementation.**
