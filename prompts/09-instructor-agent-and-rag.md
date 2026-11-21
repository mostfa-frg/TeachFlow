# PROMPT 09 — Instructor Agent, grounded RAG, AI evaluations and bounded costs

Implement one pragmatic Instructor Agent with safe tool access and measurable RAG; **no unneeded swarm**.

- Tool surface with typed auth-scoped implementations: `get_course_context`, `get_upcoming_sessions`, `get_session_details`, `get_group_progress`, `get_benchmarks`, `get_related_sessions`, `search_materials`, and optionally draft-only suggestion tools. Tools return sources and enforce owner/course boundaries server side; never trust a model's claimed ID or authorization.
- Ingestion/index: per-course cleaned chunks with page/slide/section anchors, source hashes and revision, deterministic chunking policy plus measured semantic retrieval choice (keyword first or hybrid/vector if evaluation supports it). Handle deletions/reimports, duplicate chunks, corrupted files, concurrency and stale index.
- Routing: DB tools for structured values/schedules/status; retrieval for material facts; use synthesis model for concise cited answers; refuse to invent when evidence missing. Prompt injection isolation, tool whitelist, structured inputs/outputs, PII controls, bounded tool loop, rate limits, model timeouts, fallback UI and no arbitrary code execution/network access by agent.
- UI: context-aware assistant dock, session/group/course scoping, citations that open source material, show when no evidence, suggestions with "Create proposal" not "Apply", cancel/retry and error states, no silent mutations or external sends.
- Model strategy: select provider only with user approval if external/paid; record model/version in events, tokens/cost/latency, prompt version, output schema, per-user/request budget, caching where safe. Avoid LLM calls on every refresh. If no credentials, present legitimate disabled/offline fallback.
- Evaluation set: at least 20 representative questions/grounding cases with expected sources, unauthorized cross-course cases, adversarial embedded instructions and no-answer cases. Report retrieval recall/citation correctness, unsupported claims, latency and cost, using measurable script (not arbitrary model self-score).
- Reminders: offer prerequisites to review before upcoming session using DB relationships; show draft only, never auto-email in MVP.

Implement, test, document decisions and known hallucination limits, then stop at checkpoint.
