# I4 — Feedback for the next task

When a sibling task (here C12) already produced a proof, the highest-value move is to
*measure what they asserted* rather than re-derive what they proved: C12 claimed
`I(y;R4|c)=0` in prose; computing it on the real corpus showed it is 0.0344 bits, not 0 —
a small, honest correction that makes the joint argument stronger and exposes exactly which
feature collision (`rollback_without_deploy` on cascade incidents) carries the residual.
Two reusable lessons: (1) the REx feature space Φ has a hard floor `H(y|full Φ)=0.0089` bits
that *no* rule-only change can beat — every remaining sufficiency/safety gap is a *feature*
gap (rollback-target provenance, victim-vs-root topology), so future "add a rule" proposals
should first check whether the signal is even in Φ; (2) avoid the C12 trap of an exactly-0
threshold — pick a defensible criterion (≥95% of `H(y)` removed) up front, because the real
data almost always leaves a small, locatable residual, and reporting it beats hiding it.
Reuse `rex.harness_synth.labeled_examples` for any IT/coverage analysis — it's the clean,
LLM-free oracle over all 42 scenarios.
