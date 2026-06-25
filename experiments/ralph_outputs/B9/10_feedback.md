# B9 — 10 Feedback for the next task

The real per-episode data in this repo is small and **clustered** (`rex/runs/ablation.json`
= 5 incidents × 3 near-deterministic seeds), so any per-episode statistic — Wilson,
bootstrap, or otherwise — is bottlenecked by ~5 effective samples, not 15. If your task
touches CIs, significance, or "does REx beat baseline," respect the incident clustering
(block/cluster resampling answers the generalization question; i.i.d. answers only the
fixed-5-incidents question) and lead with the honest n caveat rather than reporting a
deceptively tight interval. Reuse `experiments/compute_pass_at_k.py` read-only for
`pass_at_k`/`wilson_ci`/`binary_pass` so point estimates match the canonical pipeline and
you can assert equality. Watch the `parents[N]` path index when a script lives several
levels deep under `experiments/ralph_outputs/<ID>/artifacts/` (repo root is `parents[4]`),
and always add a `--data` override so a wrong guess fails loudly instead of silently
reading the wrong file. Stdlib-only (hand-written, tested percentile) keeps artifacts
runnable in every worker env and dodges numpy's interpolation-mode ambiguity.
