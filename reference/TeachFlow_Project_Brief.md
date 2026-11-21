# TeachFlow — Project Context & Implementation Brief

**Purpose:** This document is the canonical project brief for a ChatGPT Project dedicated to designing, implementing, and documenting TeachFlow.  
**Status:** Proposed MVP scope, informed by the existing TeachFlow MVP Plan and prior product discussions.  
**Primary constraint:** A six-week delivery window and limited time/resources. Prefer a working, focused product over broad feature coverage.

---

## 1. Product vision

**TeachFlow is an AI-powered, instructor-only course management and planning platform.** It reduces the instructor's administrative work by automatically organizing course materials, schedules, sessions, and group progress, then asking the instructor to review and approve meaningful changes.

> **Core principle:** The instructor shouldn't manage TeachFlow. TeachFlow should manage the course for the instructor.

The platform is for instructors and administrators only. **Students do not log in and do not use TeachFlow directly.** Student/group information, if needed, is stored only to support instructor-side progress tracking, with data minimization.

### Product promise

**Connect → Select materials → Wait → Review once → Approve → Done.**

After setup, new calendar events and new files should be detected and processed automatically where feasible. Avoid repeated data-entry forms and unnecessary manual maintenance.

## 2. Product goals

1. Reduce instructor setup and administration effort.
2. Turn existing course materials into an editable, connected session roadmap.
3. Show each group's progress through the roadmap and highlight concrete issues.
4. Compare session plans with what was actually covered, when transcript/recording input is available.
5. Prepare useful post-session outputs for instructor approval.
6. Give the instructor a context-aware AI assistant grounded in course materials and course data.
7. Keep the MVP achievable by reusing an existing LMS/UI where it meaningfully reduces frontend work.

## 3. Target user and UX

### Target user
- Instructor / course owner.
- Optional administrator role for configuration and support.
- No student-facing accounts or student-facing product workflow in the MVP.

### Main screens
1. **Dashboard:** “Needs your attention” alerts, pending approvals, groups falling behind, upcoming sessions.
2. **Groups sidebar:** Selecting a group opens that group's roadmap.
3. **Group roadmap:** A visual graph of session nodes, dependencies, and completion/benchmark status.
4. **Session page:** Plan, Quick Review, and Post-Session Package.
5. **AI assistant:** A chat panel for session preparation, questions about course material, and grounded suggestions.
6. **Smart Setup:** Calendar connection + materials folder selection/import + one review/confirmation screen.

Keep the UI instructor-centric and minimize navigation and data entry.

## 4. Core domain model

Treat sessions as the visible nodes in a course/knowledge graph. A topic may span multiple sessions; a session may cover multiple topics.

Core entities:
- Course
- Group / cohort
- Session
- Topic
- SessionTopic (many-to-many relationship)
- SessionDependency / relationship edge
- Material / file
- Learning objective
- Benchmark
- Session review
- Assessment draft (optional MVP extension)
- Post-session package
- Approval
- Course plan version / change log

Possible session-edge types:
- `prerequisite`
- `depends_on`
- `reinforces`
- `extends`
- `introduces`
- `applies`

Example course sequence: Python fundamentals → OOP → Git and APIs → FastAPI → databases → RAG project. This is a graph, not merely a linear checklist.

Each session should be able to show:
- Topics and learning objectives
- What will be taught and why it matters
- Prerequisites and related earlier sessions
- Materials
- Benchmarks
- Completion/review status
- Optional assignments/assessment drafts
- Relevant code/commit history if Git integration is implemented

## 5. MVP feature scope

### P0 — Must deliver

#### 5.1 Smart Setup and ingestion
- Import/parse calendar events to infer recurring groups and session schedules.
- Import a selected course-material folder or uploaded files.
- Extract text and metadata from PDF, PPT/PPTX, DOC/DOCX, notes, and code where practical.
- Generate a draft course roadmap with sessions, topics, objectives, and dependency suggestions.
- Present one review screen for the instructor to approve or edit.
- Provide a fallback one-line setup prompt, e.g. “Python course, 4 groups, Saturday and Monday.”
- CSV import for groups may be a fallback, not the primary workflow.

