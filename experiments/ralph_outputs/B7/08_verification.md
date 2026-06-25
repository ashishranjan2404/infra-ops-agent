# 08 — Verification against success criteria

| Criterion | Status | Evidence |
|---|---|---|
| Standalone metric, separate from pass/fail | MET | `evaluate()` returns `accuracy` computed only from diagnosis; `rc_vs_resolved_disagree` = 43.1% on real data proves it carries signal pass/fail does not. |
| Grounded in `rex/scoring.py` | MET | imports `rex.scoring._stems` (the deterministic judge's tokenizer); same phrasing-robust matching, no LLM/network. |
| Grounded in scenario YAML root-cause fields | MET | `KIND_CATEGORY` mirrors `rex/harness.py:_KIND_CATEGORY` over `root_cause.kind`; YAML self-test = 0.875. |
| `root_cause_accuracy.py` metric written | MET | `artifacts/root_cause_accuracy.py`, importable + CLI. |
| Unit test written | MET | `artifacts/test_root_cause_accuracy.py`, 13 tests, all pass. |
| Run on available data | MET | 197 real trajectories -> 0.213 accuracy; outputs saved to txt + json. |
| No shared core files edited | MET | only files under `experiments/ralph_outputs/B7/artifacts/` created; proposed core wiring documented, NOT applied. |

## Are outputs real (not placeholder)?
Yes. `run_output.txt` and `rca_result.json` are produced by executing the metric
on the real 197-record HUD trajectory export; the confusion matrix and per-category
recalls are computed, not hand-written. Tests run green in pytest (0.02s).

## Reproducibility
Deterministic (no RNG, no LLM, no network). Re-running yields identical numbers.
