# D1 — 10 Feedback (learnings for the next task)

The +0.037 mean-reward "trend" on the opensre RFT run is real in sign but small
relative to the per-step reward std (~0.18, SE of the mean ~0.025–0.03), so over
15 steps it sits within one standard error — the analyzer correctly verdicts it
`flat` at a 0.005/step threshold. Extending to 50 steps is cheap to *configure*
(reuse `train_rft_v2.py` unmodified, freeze group/lr/tasks) but expensive to *run*
(group 6 × 10 tasks = 60 rollouts/step on the Tinker GPU backend; well past a
15-min cap), so the honest deliverable is the runnable 50-step launcher + a real
partial curve + a documented compute blocker, never fabricated steps. The next
task should either (a) run 3+ seeds to put a confidence band on the slope before
claiming the trend continues, or (b) follow the prior memory finding and switch to
the *harder* real-outage cascades where the model starts ~0.2 (real headroom) with
lr 2e-5 — a flat curve on near-ceiling easy tasks is the expected, not surprising,
outcome and shouldn't be over-interpreted as "RFT doesn't work."
