# PROMPT 02 — UX, UI, accessibility and navigable prototype (HARD STOP GATE C)

Read persistent rules, canonical brief, audited code, and approved requirements. Define the complete **instructor-first** interface without accidentally building an LMS for students.

Deliver `docs/design/` artifacts covering:
1. Two grounded/explicitly hypothetical user personas (solo instructor, instructor managing several cohorts) with JTBD/pain points, task frequency and constraints; complete journeys: first Smart Setup, daily dashboard, open group graph, edit session, review suggested plan, upload transcript, inspect evidence, edit post-session draft, ask agent, recover failed import.
2. Site map/information architecture, routing and permissions; desktop/tablet/mobile layout specs, sidebar/group switcher, dashboard information hierarchy, roadmap graph + keyboard-accessible list alternative, session tabs (Plan / Quick Review / Post-Session Package), globally accessible AI assistant, approvals inbox with side-by-side diff and bulk approval only when safe.
3. Detailed low-fi wireframes in Markdown/ASCII and optional clickable **real** frontend prototype reusing the approved stack. Include user text, empty/loading/success/error/stale/partially imported/canceled states, skeletons/progress indicators, undo/retry and navigation preservation.
4. Design system: color, typography, spacing, density, iconography, status semantics (color + icon/text), responsive breakpoints, focus states, forms, buttons, side panels, cards, toasts, modal/confirmation, source citations, graph nodes/edges, review diff, progress indicator, reusable component inventory.
5. Accessibility: WCAG 2.2 AA as a target for core flows, visible focus, keyboard interactions, labels, aria-live for background jobs, contrast, reduced motion, screen-reader alternatives for graph, touch targets. No claim of certification without testing.
6. UX success criteria and usability test plan with 5-8 representative scripted tasks, observations, severity, targeted fixes. Minimize cognitive load: default/optional fields, one approval screen after setup, context-preserving navigation.

Maintain `docs/design/SCREEN_INVENTORY.md`, `FLOWS.md`, `DESIGN_SYSTEM.md`, `INTERACTION_STATES.md`, `USABILITY_TEST_PLAN.md`. If building clickable screens, clearly distinguish wired live data from prototypes; do not change business logic in this phase. Ensure every screen maps to P0 story IDs.

**Gate C1:** Present the UI map and 3 decisions needing approval (navigation model, approval presentation, selected visual direction) only if material; recommend sensible defaults. **STOP for signoff.**
