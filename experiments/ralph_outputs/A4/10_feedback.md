# A4 — Feedback for the next task

Outreach tasks have no verifiable end state an offline worker can reach — you
cannot send mail or land a reply — so the win is to convert "do outreach" into a
*tested artifact* the human just executes: a researched, real-channel brief, a
send-ready email with `<PLACEHOLDER>` identity (never fabricate a person or
email), a gating legal checklist, and — the part that's actually gradable — a
**data schema validated against the repo's existing format**. Two reusable moves:
(1) ground every claim in live research (Snorkel's $3M Open Benchmarks Grants and
verifiable-reward RL gyms made the email specific instead of generic); (2) when
proposing data ingestion, make the schema a *superset of the real on-disk format*
(`scenarios/cidg/generated/*.yaml` keys: root_cause/trap_actions/canonical_fix/
slo/assertions) and prove the mapping with a script over real files — that turns a
soft deliverable into a hard, testable one. Stay honest about evidence class:
third-party-authored data fixes the self-authoring/contamination critique but does
NOT close the "0 fully real raw incidents" gap; conflating them is exactly what a
reviewer pounces on. And respect parallel-safety: specify the core-file converter,
don't write it.
