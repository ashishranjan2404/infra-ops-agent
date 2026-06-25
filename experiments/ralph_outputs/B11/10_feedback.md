# 10 — Feedback for the next task

The richest reusable asset for any "robustness / sensitivity" task is
`rex/runs/ablation.json`, which uniquely stores PER-ATTEMPT graded rewards
(`per_incident[arm][incident] = [r...]`) — most other run files
(`frontier.json`, `harness_synth_v2.json`) store only pre-aggregated pass-rates, so
you cannot re-threshold them without re-running. When sweeping a binarisation cutoff,
first list the OBSERVED reward bands: this reward is a weighted sum of mostly-binary
terms, so it occupies ~10 discrete values and large stretches of the [0,1] axis are
empty — several thresholds will tie, and that tie is a finding (it shows where the
mass sits), not a bug to hide. Keep robustness artifacts standalone (copy the ~10-line
`binary_pass`/`wilson_ci` estimators rather than importing `rex.eval_pass_at_k`, which
drags in `agent.llm` and needs network/keys), and pin the copies with an offline
equivalence test so the fork can't silently drift. Finally, be disciplined about the
claim: with 5 incidents x 3 seeds the effective n is ~5 (clustered), so claim
"rank-order/gap preserved," never "significant at every cutoff."
