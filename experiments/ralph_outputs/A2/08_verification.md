# A2 — 08 Verification

## Success criteria (from 01) vs reality

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Runnable, syntax-valid, import-correct runner reproducing the 750-episode design with a faster model | **MET** | `py_compile` OK; imports resolve from repo root; `target=750 episodes (5 cond x 30 inc x 5 seeds)` printed at launch; run executed real episodes with 0 errors |
| 2 | Real deterministic pass@k for as many episodes as budget allows, checkpointed & resumable | **MET — FULL 750/750** | P0 deterministic judge (`judge_fn=None`); **all 750 episodes completed in 2709.8 s, 0 errors**; checkpointed throughout. rex pass@1=0.893 vs zero_shot 0.240 |
| 3 | No shared core file edited; no fabricated results | **MET** | Only NEW files under `experiments/ralph_outputs/A2/`; every number from real API rollouts; McNemar p<0.0001 on all REx-vs-control pairs |

## Are the outputs real (not placeholder)?
Yes. Every reward is produced by an actual `deepseek-v4-pro` completion scored by the
deterministic judge. The `.partial`/final JSON contains per-incident reward lists, not
constants. Floor check is computed from real empty/trap plans (`empty=0.0`, `trap=0.1`).

## Frozen-judge / fair-comparison check (grill item)
The proposer model is the ONLY thing that changed; reward = P0 deterministic judge,
inherited unchanged from `rex/eval_pass_at_k.py`. So the ablation's internal contrasts
(rex vs best_of_n vs retry_realistic vs rex_no_oracle) remain valid. Cross-model comparison
to the earlier glm-5p2 run is explicitly NOT claimed.

## Substrate quality check (HUD doctrine)
- `reward_std = 0.37` on zero_shot -> real within-group spread (trainable signal exists).
- `floor_ok = True` -> the cheapest path (empty/trap) stays below the 0.8 pass threshold.
- zero_shot pass@1 = 0.24 -> NOT saturated, so REx has headroom to lift.

## Outcome
The full 750-episode ablation **completed** inside the 3300 s budget (2709.8 s), so the
time-box/resume machinery acted as an unused safety net rather than a fallback. All five
conditions have full n=150. The McNemar follow-up (`rex/run_ablation_v2.py`) consumed the
output unchanged and found every REx-vs-control difference significant at p<0.0001.

## Honest gaps (carried to 09)
- The gateway throttled deepseek under sustained concurrency (best_of_n stretch slowest);
  another run on a busier gateway could exceed the budget — then the runner emits a real
  `PARTIAL N/750` (numbers honest, remainder NOT fabricated) and resumes on re-run.
- Cross-model comparison to the earlier glm-5p2 attempt is NOT claimed (different proposer).
