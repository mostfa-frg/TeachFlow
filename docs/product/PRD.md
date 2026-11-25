# TeachFlow pilot product definition

**Proposed for B1, 22 November 2026.** An instructor teaching the same Python course to Saturday and Monday groups has one set of materials and two different classroom realities. Rebuilding a plan from files, remembering which group missed a prerequisite and preparing each recap all consume preparation time. TeachFlow should let the instructor import once, review one proposed plan and spend subsequent visits on upcoming sessions and exceptions.

| Stakeholder and context | Job and value | Decision or responsibility |
| --- | --- | --- |
| Course owner at a desktop before term | Turn a calendar and mixed teaching files into an editable session graph | Correct ambiguous group assignments and approve the shared plan |
| Same instructor between classes, often on a phone | See what this group needs next and why | Confirm group evidence and correct misleading alerts |
| Instructor after class | Check observed coverage and prepare follow-up from a transcript | Review source snippets, edit findings and approve drafts |
| Optional installation administrator | Configure approved services and recover a deployment | Explicitly assigned operational privileges. Course access requires separate authorization |
| Product owner / pilot evaluator | Decide whether time saved justifies ongoing use | Review pilot measures, scope exceptions, costs and release evidence |

A calendar plus folders and spreadsheets may already serve small courses well. A conventional LMS may offer more authoring and enrollment functionality than this instructor needs. These are alternatives to test with pilot instructors, not market research results. Compare elapsed time and corrections on the same sample course before claiming a benefit.

Follow the [six-week scope and demo](MVP_SCOPE.md). The existing shell and FastAPI endpoints remain the foundation under A1. Address the session-edge round trip before expanding graph editing. Represent structured facts in the database, attach document evidence to claims, and route proposed changes through one decision workflow. A missed transcript mention cannot establish poor teaching or failed learner mastery.

## Assumptions to test

| Assumption / business risk | Validation and response |
| --- | --- |
| Reusing plans across groups saves effort | Pilot with two groups on different schedules. Measure time to approval and weekly return visits. If setup costs outweigh reuse, simplify import review. |
| Instructors can supply usable files and transcripts | Sample representative inputs with consent. Report extraction gaps and permit manual correction. Use synthetic content until privacy terms are approved. |
| Review costs less time than drafting manually | Compare active setup time and correction rate with a manual baseline. Preserve evidence and rejection even if output quality is low. |
| A six-week pilot fits available capacity | Team size, budget and hosting remain unconfirmed. Defer optional work, then escalate any threatened P0 criterion. |

[Proposed pilot measurements](SUCCESS_METRICS.md) · [Engineering risks](https://github.com/mostfa-frg/TeachFlow/blob/580fac6c9c1da89d12e5ddf7483fbbc50d380dee/docs/RISKS.md) · [Testable requirements and glossary](../requirements/TRACEABILITY.md)