**Pragmatic MVP boundary:** If fully automatic folder watching or calendar sync is too difficult, support manual import/refresh first, but keep the product architecture ready for background sync. Do not promise reliable continuous watching until tested.

#### 5.2 Course roadmap and session management
- Show groups in the sidebar.
- Show session nodes as a connected roadmap graph.
- Allow opening a session to inspect plan, objectives, materials, related sessions, and benchmarks.
- Keep group-specific progress while reusing shared course/session structure where appropriate.
- Make relationships visible and editable.

#### 5.3 Benchmarks and group progress
- Generate suggested benchmarks from objectives/materials.
- Track benchmark states and completion at group/session level.
- Display actionable indicators such as incomplete prerequisites or a group falling behind.
- Prefer transparent status and concrete evidence over an unexplained single score.

#### 5.4 Session Review Agent — constrained first version
- Start with **uploaded transcript or recording**, not live meeting-bot attendance.
- Compare transcript content against planned topics, objectives, and benchmarks.
- Report covered, partially covered, not-covered, and unanswered-question signals when evidence supports them.
- Include evidence/snippets or timestamps where available.
- Avoid claiming that a concept was poorly taught based only on topic mention; quality assessment requires a higher-confidence rubric and evaluation.

#### 5.5 Post-Session Auto Package
Build from the Session Review output:
- Session summary
- Recap / key concepts
- Homework or follow-up activity draft
- Draft group message
- Missed-topic and unanswered-question notes
- One approval/edit step before anything is sent or applied

Do not implement delivery to external messaging services in the first version unless time permits.

#### 5.6 Instructor AI Agent
A single orchestrator/agent initially; do not create a multi-agent architecture without a demonstrated need. Use tools/functions for deterministic data access and actions. Use LangGraph if it helps implement explicit workflows, state, and human approval.

Initial tools:
- `get_course_context()`
- `get_upcoming_sessions()`
- `get_session_details(session_id)`
- `get_group_progress(group_id)`
- `get_benchmarks(session_id, group_id?)`
- `get_related_sessions(session_id)`
- `search_materials(query, course_id?)`

The agent should retrieve real course context before answering, ground material-related answers in retrieved content, and distinguish known data from suggestions. It may propose changes but must not silently modify the roadmap or send messages.

#### 5.7 Approval and audit trail
- All generated roadmaps, benchmarks, reviews, assessment drafts, and post-session content are proposals until approved.
- Record what was proposed, approved, edited, rejected, and when.
- Use a shared approval workflow rather than custom approval code for every feature.

### P1 — Include only if time permits

#### 5.8 Auto-generated assessments (small slice)
A bounded assessment draft tool:
- Generate a short quiz or task from one session's objectives and selected materials.
- Let instructor specify type, difficulty, and question count.
- Optionally generate a simple rubric for a task.
- Keep instructor review mandatory.
- Defer automated grading, confidence calibration, and adaptive scheduling.

#### 5.9 Course version history (lightweight)
- Store snapshots or change records when the instructor approves a roadmap/plan change.
- Show what changed and allow viewing a prior version.
- Full branching/merging/version-control features are out of scope.

#### 5.10 GitHub commit-to-session linking
- Add only if the team already has time and a clear demo use case.
- Start with read-only repository/commit linking.
- Do not make Git integration a dependency for core course workflows.

#### 5.11 FAQ from session questions
- Only if transcript/question extraction is reliable.
- Extract recurring or unanswered questions from transcripts and draft a grounded FAQ.
- Reuse Session Review output and course-material retrieval.
- Defer chat integrations and cross-cohort question analytics.

### P2 — Later phases / explicitly out of scope

