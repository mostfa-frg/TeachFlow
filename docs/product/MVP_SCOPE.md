# Proposed MVP boundary

**Pilot:** one course owner teaching multiple groups, with a second instructor identity for isolation tests. Start with a reproducible private local demo using synthetic data. A documented secure deployment and restore path remains a P0 release requirement. Hosting, identity provider, retention, external processing and spending require separate approval.

| Window / dependency | P0 outcome | Fallback or cut line |
| --- | --- | --- |
| Week 1 · phases 01–04 | Approve scope, UX and data contracts. Establish owner-scoped access and preserve existing API behavior. | If deployment decisions are pending, validate locally. Gate any shared exposure. |
| Week 2 · 05–06 after identity and schema | Ingest calendar and selected materials. Propose sessions, topics, objectives and dependencies in one editable review. | ICS import or calendar CSV, manual refresh and multi-file upload suffice. Offer one-line setup and group CSV fallback. Without a model key, label manual/deterministic drafting explicitly. |
| Weeks 2–3 · 06–07 after ingestion | Approve a graph that round-trips intact. Show group occurrences, benchmarks, evidence, status and actionable reminders. | Keyboard list provides equivalent graph operations. Missing evidence stays unknown. |
| Week 4 · 08 after session objectives | Review uploaded transcript text against the plan, correct evidence and approve coverage. | Timestamp if supplied, otherwise cite a snippet and source position. Defer audio and transcription pending privacy/cost approval. |
| Week 5 · 08–09 after approved review and indexed sources | Draft post-session package. Answer instructor questions with scoped tools and citations. | Insufficient context yields an explicit gap. Instructor can edit drafts and copy approved text manually. |
| Week 6 · 10 after all above | Run isolated, accessible end-to-end demo, migration, security and restore checks. | Cut P1 first. Report a release blocker if P0 cannot pass. |

**Formats proposed for the pilot.** Parse text PDFs, TXT/Markdown, DOCX, PPTX and plain-text code as data. For scanned PDFs or legacy DOC/PPT without a safe parser, identify the unsupported input and offer an exported PDF, modern Office file or text upload. Confirm this fallback at B1. Continuous sync and native legacy conversion have no acceptance claim until tested.

**P1**, separately approved after P0 passes: bounded assessment drafts, read-only plan history, read-only GitHub links and grounded FAQs. **P2/outside the pilot:** student accounts or portals, bots joining meetings, automatic sending/rescheduling, autonomous grading, composite health scores, cross-course analytics, broad integrations, learner profiling and coaching.

## Acceptance demonstration

Use synthetic Python materials, two independent owners, two groups and a transcript. Import a recurring schedule and files twice and show stable counts. Inspect one draft with a multi-topic session, edit three distinct directed session edges, reload and approve. Show the same graph for both groups, mark one benchmark in only one group, and inspect the resulting prerequisite alert. Open its session in the keyboard list. Upload a transcript, inspect a cited partial finding, correct it, then approve the review and edited package. Ask for the next session and a sourced material claim. Inspect actor, evidence, diff and time for each decision. Demonstrate denial for the other owner and recovery from a failed import. Release requires measured evidence against the [acceptance catalogue](../requirements/TRACEABILITY.md).
