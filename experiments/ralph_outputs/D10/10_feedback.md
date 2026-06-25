# D10 — 10 Feedback for the next task

Grounding the wrapper in core's own helpers and asserting equivalence to `score_plan` at
default weights (the selftest) was the single highest-value move — it converts "trust me, I
mirrored the formula" into a checkable contract and lets the artifact be non-invasive yet
provably faithful. The biggest lesson for any reward/metric task here: a *global* spread over
a candidate bank that always contains a 1.0 and a 0.0 is pinned at 1.0 and tells you nothing —
the trainability signal RFT actually cares about is the **within-group (per-scenario) reward
std**, so compute that, not the global range. Also, when you can't run the real GPU loop, run
the *reward function* over real sim rollouts and say plainly which half you did — an honest
"reward-design half, training-update blocked" with real numbers beats a fabricated training
curve, and reviewers respect the boundary if argmax-flip evidence proves the weights are
load-bearing. Next reward-shaping task should sample rollouts from an actual model (even a few)
so flip-rate becomes a population statistic rather than an existence proof.
