# TeachFlow improvement outcomes

## Instructor dashboard surfaces the next actions

- [x] The dashboard shows a clear course context, “needs your attention” items, pending approval state, upcoming sessions, and group progress instead of only a course card.
- [x] Attention copy is concrete and tied to an instructor action; it does not invent student-facing workflows or unexplained composite scores.

## Roadmap progress is actionable

- [x] The roadmap keeps the selected course and group visible and shows completed, in-progress, upcoming, and attention states.
- [x] A selected session offers a reversible complete/reopen control.
- [x] Persisted courses use the existing group/session progress API; the local sample course remains explicitly local.

## Reference-aligned responsive shell

- [x] The warm neutral canvas, sage/blue/terracotta status palette, connected graph, compact controls, and asymmetric detail panel remain coherent on desktop and mobile widths.
- [x] Focus-visible behavior and reduced-motion behavior remain supported.

## Validation and documentation

- [x] Existing backend tests pass: 20 passed.
- [x] The app starts and serves the route manifest and main UI successfully.
- [x] Known limitations remain documented; no unsupported calendar or student workflow is implied.
