# Phase 00 risk register

| ID / priority | Evidence and consequence | Mitigation and acceptance trigger |
| --- | --- | --- |
| R1 · Critical | Course has no owner FK. The v1 handlers lack an identity dependency. Group-to-course checks do not isolate instructors. | Before shared deployment, approve an identity/tenancy model. Verify two-instructor denial tests for every query and mutation, including files and proposal actions. |
| R2 · High | proposalForSave reduces session links to topic pairs. TeachingSession has one topic. A saved graph can differ from the one reviewed. | Preserve stable IDs. Test legacy backfill, same-topic edges, cross-topic edge multiplicity and typed-edge round trips before rollout. |
| R3 · High | Roadmap state and approved_at lack an actor and immutable edit/reject history. Group progress may move to a newer version. | Establish an attributable proposal lifecycle, retain prior evidence and test retries/concurrent approvals before adding generated reviews. |
| R4 · High | extract_document flattens pages. For TXT both original and sidecar are named from the same UUID plus .txt. Re-import generates new IDs. | Verify byte-preserving originals under approved retention, checksums, source locators and idempotent refresh. Exercise malformed, oversized and partial inputs. |
| R5 · High | Synchronous extraction and provider calls share request capacity. No cost ledger, cited search or output-quality suite. | Approve limits and provider policy. Exercise deterministic fallback and evaluate synthetic answers and evidence before using real material. |
| R6 · High | No transcript/review privacy policy, storage lifecycle or release target. Browser draft cache has no instructor scope. | Start with synthetic text, approve access/deletion rules and clear or partition cached state on identity changes. Gate audio separately. |
| R7 · Medium | Monolithic frontend, placeholder navigation and no browser/a11y suite. Shell changes could break accessible setup or progress save. | Cover import → edit → approve → reload, failed writes and keyboard/list parity before changing UI base or extracting components. |
| R8 · Medium | Dependency ranges float. CI, deployment manifest and .env.example are absent. SQLite is the verified DB path. | Reproduce installs in CI, review dependency advisories, restore an empty config template, test PostgreSQL migrations and restore a backup before release. |
| R9 · Medium | Calendar access, team capacity, target budget and Frappe operating experience are unknown. | Set time/spend limits at the next gates. Use manual imports and explicit refresh at week 2. Cut P1 first. |

Risk retirement requires the evidence in the final column. Phase 00 records these risks for planning.
