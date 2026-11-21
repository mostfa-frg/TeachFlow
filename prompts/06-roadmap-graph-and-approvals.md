# PROMPT 06 — Course roadmap generation, graph, sessions and shared approvals

Implement the core product value **from imported sources to approved instructor-editable graph** using the approved design and domain contracts.

- Generate structured draft course, sessions, topics, objectives, suggested benchmark criteria and typed dependency edges from imported material plus calendar/group context. Respect session/topic many-to-many. Keep provenance for each semantic claim and uncertainty/unknowns; use structured schemas with validation, retry/recovery. If LLM provider is not configured, offer explicit guided/manual draft mode and clearly label its capabilities.
- Use one reusable `Proposal` and `Approval` service for all generated changes. States: draft/proposed/pending_review/approved/rejected/superseded or a smaller approved equivalent; prohibit modifying course master state before approval. Show field-level diff, edit/accept/reject, stale proposal detection based on source/version, authenticated actor, timestamp, material provenance, reason and immutable audit event. Make approved plan revision atomic/idempotent; race-safe; no silent AI changes.
- Implement full session details: plan, objectives, topics, relevant materials, benchmarks, related sessions, edit and approval history, source links. Persist separate `GroupSession` scheduled/actual occurrence data from shared canonical course plan.
- Implement roadmap graph using approved renderer: session nodes and typed visible edges; zoom/pan/minimap as appropriate, status badges + accessible list, node filter/search, edit session/edge, graph validation, no hard-prerequisite cycles, no cross-course references, graph layout persist strategy. Verify large-ish graph performance.
- End-to-end test: import → generate candidate → edit review → approve → view shared plan graph → open group occurrence; duplicate proposal replay, invalid edge, rejection, stale version, unauthorized approval and broken generated schema.
- Include deterministic scenario fixtures and AI evaluation samples: objective extraction, session ordering, citation/source recall, benchmark plausibility; record known errors and costs.

Update documentation and stop at checkpoint. If AI outputs substantially influence plan but lack validation/evidence, don't claim P0 done.
