# I5 — 10 Feedback for the next task

The cleanest, most defensible result from a one-day formal-model task is a **sign-change
crossover**, not a "we got a speedup" number — a sign flip is hard to fake and survives the
"so what?" reviewer, whereas a learning curve driven by your own metric is tautological and
gets shredded. So: when you define a heuristic optimization proxy (`G = Corr·Std` here),
*label it a proxy immediately*, and make the load-bearing evidence a qualitative regime
change (helps→hurts) that your tests actually enforce (a deliberately-bad case must be able
to fail the test). Two concrete follow-ups this task surfaced and could not close: (1)
**derive `G` from the actual GRPO/REINFORCE group-normalized gradient variance** to upgrade
the proposition from semi-formal to a real bound; (2) **measure `rho_V` / within-group
reward flatness on the real CIDG scenarios via `rex/scoring.py`** so the "RLVR is coarse
here" premise is empirical rather than assumed — that single measurement would tell us
whether SME feedback is worth wiring into REx at all. Also: numpy-only + seeded + JSON-out
made this trivially reproducible and CI-friendly; keep that bar for every analysis artifact.
