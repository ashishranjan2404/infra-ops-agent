# A1 — Full 42-incident pass@k evaluation — SUMMARY

## TL;DR
Ran the **full 42-incident** pass@k benchmark (was only a 15-incident, 5-per-family slice).
One model (glm-5p2, deterministic P0 judge), **all 42 incidents** (12 simple / 20 cascade /
10 novel), **5 conditions**, 3 seeds = **630 real episodes, 0 errors, ~27 min**. Floor check
holds on all 42 (`floor_ok=true`). Headline:

**REx lifts pass@1 from 0.23 (zero-shot) to 0.90 across the full 42-incident set, with
non-overlapping 95% CIs** (rex [0.83,0.94] vs zero_shot [0.17,0.31]).

## Overall pass@k (n=126 per condition)
| condition | pass@1 | 95% CI | pass@2 | pass@5* | mean | std |
|---|---|---|---|---|---|---|
| zero_shot | 0.230 | [0.17,0.31] | 0.41 | 0.74 | 0.43 | 0.38 |
| best_of_n | 0.341 | [0.26,0.43] | 0.57 | 0.88 | 0.65 | 0.31 |
| retry_realistic | 0.349 | [0.27,0.44] | 0.58 | 0.89 | 0.66 | 0.30 |
| **rex** | **0.897** | **[0.83,0.94]** | 0.99 | 1.00 | 0.94 | 0.17 |
| rex_no_oracle | 0.333 | [0.26,0.42] | 0.56 | 0.87 | 0.66 | 0.30 |

* pass@5 is an optimistic upper bound at seeds=3 (Chen estimator saturates); lead with pass@1.

## Per-family pass@1 (rex)
simple 0.889 [0.75,0.96] | cascade 0.850 [0.74,0.92] | novel 1.000 [0.89,1.00].
(zero_shot for contrast: simple 0.556, cascade 0.067, novel 0.167.)

## How it was built (parallel-safe)
- New task-namespaced runner artifacts/run_full_pass_at_k.py — imports rex/eval_pass_at_k.py
  UNMODIFIED, passes per_family=None (=> all 42), and redirects the checkpoint + final JSON
  into A1/artifacts/ so it never races the shared experiments/results/ dir. No shared core
  file edited.
- artifacts/summarize_result.py independently recomputes the table from the stored rewards
  (reproduces the runner's numbers exactly) -> artifacts/summary_table.json.

## Artifacts
- artifacts/run_full_pass_at_k.py — the runner.
- artifacts/full_pass_at_k_glm-5p2.json — full result (42 incidents x 5 conditions x 3 seeds).
- artifacts/summarize_result.py, artifacts/summary_table.json — independent re-derivation.
- artifacts/run.log — full real run output (630 episodes, 0 errors, 1608 s).

## Honest limits (see 09)
Single model; seeds=3 (pass@1 powered, pass@5 degenerate, per-family CIs wide); REx perfect on
the novel family (possibly under-difficult at N=4 budget); rex_no_oracle ~ baseline on cascades
(a real method limitation, surfaced not hidden). A --seeds 5 and --frontier (multi-model)
rerun are the obvious next steps and are supported by the same runner.