- Fully adaptive course planning and automatic schedule changes.
- Course Health Score as a single composite number.
- Project/team matching based on student profiles.
- Cross-course/cohort analytics.
- Instructor coaching and longitudinal teaching-style metrics.
- Plagiarism/AI-use detection.
- Broad multi-language/accessibility workflows.
- Slack/Discord/LMS/Notion integrations beyond the one essential calendar/material workflow.
- Live meeting bot that joins calls automatically.
- Automated grading that makes decisions without instructor review.
- Student accounts, student dashboards, or student-facing workflows.

## 6. Important comparison decisions from the prior product discussions

The existing MVP plan aligns well with the earlier concept on:
- Instructor-only platform, with no student access.
- Sessions as nodes in a connected roadmap graph.
- Minimal-effort onboarding and one confirmation screen.
- Automatic benchmark suggestions and group progress.
- Session review, post-session package, and context-aware reminders.
- One Instructor Agent that uses tools/RAG rather than many separate agents.
- Approval before applying AI-generated changes.

Keep these earlier refinements explicit:
1. **The roadmap is a graph**, not just a sequence of lessons.
2. **Reminders are agent behavior**, not a separate complex subsystem. Use dependencies and session context to generate lightweight reminders.
3. **Cost control matters.** Do not send every file or every sync event to an expensive LLM. Use deterministic parsing, database queries, local/cheap extraction, embeddings, and rules where possible; call an LLM for semantic extraction and drafting.
4. **No repetitive manual maintenance.** Background sync is the goal, but it is acceptable to ship manual import/refresh first if automatic watching threatens delivery.
5. **Session review should start with uploaded transcripts/recordings.** Live meeting access is integration-heavy and unreliable for a short project.
6. **Use existing software to save frontend time**, but evaluate the framework and customization cost before committing to it.
7. **Instructor remains in control.** Generated output is a draft until explicitly approved.
8. **No student accounts.** Do not accidentally turn TeachFlow into a student-facing LMS.

## 7. Recommended implementation architecture

Use the simplest architecture the team can deliver and maintain.

### Logical components
- Existing LMS/UI or lightweight frontend shell
- Backend API
- Relational database for structured course data
- File storage and parsing pipeline
- Retrieval/search index for course materials (vector search optional initially)
- One Instructor Agent/orchestrator with tools
- Background job queue for ingestion/review tasks if needed
- Calendar integration
- Approval/audit service

### Candidate stack
- Backend: Python + FastAPI, unless adopting an LMS whose backend/framework is worth reusing.
- Structured data: PostgreSQL.
- AI workflows: LangGraph only where explicit workflow state/human approval helps; otherwise simple Python functions first.
- RAG: Start with a reliable document search/chunking pipeline; add vector database only when semantic retrieval is needed.
- Frontend: Prefer reusing an open-source LMS/admin UI if it fits the instructor-only model. Avoid assuming a specific base project until a short technical spike confirms it.
- Background tasks: Keep simple; add a queue/scheduler only for jobs that must run asynchronously/reliably.
- Integrations: Calendar and material import first. Everything else is optional.

**Architecture decision rule:** Do not adopt a framework just because it has many features. Validate that its data model, permissions, UI customization, APIs, deployment, and license fit TeachFlow.

## 8. Open-source LMS/base-project decision

Frappe Learning was previously suggested as a possible base to reduce frontend effort. Treat it as a **candidate, not a confirmed decision**.

Before committing, run a short proof of concept:
1. Can we remove or hide student-facing flows and operate as instructor/admin only?
2. Can its course/lesson/batch model map cleanly to TeachFlow's groups, sessions, objectives, benchmarks, and graph edges?
3. Can we add a custom roadmap graph and session-review UI without a large rewrite?
4. Can our Python AI service integrate cleanly with its backend and auth?
5. Is its deployment and local development manageable for the team?
6. Does the license and maintenance state suit the project?

Time-box the spike. If substantial rewrites are needed, use a simpler admin UI/template with FastAPI instead.

## 9. Suggested delivery plan (six weeks)

This is a proposed schedule, not a guarantee. Cut scope if integration risks emerge.

