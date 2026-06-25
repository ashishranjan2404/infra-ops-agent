# I6 — SUMMARY: Failure-mode taxonomy of REx rollouts

## Deliverable
A read-only analysis tool that buckets every failed REx rollout into failure modes
derived from `rex/scoring.py` signals, run on real on-disk rollout data.

- `artifacts/failure_taxonomy.py` — ingest + bucket + report (imports rex.scoring, no edits)
- `artifacts/test_failure_taxonomy.py` — 7 pytest cases, all pass
- `artifacts/failure_report.json` / `.md` — generated distribution (real data)

## Key trick
HUD traces (`rex/runs/hud/*.jsonl`) store the `rex.score_plan` REQUEST payload
`{plan, scenario, sim_result}` but not the score response, so the tool replays
`rex.scoring.score_plan` + `failed_checks` over the captured tuple with the deterministic
(hermetic) judge to reconstruct per-rollout signals. Probe jsonl rows are ingested directly.

## Result (57 real rollouts: 12 probe + 45 unique HUD)
- Failure tail (score<1 or any failed_check): 36 of 57; clean wins 21; strict 0-reward 0.
- Primary buckets of the 36 failed: no_fix 22, wrong_root_cause 7, trap_taken 7, not_resolved 0.
- By scenario: singleton_node_notready 20/20 no_fix (safe-abstain penalized as failure),
  oom_kill 6 trap_taken (scale/clear_cache on a leak), gcp_service_control 7
  wrong_root_cause (blames downstream victim) + 2 attempted-but-blocked traps.

## Headline insight
The reward scores correct safe abstention on an unfixable scenario as `no_fix` — a
reward-design finding, not a model failure. Surfaced via the `safe_abstain` tag.

## Status
completed — real plan + spec + runnable tool + passing tests + real distribution; no shared
core file touched. Limitation: small, scenario-imbalanced N (directional, not statistical).
