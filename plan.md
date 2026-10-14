# TeachFlow UI improvement plan

## Direction

TeachFlow should feel like a calm instructor workspace: graph-first, evidence-aware, and optimized for one review/approval moment rather than repetitive administration.

- **Design movement:** quiet editorial admin interface with soft, paper-like surfaces and a connected knowledge-graph motif.
- **Core principles:** reduce cognitive load; make status actionable; keep generated work visibly provisional; keep the selected group and course context persistent.
- **Color philosophy:** warm off-white canvas for focus, sage for completed/approved work, muted blue for active work, terracotta for attention, and lavender for optional/secondary information.
- **Layout paradigm:** a persistent course/group context rail, compact topbar, and asymmetric content areas that prioritize the roadmap and its selected session.
- **Signature elements:** connected roadmap edges, compact status dots/badges, and attention cards that turn progress into a next action.
- **Interaction philosophy:** every status should answer “what should I do next?”; edits remain reversible and approvals remain explicit.
- **Animation:** use short ease-out transitions only for selection, toast feedback, and progress changes; honor reduced motion.
- **Typography:** system sans for reliable rendering, with tight display sizing for page titles and generous line-height for explanatory copy.
- **Brand essence:** an instructor’s operating system for turning teaching material into a course plan; calm, grounded, practical.
- **Voice:** concise and supportive. Example: “Three groups need a quick check-in.” / “Review the proposal before it becomes the plan.”
- **Wordmark/mark:** retain the simple directional mark, but use it as a visual cue for flow rather than a generic app icon.
- **Signature color:** sage green `#708a7b`.

## Implementation

1. Improve the existing standalone frontend without introducing a framework migration.
2. Replace placeholder dashboard copy with attention, upcoming-session, group-progress, and approval-oriented surfaces.
3. Add a real “mark complete / reopen” action to roadmap session details. Persist it through the existing group progress endpoint when API identifiers exist; keep local demo behavior explicit.
4. Improve responsive behavior, focus states, status hierarchy, and reference-aligned spacing.
5. Add route metadata for the two currently rendered screens.
6. Validate with the existing Python test suite plus a frontend smoke check through the running FastAPI app.

## Project structure

- `frontend/index.html`: current self-contained instructor UI, styles, state, and API wiring.
- `backend/app/api/v1/router.py`: course, material, roadmap, and progress endpoints.
- `backend/app/models.py`: relational course/roadmap/group progress model.
- `backend/tests/`: API and validation coverage.
- `docs/`: architecture and implementation status.
