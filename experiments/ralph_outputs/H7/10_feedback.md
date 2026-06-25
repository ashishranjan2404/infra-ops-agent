# 10 — Feedback for the next task

The highest-leverage move was harvesting REAL numbers before writing a line of code: the
ROSTER in `agent/models.py`, the per-step `mean_reward` in `opensre-traj/runs/train_*.jsonl`,
and the baseline/REx means in `rex/runs/frontier.json` together gave enough ground truth to
populate a registry honestly — and pinning those exact figures in the tests (e.g. the 8b run's
`0.522 -> 0.491` *downward* curve) makes fabrication self-breaking. The trap to avoid is metric
conflation: there is real per-model reward data but NO per-model pass@1, so keep them in
separate columns and leave pass@1 null rather than launder mean reward as accuracy. Future
metadata/registry tasks should ship a `--refresh` derivation path from day one (the snapshot
drift is the one real weakness here) and remember the eval-vs-trainable split — closed models
are baselines you cannot GRPO, and the only trainable assets are the forked Qwen slugs.
