# 03 — Improved Plan

## What changed after the grill
- **Two orthogonal axes** (accepted, PSRE+AAAI): added `role` AND a separate
  `training_status`. Originally I had a single status field; a model can be `trainable` +
  `aborted` simultaneously, so they must not be merged.
- **No metric conflation** (accepted, SMR over RLE): `eval_pass_at_1` stays a separate,
  honestly-null column. The real per-model signal we have (frontier means) lives in its own
  `frontier_baseline_mean` / `frontier_rex_mean` columns. This was the key correction — it
  prevents passing off mean reward as pass@1.
- **Per-row `source`** (accepted, SMR+DOL): every row cites the file(s) it came from.
- **No raw reward arrays** (accepted, DOL): store only start/end mean reward + a `source`
  pointer to `opensre-traj/runs/*.jsonl`. Avoids duplicating the run logs.
- **Training deltas surfaced** (accepted, RLE): `stats` prints start→end with up/flat/down.

## Critiques rejected and why
- **SMR's per-cell confidence intervals / seeds in the registry** — rejected (over-engineering,
  per AAAI's own counter). A registry indexes models and points to eval artifacts; it is not a
  re-implementation of the eval harness.
- **RLE's "populate pass@1 with frontier means so it doesn't look empty"** — rejected. That is
  exactly the fabrication risk. Honest null + a clearly-named real column is better than a
  mislabeled number.

## Final shape
`model_registry.json`: fields {id, slug, base, provider, role, anchor, training_status,
eval_pass_at_1, frontier_baseline_mean, frontier_rex_mean, train_mean_reward_start,
train_mean_reward_end, source} + a notes block. CLI subcommands: list, show, query, stats.
