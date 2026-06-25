# D12 — SUMMARY

**Task:** Run RFT with group size 8 (currently 4) — does more rollouts help? Build a group-size-8
config + analysis of expected variance reduction. Grounded in opensre-traj/train_rft*.py.

## The group-size param
`--group G` in train_rft_v2.py, threaded to Job.start(group=G), ts.run(group=G), and
trainer.step(group_size=G). Rollouts/step = tasks * G. Logged baseline used G=4 (10 tasks ->
40 rollouts/step, runs/train_qwen3-8b_v2.jsonl).

## Deliverables (artifacts/)
- group8_config.yaml — group=8 run config (parses, group==8).
- run_group8.sh — launcher for train_rft_v2.py --group 8 (+ --smoke); does not edit core files.
- variance_analysis.py — derives within-group sigma from the REAL log and projects SEM(4)->SEM(8).
- group8_smoke.log — LIVE harness proof: group=8 ran, n=16 = 2 tasks x 8, "SMOKE OK".

## Result of the analysis (grounded)
within-group sigma ~ 0.069. Group 4->8 cuts the GRPO baseline-mean standard error by 29.3%
(= 1 - 1/sqrt(2)) and its variance by 50%, at 2x rollout cost (40->80/step).

## Verdict: does more rollouts help?
Modestly yes, statistically (cleaner advantage estimate). But it is a second-order fix — the
baseline-mean SEM (~0.034) was already small vs sigma (~0.069); the flat-reward root cause is too
few tasks + low headroom, which more rollouts don't address. Worth doing only after the v2
task/headroom fixes.

## Blocker
Full 30-step group-8 run (2400 rollouts) exceeds the ~15-min cap; trainable slug opensre-qwen3-8b
404s (needs forking). The smoke still ran group=8 end-to-end, proving the config. Status: completed
(real plan+spec+validated artifacts+live smoke; full run blocked & documented).
