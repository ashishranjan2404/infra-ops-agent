# I6 — 08 Verification

## Success criteria (from 01) vs reality
| Criterion | Met? | Evidence |
|---|---|---|
| Script runs on real data | YES | `failure_taxonomy.py` ingests 12 probe + 45 hud real rollouts, exits 0 |
| Buckets 0/failed rollouts by failure type using rex/scoring signals | YES | buckets derived from `rex.scoring.failed_checks` (trap_action/root_cause/correct_fix_missing/not_resolved) |
| Reports the distribution | YES | `failure_report.json` + `.md` with per-bucket counts, %, tags, by-scenario |
| Agrees with probe pre-computed failed_checks | YES | `test_probe_recompute_matches_stored_failed_checks` passes; trap/clean rows bucket consistently |
| Tests pass | YES | 7/7 pytest |
| No shared core file edited | YES | only reads/imports rex.scoring; all artifacts under I6/ |

## Outputs are REAL, not placeholder
- 57 rollouts come from on-disk files (`rex/runs/diagnostic_probe_*.jsonl`,
  `rex/runs/hud/*.jsonl`), not synthesized.
- HUD scores are re-derived deterministically from captured `{plan, scenario, sim_result}`
  payloads via the actual project scorer — the replay-trap test proves the path matches
  `rex.scoring`.
- The headline finding (singleton_node_notready: 20/20 `no_fix` via safe-abstain) is
  independently consistent with `harness_synth_v2.json`, which flags that scenario's
  cordon/drain as `UNSEEN in train` / `last_ready_node` hazard — i.e. the model is
  correctly refusing the trap and abstaining. Cross-source corroboration.

## Reproducibility
`REX_JUDGE_MODE=deterministic` is forced and `deterministic_judge` injected → no network,
identical output across runs. `python3 failure_taxonomy.py` regenerates both reports.
