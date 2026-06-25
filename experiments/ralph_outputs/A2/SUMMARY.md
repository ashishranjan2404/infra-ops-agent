# A2 — SUMMARY

## Task
Complete the 750-episode ablation (5 conditions x 30 incidents x 5 seeds) with a
faster/cheaper model. The prior glm-5p2 run was killed at 175/750 (loop SIGTERM, rc=143).

## Outcome: COMPLETED — full 750/750, real numbers
Ran the full ablation with deepseek-v4-pro (cheaper API via HUD gateway; vLLM is not
available on this box — no GPU — so the "cheaper API" branch is the honest path).
Deterministic P0 judge (no LLM judge). 750/750 episodes, 0 errors, 2709.8 s (~45 min).

| condition | pass@1 | 95% CI | mean | std | n |
|-----------|-------:|--------|-----:|----:|--:|
| zero_shot | 0.240 | [0.18,0.31] | 0.48 | 0.37 | 150 |
| best_of_n | 0.307 | [0.24,0.38] | 0.61 | 0.33 | 150 |
| retry_realistic | 0.313 | [0.24,0.39] | 0.62 | 0.33 | 150 |
| rex | 0.893 | [0.83,0.93] | 0.93 | 0.22 | 150 |
| rex_no_oracle | 0.287 | [0.22,0.36] | 0.59 | 0.33 | 150 |

Floor check OK (empty=0.0, trap=0.1 < 0.8). McNemar (paired, n=150): rex beats every control
at p<0.0001. Key finding: rex_no_oracle ~= best_of_n ~= retry_realistic — REx's lift is
driven by the oracle feedback content, not the tree (honest, load-bearing negative).

## Artifacts (all NEW, task-namespaced — no shared core file edited)
- artifacts/run_ablation_fast.py — resumable, time-boxed wrapper over
  rex/eval_pass_at_k.run_eval with a faster-model default and partial-aware honest reporting.
- artifacts/ablation_pass_at_k_deepseek-v4-pro.json — the full 750-episode result.
- artifacts/ablation_v2_mcnemar_deepseek-v4-pro.json — McNemar paired significance.
- artifacts/run.log — full run log (50-episode progress, 0 errors, final report).

## Reproduce
    set -a; source ~/.zshrc; set +a
    python3 experiments/ralph_outputs/A2/artifacts/run_ablation_fast.py \
        --model deepseek-v4-pro --per-family 10 --seeds 5 --max-workers 16 --max-seconds 3300

## Honest caveats
- The lift mostly disappears without the oracle hint (see 09) — a property of the method.
- One faster model tested; "lifts EVERY model" not proven by this run alone.
- Per-REx node counts not logged this round (recommended next step).
