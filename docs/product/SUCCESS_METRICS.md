# Proposed pilot measures

Targets are hypotheses for B1, not measured results or spending authority. Use a four-week pilot after activation. Report sample counts with ratios, median and p95 where specified, and “insufficient data” for empty denominators. Compare setup against a timed manual task on the same materials. Count distinct event IDs once per attempt. Restrict measurement to pseudonymous owner/course IDs, durations, outcomes and counts. Keep source text and transcripts out of analytics.

| Measure | Numerator / denominator or timed population | Events | Proposed target |
| --- | --- | --- | --- |
| North Star | Active instructor-weeks with an approved plan and at least one evidence-backed group update / active instructor-weeks | plan_approved, benchmark_recorded, instructor_active | ≥60% |
| Activation | New pilot owners approving a first plan within 7 days / enrolled owners with 7 days of observation | pilot_enrolled, plan_approved | ≥70% |
| Setup effort | Active input minutes summed per completed setup / completed setups, also report median | setup_started, input_active, review_submitted | Median ≤15 min and below manual baseline |
| Time to roadmap | First review-ready time minus import submission per successful setup | import_submitted, plan_ready | Median ≤5 min for fixture below |
| Approval and correction | Approved proposals / decided proposals. Edited proposals / reviewed proposals, broken down by kind | proposal_opened, edited, approved, rejected | ≥70% approved, investigate >40% edited |
| Ingestion completion | Supported valid files processed with locatable text / supported valid files submitted | file_received, extraction_finished | ≥95%, report unsupported and partial separately |
| Review usefulness | Reviews rated useful by owner / reviews receiving a rating | review_decided, review_rated | ≥75%, publish response rate |
| Grounding | Supported factual answers with correct citations / answerable evaluation questions. Correct abstentions / unanswerable questions | eval_scored | ≥90% on each, zero cross-owner disclosures |
| Latency and reliability | p95 elapsed read time across group/session reads. Completed valid import jobs / submitted valid jobs after one retry | read_finished, job_submitted, job_finished | ≤2 s reads, ≥95% job completion |
| Recurrence | Activated owners returning for a meaningful course action in week 4 / activated owners observed for 4 weeks | plan_approved, review_decided, benchmark_recorded | ≥50% |
| AI cost per course | Total metered generation/retrieval charges including retries / distinct pilot courses processed | provider_usage with model, units, price version and course | Proposed ≤US$1 per setup, validate pricing before external use. Record zero paid calls in offline demo. |

Performance fixture for comparison: one instructor, two groups, 12 session templates and ten text-bearing documents of at most ten pages each. Record hardware, model mode and failures. Separately report larger workloads, incomplete setups and timeouts so successful-run timing cannot mask abandonment.
