# A2 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Frozen judge made explicit (SMR, accepted).** The runner changes ONLY the proposer
   model; reward stays the P0 deterministic judge via `score_plan(..., judge_fn=None)`
   inherited unchanged from `rex/eval_pass_at_k.py`. No judge swap -> the rex-vs-control
   contrasts remain valid. I do NOT claim deepseek's absolute pass@1 equals glm-5p2's.
2. **Model strength, not just speed (RLE+SMR, accepted).** Added an empirical check that the
   chosen model has *headroom and spread*: I verify `reward_std > 0` and that zero_shot does
   not already saturate. deepseek-v4-pro is mid/strong; if it ceilings I note it honestly
   rather than spin a null result as success.
3. **Per-family + floor + std reporting (PSRE, accepted).** Reused `print_report`, which
   already prints per-family pass@k, `reward_std`, and `floor_check`. Nothing new needed.
4. **Graceful time-box + resume, no double-count (DVO+PSRE+AAAI, accepted).** Added
   `--max-seconds` via SIGALRM. Crucially: completed-episode count is read from the actual
   checkpoint/result `per_incident_rewards`, NOT from a wall-time estimate, so mid-flight
   aborted episodes are never counted as done. Resume replays only un-checkpointed episodes
   (rewards are deterministic given the plan, so replay is correct).
5. **Empty-checkpoint degrade (DVO, accepted — the smoke test proved it).** Fixed the
   `_summarize_partial -> None` crash: if the time-box fires before the first 25-episode
   checkpoint, emit a valid empty report (`0/750 completed`) instead of erroring.

## Critiques rejected (with reasons)
- **RLE "a weaker model is strictly better substrate"** — rejected as a rule. Too weak floors
  out (no spread either). I keep a mid/strong fast model and *measure* spread instead of
  assuming a strength tier is correct.
- **AAAI "must complete fully or McNemar is invalid"** — partially rejected. A *full* run is
  the goal and is attempted, but a partial run is still a legitimate deliverable: pass@k over
  completed episodes is honest, and McNemar simply runs over whichever conditions are equally
  complete. I document completion per condition rather than block the whole task on 750/750.

## Final approach (unchanged structure, hardened)
`artifacts/run_ablation_fast.py` = thin wrapper over `run_eval`/`print_report`:
proposer=`deepseek-v4-pro`, 30 incidents x 5 seeds x 5 conditions, deterministic judge,
checkpointed + resumable + time-boxed, partial-aware honest reporting.