### Week 1 — Foundation and feasibility
- Confirm base LMS versus custom UI with a time-boxed spike.
- Define entities, relationships, permissions, and API contracts.
- Set up repository, development environment, sample course, and evaluation examples.
- Test calendar access and document parsing on representative files.

### Week 2 — Smart Setup and roadmap
- Implement material ingestion and calendar import.
- Generate initial course/session roadmap and dependencies.
- Build one-screen approve/edit flow.
- Show graph nodes with basic session detail.

### Week 3 — Groups, benchmarks, progress
- Implement group-specific benchmark status.
- Display roadmap/session progress and actionable alerts.
- Add related-session/prerequisite retrieval.

### Week 4 — Session review
- Accept uploaded transcripts first.
- Compare transcript to objectives/plan and produce evidence-grounded coverage report.
- Add quick-review UI and manual correction path.

### Week 5 — Post-session package and assistant
- Generate summary, recap, homework, and message drafts.
- Implement core Instructor Agent tools and material-grounded Q&A.
- Add context-aware reminders and shared approval/audit flow.

### Week 6 — QA, hardening, demo
- Test full setup-to-dashboard flow.
- Evaluate roadmap/benchmark/review outputs against sample courses.
- Fix errors, document limitations, secure integrations, prepare demo.
- Only add one small extension if core flow is stable.

## 10. Team workstreams (adapt to actual team size)

The source MVP plan assumes six team members:
1. Backend/technical lead: schema, API, auth, jobs, approvals, notifications.
2. Course AI: parsing, topic/objective extraction, roadmap, benchmarks, assistant.
3. Session AI: transcript processing, session review, post-session package.
4. Frontend: dashboard, roadmap, session details, approval screens, chat.
5. Integrations/data: calendar, material import, group import, sync.
6. Product/QA: UX, sample courses, evaluation, tests, documentation, demo.

Reassign or combine roles based on actual team size. Do not treat six members as a confirmed team fact unless the project team confirms it.

## 11. Definition of Done for the MVP

A demo-ready MVP should allow an instructor to:
1. Connect/import a calendar and choose/import course materials.
2. Review and approve an initial group/session roadmap.
3. See each group's roadmap and benchmark progress.
4. Open a session and inspect its plan and related sessions.
5. Upload a transcript and receive a coverage review against the plan.
6. Generate a post-session package for approval.
7. Ask the Instructor Agent questions grounded in course materials and current course data.
8. See actionable reminders and pending approvals.
9. Inspect an audit trail of approved changes.

If the six-week deadline is at risk, prioritize steps 2, 3, 4, 6, and 7 with sample calendar/material imports; do not let live meeting integration or automatic background file watching block the demo.

## 12. Engineering principles

- Build the smallest vertical slice first.
- Use structured database tools for structured facts; use RAG for unstructured course materials.
- Keep prompts, outputs, and schemas testable.
- Validate AI outputs against known examples.
- Treat AI output as untrusted proposals; validate before applying.
- Keep confidence/uncertainty visible where useful; do not fabricate missing course facts.
- Minimize student-related personal data and respect consent for recordings.
- Prefer readable, documented tools over unnecessary agent frameworks.
- Track failures, latency, and model/API costs.
- Do not promise automatic integrations until tested end to end.

## 13. Suggested ChatGPT Project instructions

Use the following as the Project's instructions if desired:

> You are the technical/product copilot for TeachFlow, an instructor-only AI course management and planning platform. Use the uploaded TeachFlow project brief as the canonical source of project decisions. Preserve the core principles: minimal instructor effort, session-node roadmap graph, no student accounts, cost-conscious AI, one Instructor Agent with tools, and human approval for changes. Prefer practical, incremental, engineer-ready advice. Separate MVP from later phases. When suggesting a feature, explain value, implementation complexity, dependencies, and what it replaces or reuses. Do not expand scope without explaining the trade-off. Do not assume Frappe Learning or any other base LMS is selected until feasibility is verified. Produce implementation-ready artifacts when asked (issues, tasks, schemas, APIs, prompts, test plans, architecture decisions). If project facts are missing, identify the uncertainty rather than inventing decisions.
