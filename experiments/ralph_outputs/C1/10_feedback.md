# 10 — Feedback for the next task

The cleanest way to sweep a hyper-parameter that lives as a module constant inside a core
scoring function (here `COMPLEXITY_LAMBDA` in `rex/harness_synth.py`) — WITHOUT editing the
core — is to re-implement the scoring math as a parameterized closure and inject it as the
`evaluate=` callback to the generic `rex.tree.thompson_search`, then *prove* the closure equals
the core function at the default value with a sub-1e-12 assertion. That fidelity test is what
makes the sweep trustworthy. Two practical gotchas for the next worker: (1) the Anthropic API
on this machine is out of credits (HTTP 400 "credit balance too low"), so any task that calls
`agent.llm.call` on a `claude-*` model will fail — build a deterministic offline path FIRST and
treat the live API as a best-effort add-on, or repoint the roster at the HUD gateway/Fireworks;
(2) when a greedy add-only search "collapses to empty" under a strong penalty, be careful to label
it as an operator artifact (add-only can't model swap-for-smaller) rather than an inherent property
of the objective — the response *direction* is robust but exact thresholds are operator-specific.
