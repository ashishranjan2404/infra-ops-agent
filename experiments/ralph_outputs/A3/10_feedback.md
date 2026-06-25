# A3 — Feedback for the next task

Outreach/process tasks have a real ceiling for an autonomous agent: you can build and validate
the *entire pipeline* (lists, templates, schema, consent gate, tracker, validator) but you
cannot execute the human/legal steps (sending mail, signing DUAs), so be upfront that the
deliverable is machinery + one worked example, and mark the campaign itself as the blocker —
don't fake yield. The highest-leverage next step is the missing `intake → specs/real/*.json`
**transform + evidence-author scaffold**: the intake schema only captures *labels*
(root_cause/trap/causal_chain), and the genuinely hard, unautomated work is generating
internally-consistent synthetic evidence (k8s_pods/metrics/traces) from those labels so a
donated incident becomes a runnable graded scenario. Also keep a `provenance` tag on every
ingested incident from day one — it is the cheap thing that defends the novelty claim against
the "this is just your existing public postmortems" reviewer attack.
