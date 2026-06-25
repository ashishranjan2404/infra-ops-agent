# A12 — SUMMARY

## Task
Build a curriculum ordering (easy → hard) of the CIDG incident set for
curriculum-learning experiments.

## Deliverable
A deterministic, model-free curriculum generator + the resulting ordered incident
list with a per-incident difficulty signal and feature breakdown.

- `artifacts/build_curriculum.py` — parses `scenarios/cidg/generated/*.yaml`, joins
  `registry.json`, computes an 11-feature difficulty vector per incident, scores it
  with a documented weight dict, sorts easy→hard (stable tiebreak). `--print` shows
  the ranked table.
- `artifacts/curriculum_order.json` — the ordering: `signal`, `weights`,
  `order_easy_to_hard` (ids), `n`, and `incidents[]` each with `difficulty`, `rank`,
  `family`, `failure_class`, full `features`.
- `artifacts/test_curriculum.py` — validates coverage, monotonicity, simple-vs-real
  split, determinism, id-uniqueness. PASS.

## Difficulty signal
Composite static-structural score (a documented prior, not measured pass-rate):
weighted sum of topology size + the "trap" booleans that define a hard incident
(hidden_root, cascades, loudest_alert_not_cause, buried_gun_exists, hysteresis,
monitoring_degrades), buried-evidence depth, red-herring count, SLO count, multi-step
fix. Trap booleans dominate so single-leaf incidents sit at the easy end and real
cascades at the hard end — matching the SIMPLE/HARD tiers hand-coded in
rex/curriculum.py.

## Result (current run)
- 51 incidents ordered, difficulty range 0.90 → 17.00.
- Easiest: single-leaf clones (cert-expire-leaf-sidecar, billing_disk_fill, ...).
- Hardest: real multi-service cascades (slack_tgw_fd_exhaustion, launchdarkly_cold_cache,
  github_network_partition).
- Idempotent: scenario set is being grown by parallel workers; generator re-run last.

## Caveats
- Difficulty is a structural prior, not learner-perceived difficulty. Coarse simple-vs-
  real split is trustworthy; fine within-tier order is provisional (ties exist; break on
  the emitted feature vector). Next step: correlate vs empirical pass@k
  (rex/eval_pass_at_k.py) and refit weights.
- No shared core file modified; ids are registry keys, consumable by
  rex/harness.py:load_scenario.

## Run
    python3 experiments/ralph_outputs/A12/artifacts/build_curriculum.py --print
    python3 experiments/ralph_outputs/A12/artifacts/test_curriculum.py
