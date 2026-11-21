# PROMPT 11 — OPTIONAL P1 extensions (only after approved P0 release gate)

Only start if P0 Gate R1 is APPROVED, tests are green and the user selects specific P1 feature(s). Do not implement all extensions by default.

Candidate small vertical slices, ordered by user value and integration complexity:
A. Assessment draft from a selected session's approved objectives/materials (quiz/task, difficulty and count, optional rubric, editable proposal + approval; **no automatic grading**).
B. Lightweight plan version history (inspect snapshots/diff, no branching/merging; rollback only if explicitly designed and approved).
C. GitHub read-only commit/repository links to session material (scoped permissions, no git write, no access to unrelated repos).
D. FAQ draft from reliable unanswered questions with transcript citations and instructor approval; no chat delivery/cross-cohort analytics.

Before coding: propose one feature's acceptance criteria, schema/API changes, risks, estimated complexity, privacy issues and exact cut line, then issue DECISION REQUIRED — P1-SCOPE. After approval, build ONE feature behind a flag with tests, docs and a regression pass of all P0 flows. Stop and report. Never smuggle a P2 item into P1.
