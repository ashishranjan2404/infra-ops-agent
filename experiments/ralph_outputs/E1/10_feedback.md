# 10 — Feedback for the next task

Coordination/blocker tasks still have a real, testable deliverable — the trick is to convert
"ask a human" into "ship the artifact that makes the human's action one copy-paste, plus a
verifier that gates it when it lands." Ground every "expected from them" item in an existing
in-repo counterpart (here: the v1/v2 GRPO drivers + run logs + `rex/scoring.py` judge) so the
ask is additive and parity-checkable, not vague. Verify the load-bearing fact with `git`
itself rather than asserting it (the "no GRPO branch on origin" claim is the whole point — it
must be evidence, not memory). Watch for over-broad globs in verifiers: my corpus matcher
initially false-positived on the opensre *target-domain* trajectories, which an in-repo status
doc (`P7_fireball_status.md`) explicitly distinguishes from the Fireball *source* corpus —
read the adjacent status docs before trusting filename heuristics. Finally, separate the
"mergeable" gate from the "scientifically true" gate; conflating them either inflates the ask
(delaying the push) or over-reads a green check as proof of a claim it can't establish.
