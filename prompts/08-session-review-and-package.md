# PROMPT 08 — Session Review and post-session approval package

Implement the constrained P0 Session Review. **Do not build a live meeting bot.**

- Upload instructor-provided transcript (.txt/.srt/.vtt and any expressly approved formats) tied to a group-session occurrence; validate permissions, consent/notice acknowledgement, size/type, PII/retention policy. Recording-to-transcript is conditional on approved secure STT provider or locally feasible worker; transcripts MUST work without audio support.
- Parse timestamps/speakers where present, segment evidence, link to planned objectives/topics/benchmarks, classify `covered`, `partially_covered`, `not_observed`, `insufficient_evidence`. For each report item, give transcript snippet/line/timestamp, source, short rationale and editable human correction. Unanswered questions only if grounded in transcript. Not mentioning a concept never proves teaching quality.
- Validate AI structured result and ground to actual uploaded content. Confidence is calibrated only if evaluated; otherwise surface plain uncertainty and evidence. Store review as a proposal; no automatic benchmark completion without instructor approval and explicit mapping.
- Generate **draft** post-session package from approved/corrected review plus plan: summary, recap, optional homework/follow-up draft, draft group message, missed topics and open questions. Present editable diff/review/approve and copy/export. **Never send** externally.
- Worker flow: upload, queued, progress, transcript extraction, review generated, corrected, package generated, approved; retry, cancel, partial error with user recovery; version/review invalidation if plan or transcript changes.
- Eval: curated synthetic transcripts that cover, partially cover, or omit objectives, contain contradictory mentions and unanswered questions; check citation validity and false coverage. Security: prompt-injection in transcript, tenant isolation, storage deletion and leakage tests.

Deliver real end-to-end transcript → evidence report → manual correction → post-session package → approval/audit, with tests. Stop at checkpoint.
