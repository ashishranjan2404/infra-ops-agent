# D5 — 10_feedback (for the next task)

The biggest leverage was treating "same data" as a first-class, auditable artifact (a frozen seeded
`split.json` that BOTH configs import) instead of an assertion — it pre-empts the strongest reviewer
attack and made the RFT/SFT contrast precise. Second lesson: when a regime needs an SDK surface you
can't verify (here, a supervised step on HUD's rollout-oriented `TrainingClient`), build an honest
introspection guard that raises a precise `NotImplementedError` rather than a plausible fake loop —
the blocker becomes a finding, not a hand-wave. Third: keep offline tools import-light (avoid pulling
in `hud`/env modules in the 3.13 worker) so the data + harness actually run and self-test; reach for
`.venv-hud` only at the real training boundary. Finally, label any offline grader output a *proxy
ceiling* loudly — the saturated mechanism_match (1.0) on strong demos is genuinely useful for headroom
analysis but trivially mistaken for a result; the caption and the blank trained-results table do real
work. Next worker: reuse this split + sft_pairs to actually run the legs in `.venv-hud` once credits
exist, and add a single-teacher SFT ablation.
