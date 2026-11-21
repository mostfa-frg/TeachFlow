# A1 · Which UI base should TeachFlow keep?

**Recommend A, evolve the current instructor shell.** Its wizard and group controls already call the API. The experiment below found a concrete limit in the persisted graph contract. Changing the renderer alone would leave that limit in place.

## Bounded experiment

Scope was one synthetic save through the actual shell adapter and a field-level comparison against four Frappe Learning v16.1.0 DocTypes. Stop condition was enough evidence to identify reusable flows, missing records and deployment prerequisites. No framework or service was installed for the spike. Frappe runtime permissions, visual accessibility, performance and team proficiency remain unverified.

**Current shell.** In the repository root, run the following JavaScript with Node on stdin. It compiles the complete inline script, extracts the actual save function and sends it three Python-course sessions. Two sessions share a topic, and both point to the API session. The adapter drops the within-topic edge and combines the other two, retaining all three sessions but only one topic prerequisite. Opening an approved draft reconstructs connections from sequence plus topic endpoints in `beginEditRoadmap`. Exact session relationships cannot round-trip through this contract.

```javascript
const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const html = fs.readFileSync("frontend/index.html", "utf8");
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
const adapter = script.split("\n").find(line => line.startsWith("function proposalForSave("));
const save = vm.runInNewContext("(" + adapter.trim() + ")");
const topic = (id) => ({stable_id:id, title:id, description:id, learning_objectives:[id]});
const sessions = [["intro","python"],["loops","python"],["api","web"]].map(([id,parent],i) =>
  ({id,topicStableId:parent,title:id,description:id,objectives:[id],minutes:60,sequenceIndex:i+1}));
const draft = {topics:sessions,edges:[["intro","loops"],["intro","api"],["loops","api"]],
  roadmapProposal:{topics:[topic("python"),topic("web")],sessions:[],warnings:[]}};
const result = save(draft);
assert.equal(result.sessions.length,3);
assert.equal(result.dependencies.length,1);
assert.equal(result.dependencies[0].prerequisite_topic_id,"python");
assert.equal(result.dependencies[0].dependent_topic_id,"web");
console.log("3 displayed session edges -> 1 saved topic dependency; all 3 sessions retained.");
```

**Frappe.** The source probe compared the JSON `field_order` arrays in the four linked definitions. It found course chapters, a batch course list and timetable, lesson course/chapter links, and timetable reference/date/time. The lesson definition has no fields named `session_topics`, `typed_dependencies`, `group_benchmark_evidence` or `review_proposal`. This is a narrow field check. A Frappe extension could represent these relationships in additional DocTypes. A timetable row could anchor a group occurrence while a lesson could anchor shared content. Either mapping still needs explicit group evidence, graph edges and immutable proposal decisions. [Course](https://raw.githubusercontent.com/frappe/lms/v16.1.0/lms/lms/doctype/lms_course/lms_course.json) · [Batch](https://raw.githubusercontent.com/frappe/lms/v16.1.0/lms/lms/doctype/lms_batch/lms_batch.json) · [Lesson](https://raw.githubusercontent.com/frappe/lms/v16.1.0/lms/lms/doctype/course_lesson/course_lesson.json) · [Timetable](https://raw.githubusercontent.com/frappe/lms/v16.1.0/lms/lms/doctype/lms_batch_timetable/lms_batch_timetable.json)

## Alternatives

| Criterion | A · Extend existing shell | B · Frappe Learning extension | C · New custom React/TypeScript shell |
| --- | --- | --- | --- |
| Instructor-only access | Existing UI is instructor-oriented. Add backend identity, ownership and draft scoping. | Reuse roles and user management. Restrict signup, public preview, enrollment, discovery and APIs. Test instructor-owner boundaries for every added DocType. | Same backend access work as A. Rebuild identity-aware navigation and state. |
| Course/group/session model | Keep course, group, versions and goal progress. Migrate session topics, occurrences, edges and benchmarks. | Course/batch/lesson offer partial anchors. Map existing IDs and reconcile Frappe records with versioned TeachFlow plans. | Can reuse the existing API. Still requires the same domain migration as A. |
| Roadmap, list and transcript review | Keep session detail and edits. Add edge round-trip, equivalent keyboard list and evidence/approval screens. | Build custom graph/list, evidence and proposal views in the Vue frontend or extension. | Componentized graph and review UI are plausible. Rebuild import, editing, recovery and mobile behavior. React Flow documents keyboard controls. |
| API and identity boundary | Same-origin FastAPI serves the shell. No second application identity. | Framework REST methods can call or be called by a Python service. Decide which system owns identity, documents and approvals. Avoid duplicate write paths or a globally privileged bridge. | Serve built assets from the same API origin. Port requests and errors slice by slice. |
| Development, deployment and maintenance | Existing Python/Alembic process and no JS build. Large inline functions increase regression risk. Extract only tested seams. | Operate Bench/Frappe and its app dependencies, build Vue assets, maintain permission customizations through upgrades and run TeachFlow integration tests. | Adds Node/build/lockfile and browser test tooling. Incremental introduction can reduce cutover risk. |
| Cost and schedule | **Low–medium integration risk**, medium UI maintenance risk. Least duplicated work. | **High integration risk**. License review, permission verification, migration and operations precede the same custom P0 screens. | **Medium–high integration risk** for a replacement. A route-level trial after parity tests would reduce rework. |

Frappe documents student, creator, evaluator and moderator roles, enrollment behavior and optional guest previews. Hiding navigation alone gives insufficient evidence of isolation. Its framework exposes REST resources and whitelisted methods. [Roles](https://docs.frappe.io/learning/roles) · [Setup and enrollment](https://docs.frappe.io/learning/setup-guide/your-first-steps-with-frappe-learning) · [Lesson previews](https://docs.frappe.io/learning/course-creation/adding-a-lesson/adding-simple-content) · [Frappe REST API](https://docs.frappe.io/framework/user/en/api/rest)

The v16.1.0 tag and release history show active maintenance. The app manifest declares Python ≥3.10, Frappe ≥16 and <17, and a payments dependency. Its frontend links to UI assets in the sibling Frappe tree. These requirements rule out a drop-in install into the existing FastAPI virtual environment alone. The project describes Bench and Docker deployment paths. Neither Bench nor Docker was found on this host's command path. The candidate is AGPL-3.0. The owner should review distribution and network-use obligations before selecting it. TeachFlow had no tracked project license at the audited revision. [Release history](https://github.com/frappe/lms/releases) · [Tagged manifest](https://raw.githubusercontent.com/frappe/lms/v16.1.0/pyproject.toml) · [Tagged frontend](https://raw.githubusercontent.com/frappe/lms/v16.1.0/frontend/package.json) · [Install guide](https://github.com/frappe/lms) · [Tagged license](https://github.com/frappe/lms/blob/v16.1.0/license.txt) · [React Flow accessibility](https://reactflow.dev/learn/advanced-use/accessibility)

**Reconsideration criteria.** B becomes credible if the team can operate Frappe and demonstrate a private instructor-only installation, two-owner isolation and an upgrade-safe graph/review extension. C becomes credible if browser parity tests protect the existing workflows and a small route proves materially easier to maintain. A1 approves a direction only. See the [decision register](../DECISIONS.md).
