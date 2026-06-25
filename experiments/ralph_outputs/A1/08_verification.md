# A1 — 08 Verification

## Success criteria (from 01/03) — all met
1. **Full 42-incident pass@k for >=1 model/condition with non-trivial seeds, deterministic
   judge** — MET. `glm-5p2`, all 42 incidents (12/20/10), **5 conditions**, 3 seeds, 630 real
   episodes, 0 errors, deterministic P0 judge. Result: `artifacts/full_pass_at_k_glm-5p2.json`.
2. **floor_ok over all 42** — MET. `empty_plan_max=0.0`, `trap_max=0.1`, both < 0.8 ->
   `floor_ok=true`. Verified offline AND re-asserted in the runner.
3. **Per-family pass@1/2/5 + Wilson CIs + reward std** — MET (table in 07, JSON `by_family`).
4. **No shared core file edited; artifacts task-namespaced** — MET. Only `rex/eval_pass_at_k.py`
   etc. were *imported*, never written. All outputs under `experiments/ralph_outputs/A1/`.
   The shared `experiments/results/ablation_pass_at_k_glm-5p2.json.partial` was left untouched.
5. **Honest blocker if truncated** — N/A: the full 5-condition sweep completed.

## Are the outputs real (not placeholder)?
Yes. Evidence:
- 630 distinct LLM proposer calls actually executed (run.log progress 50..630, elapsed 1608 s).
- `per_incident_rewards` holds real graded rewards for all 42 incidents × seeds (e.g. rex novel
  = all 1.0; zero_shot cascade mean 0.28 with std 0.33 — non-degenerate spread).
- The numbers are internally consistent: monotone in k, CIs computed from the actual n, and the
  ablation ordering is sensible (rex >> retry ~ best_of_n >> zero_shot; rex_no_oracle collapses
  to baseline-ish on cascades because it loses the oracle feedback — a believable, not invented,
  pattern).

## Independent re-derivation
`summarize_result.py` recomputes pass@k/CI/std straight from the stored rewards and reproduces
the runner's table exactly -> the JSON is self-consistent and the reported metrics are not
hand-entered.

## Caveat carried forward
seeds=3 makes pass@5 an optimistic upper bound (Chen estimator saturates). The headline is
pass@1 ± Wilson CI, which is fully powered at n=126 overall (per-family n=30–60 is directional).
