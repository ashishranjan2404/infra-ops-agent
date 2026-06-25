# A2 — 10 Feedback for the next task

The 750-episode ablation is *not* compute-bound on per-call latency — it is bound by total
wall-clock against gateway throttling, which is why the prior glm-5p2 run died at 175/750 to a
fixed loop timeout. The fix that actually worked was not "a faster model" per se but a
**resumable + time-boxed wrapper** around the existing `rex/eval_pass_at_k.run_eval` (which
already checkpoints every 25 episodes): pick a *working* cheaper model (deepseek-v4-pro — note
`claude-haiku-4-5` 400s and `minimax-m3` returns empty, so always probe before committing),
give it a wall-clock budget, and let it resume. The full run took ~45 min / 2710 s with 0
errors. Scientifically, the headline finding to carry forward is that **rex_no_oracle ≈
best_of_n ≈ retry_realistic** — REx's huge lift (0.89 vs 0.24-0.31) is almost entirely the
*oracle feedback content*, not the Thompson tree; the next task should log REx node counts to
confirm the tree isn't degenerating to <=2 nodes, and should run a second cheap model to test
the "lifts EVERY model" universality claim. Reuse `rex/run_ablation_v2.py::mcnemar_exact` for
paired significance — the JSON schema from `run_eval` drops straight in.
