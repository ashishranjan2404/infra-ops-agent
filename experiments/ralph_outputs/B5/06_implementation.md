# 06 — Implementation

## What I built (all under B5/artifacts/, no shared core edited)
1. **`frontier_pass_at_k.py`** — runnable pass@k frontier sweep. Reuses the exact grading
   path of `rex/frontier.py` (zero-shot baseline `_grade` + `rex_tree(...).best_score`) and
   the exact estimators of `experiments/compute_pass_at_k.py` (`pass_at_k`, `wilson_ci`,
   `binary_pass`). Per (model, condition∈{baseline,rex}) it computes pass@1/2/5 + Wilson
   95% CI + mean + within-group std + n, plus per-model pass@1 lift and mean lift. CLI flags:
   `--models --scenarios --seeds --budget --threshold --time-budget-s --out`. Grades with the
   deterministic judge (`judge_fn=None`) for reproducibility. Per-call try/except isolation,
   between-model wall-budget guard, unconditional final JSON write.
2. **`test_frontier_pass_at_k.py`** — 6 unit tests (no network) pinning `summarize`:
   monotonicity+bounds, partial-credit-doesn't-pass-at-1, the n<k extrapolation edge,
   all-pass, empty-no-crash, population-std.
3. **`frontier_pass_at_k_result.json`** + **`run.log`** — REAL subset run output.

## Why this is the right delta on rex/frontier.py
`rex/frontier.py`'s `main()` headline is a single mean-reward column per model
(`baseline_mean`, `rex_mean`, `lift`). That conflates "barely cleared" with "crushed it"
and gives no reliability/CI. This script keeps everything else identical and upgrades the
**aggregation** to pass@k. To upstream: import `summarize`/`run_model`/`print_report` into
`rex/frontier.py`, or run this module directly — no substrate/judge/REx change required.

## How I did NOT touch shared core
- No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`. The script imports them read-only.
- The one substrate property I found (gateway frontier models are `no_temperature`, so
  baseline pass@k is degenerate) is **documented**, not patched — patching would mean
  editing `agent/models.py`/`agent/llm.py` (forbidden) and would change the policy measured.

## Real run (subset, under the 15-min cap)
Command:
```
python3 -u .../frontier_pass_at_k.py \
  --models deepseek-v4-pro,gpt-5.5 --scenarios oom_kill,gcp_service_control \
  --seeds 3 --budget 3 --time-budget-s 540 --out .../frontier_pass_at_k_result.json
```
Wall: **558.7s (~9.3 min)**, 0 errors, 2 models × 2 incidents × 3 seeds × {baseline,rex}.

## Headline result (pass@1 = SLO restored + root cleared + no trap)
| model | baseline pass@1 [CI] | REx pass@1 [CI] | pass@1 lift | mean lift |
|---|---|---|---|---|
| deepseek-v4-pro | 0.167 [0.03, 0.56] | 1.000 [0.61, 1.00] | **+0.833** | +0.425 |
| gpt-5.5 | 0.000 [0.00, 0.39] | 1.000 [0.61, 1.00] | **+1.000** | +0.650 |

The pass@k lens is more revealing than mean: gpt-5.5 zero-shot has mean_reward 0.35
(partial credit) but **pass@1 = 0.000** — it never actually resolves an incident on the
first try; REx lifts it to pass@1 = 1.000. Mean reward alone would have hidden that the
baseline never crosses the resolution bar.
