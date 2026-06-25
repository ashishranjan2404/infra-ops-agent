# C2 — Verification against success criteria

| Success criterion (from 01/03) | Met? | Evidence |
|---|---|---|
| Real cascade-only synthesis run completes, writes valid JSON | YES | `cascade_synth.json` validates; run exit 0; `run_gpt55.log` |
| Reuses baseline machinery (apples-to-apples; only split + model change) | YES | `cascade_synth.py` imports `rex.harness_synth` features/labels/interpreter/scoring/search read-only |
| Concrete, evidenced comparison vs baseline rule-set | YES | `compare.md` tables; baseline hazards {leak_active, at_replica_limit, rollback_without_deploy, treats_forbidden_category} vs cascade {treats_forbidden_category + scale blanket} |
| Answers "does it find different rules?" meaningfully | YES | Different at hazard/feature level: cascade drops all 3 leaf guards, keeps forbidden-category, adds spurious scale block |
| Held-out comparison on the SAME family | YES | cascade-synth 0.83 vs cascade hand-written 0.864 on cascade held-out; FA% both 0.476 |
| Honest reporting of negatives | YES | deepseek no-op blocker (`run_deepseek_noop.log`); spurious overfit rule; n=1 + model-confound caveats in `compare.md`/`09` |
| No shared core files edited | YES | only `experiments/ralph_outputs/C2/**` written; `git status` shows no `rex/*.py` change from this task |

## Are outputs real (not placeholder)?
- `cascade_synth.json` is produced by an actual Thompson search with gpt-5.5 as the live
  mutation operator (node scores climb 0.395→0.954, not constant placeholders).
- The held-out false-allow/false-block lists are real per-incident actions
  (e.g. `azure_ddos / scale_deployment->ddos-mitigation` false-block on a correct_fix).
- The deepseek no-op was reproduced and root-caused live (raw completion length 0).

## Verdict
COMPLETED. The deliverable (runnable wrapper + real run + structured comparison + honest
caveats) is real. The headline finding — cascade-only synthesis discovers a different,
narrower rule-set that specializes to the forbidden-category guard and drops leaf hazards
it has no supervision for — is supported by the data.
