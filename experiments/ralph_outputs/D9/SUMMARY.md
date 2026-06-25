# D9 — SUMMARY

**Task:** Run curriculum learning (easy→hard) over the CIDG incident set; reuse
A12's ordering; build a curriculum-scheduled training config + a curriculum-vs-
random comparison harness. ~15 min cap.

## What got done
- **Reused A12** `curriculum_order.json` (51 incidents, static-structural
  difficulty 0.9→17.0, trap-weighted, non-decreasing).
- **`curriculum_schedule.py`** — bands the A12 order into stages with progressive
  unlock + rehearsal weighting; emits a GRPO-style **`training_config.json`**
  (51 incidents, 5 stages, 616-sample budget, advance criterion, group_size 8).
  Supports curriculum / random / anti orderings on one budget.
- **`curriculum_vs_random.py`** — comparison harness over all three orderings;
  emits **`comparison.json`**. Real gradient training is blocked (no GPU), so it
  runs a transparent, labeled competence-vs-difficulty **simulation** with a
  one-function seam to swap in real `rex.scoring.score_plan` eval.
- **`test_curriculum_schedule.py`** — 10/10 pytest pass.

## Result (SIMULATED — training blocked)
`mean_reward` per stage, eval over all 51 incidents:
- curriculum 0.12→0.20, random 0.07→0.13, anti 0.05→0.12
- **curriculum AUC 0.168 > random 0.093 (Δ+0.075) > anti**; hypothesis encoded
  as tests 9 & 10.

## Blocker
No GPU / training backend in this frozen-LLM env. Schedule + config are real
runnable inputs; comparison numbers are a declared proxy, not measured model
reward. Plugging in real rollouts = replace `simulate_run`.

## Artifacts
`D9/artifacts/{curriculum_schedule.py, curriculum_vs_random.py,
test_curriculum_schedule.py, training_config.json, comparison.json}`

## Safety
Only `D9/artifacts/` written; A12 read-only; no shared-core edits.
