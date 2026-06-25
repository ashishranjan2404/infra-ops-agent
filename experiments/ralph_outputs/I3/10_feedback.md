# I3 — Feedback for the next task

The single biggest lesson: a hand-rolled statistical primitive must be gated by a
known-answer test BEFORE it touches real data. My first GCM/LCM dip statistic
looked plausible and was deterministic, yet returned D≈0.16 for a Gaussian (truth
≈0.02) — it would have produced a confident, wrong "everything is bimodal." The
Gaussian sanity test caught it; swapping to the vetted `diptest` (AS 217) package
fixed it. Prefer a vetted implementation for any nontrivial statistic and keep the
hand-rolled version only as a labelled fallback. Two operational gotchas worth
carrying forward: (1) `pip install X` can land in a different interpreter than
`python3` — always install with `python3 -m pip` and verify the import under the
exact interpreter that runs the analysis; (2) the richest reward data in this repo
is the A1/A2 `per_incident_rewards` arrays (126-150 episodes/condition), far better
than rex/runs (n=12) for any distributional test. Finally, the scientific payoff
came from reframing the question per the grill: not "are rewards bimodal?" but
"WHICH policies are bimodal?" — that turned a trivial yes into the genuinely
interesting finding that REx is the one condition that collapses the failure mode.
