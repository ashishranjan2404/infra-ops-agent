# B10 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/B10/artifacts/`, no shared-core edits)

### `learning_curve.py` (~190 LoC)
Parser + pass@1 harness + matplotlib plotter for opensre RFT JSONL logs.
- `parse_log(path, threshold)` — reads one JSONL training log, derives **per-step pass@1** from the
  per-rollout `rewards` array: `pass1 = (#rewards >= threshold) / n`. Returns step-sorted rows with
  Wilson 95% CI. Warn-and-skip on blank / malformed / missing-key / empty-rewards lines.
- `wilson_ci` — mirrors `experiments/compute_pass_at_k.wilson_ci` (NOT imported, to keep the artifact
  self-contained and avoid coupling to that shared file's sys.path shims; documented as a mirror).
- `plot` — one pass@1 line + shaded Wilson band + faint dashed `mean_reward` reference per run, a
  dotted threshold line, Agg backend, dpi=130.
- `write_csv` — tidy long-format CSV (run, step, n, passes, pass1, ci_lo, ci_hi, mean_reward).
- `main` — CLI; auto-discovers `opensre-traj/runs/*.jsonl` when no `--log`; exit 2 = blocker.

### `test_learning_curve.py`
5 self-tests: threshold math, inclusive boundary, garbage-robustness, Wilson bounds, real-log parse.

## Real artifacts produced (verified, not placeholder)
- `learning_curve.png` + `learning_curve.csv` — τ=0.8 (canonical "incident resolved").
- `learning_curve_t065.png` + `learning_curve_t065.csv` — τ=0.65 ("substantially-correct diagnosis").

## Data the curve is built on (REAL logs in `opensre-traj/runs/`)
| log | steps | n/step | reward range | pass@1 τ=0.8 | pass@1 τ=0.65 (start→end) |
|---|---|---|---|---|---|
| train_qwen3-8b.jsonl (baseline) | 25 | 24 | 0.05–0.77 | 0.000 flat | 0.375 → 0.208 (degrades) |
| train_qwen3-8b_v2.jsonl | 15 | 40 | 0.14–0.80 | 0.000 flat | 0.375 → 0.525 (climbs) |
| train_qwen3-30b.jsonl | 14 | 24 | 0.17–0.78 | 0.000 flat | 0.167 → 0.167 (flat) |

## Key result
At the operational τ=0.8 bar, **no run ever resolves an incident** — max reward ≈0.78–0.80, so
pass@1 is honestly flat at 0. At the τ=0.65 partial-credit bar the curves separate: the v2
deterministic-reward run is the only one that **climbs** (0.375→0.525), the original 8b baseline
**declines** (0.375→0.208), 30b is flat — consistent with the flat-baseline diagnosis written into
`train_rft_v2.py`'s docstring.

## Shared-core policy
No shared file edited. `compute_pass_at_k` math is mirrored, not modified. Logs are read-only.
