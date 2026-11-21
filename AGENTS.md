# Working on TeachFlow

Before each milestone, read [the operating contract](CODEX_RULES.md), [the canonical project brief](reference/TeachFlow_Project_Brief.md), [the decision record](docs/DECISIONS.md), and the requested file in [the milestone prompt pack](prompts/). Apply approved decisions first. Distinguish inherited code and proposals from decisions the owner has approved.

Work directly on main for authorized milestones. Fetch origin/main before starting and before pushing. Preserve local and remote changes. Fast-forward when possible. If histories diverge, merge remote changes, inspect the result, and repeat relevant validation before a normal push. Never force push, rewrite history or discard work. Use feature branches or pull requests only at the owner's explicit request. Make small reversible commits, run applicable checks, maintain the project records and stop at mandatory approval gates.

Keep TeachFlow instructor-only. Preserve human review for generated changes. Record the outcome, checks and limitations at every handoff.

UI interaction regression guards (owner UX update): Clicking any roadmap session must open its details panel if closed; selecting another session while open must switch the panel content in place without an unnecessary full rerender or repeated entrance animation. The large detail toggle belongs directly below the Edit, Delete and New course actions and must allow explicit open/close. Use palette-aligned semantic action colors (blue for edit, terracotta for destructive actions, sage for create), with keyboard focus states. Preserve selection, focus and editing context, and keep the accessible TeachFlow-styled dropdowns. Maintain regression coverage.
