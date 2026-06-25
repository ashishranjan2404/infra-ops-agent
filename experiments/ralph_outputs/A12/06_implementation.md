# A12 — 06 Implementation

## What I built (real artifacts)
1. **`artifacts/build_curriculum.py`** — deterministic, model-free curriculum
   generator. Parses every `scenarios/cidg/generated/*.yaml`, joins `registry.json`
   for `family` + `red_herrings`, computes an 11-feature vector per incident, scores
   it with a documented weight dict, sorts easy→hard (stable tiebreak on id), and
   writes `curriculum_order.json`. Has a `--print` mode for a ranked table.
2. **`artifacts/curriculum_order.json`** — the deliverable. Contains `signal`,
   `weights`, `order_easy_to_hard` (ordered incident ids), `n`, and `incidents[]`
   with per-incident `difficulty`, `rank`, `family`, `failure_class`, and the full
   `features` breakdown.
3. **`artifacts/test_curriculum.py`** — self-contained validator (no pytest dep):
   coverage, monotonicity, simple-vs-real split, determinism, id-uniqueness.

## Difficulty signal
Composite static-structural score (a documented **prior**, not measured pass-rate):
`difficulty = Σ W[k]·feature[k]` over topology size, `hidden_root`, `cascades`,
`loudest_alert_not_cause`, `buried_gun`, buried-evidence depth, `hysteresis`,
`monitoring_degrades`, red-herring count, SLO count, and multi-step fix. The four
"trap" booleans dominate so the 8 simple-leaf clones (all-zero traps) sit at the easy
end and the real-outage cascades at the hard end; size/counts are tiebreakers.

## Result (current run)
- **49 incidents** ordered (the scenario set was being grown by parallel workers;
  the generator was re-run last and is idempotent).
- Families: 8 simple, 14 cascade, 10 novel, 17 unknown (not yet in registry.json).
- Difficulty range **0.90 → 17.00**. Easiest: leaf clones (`cert-expire-leaf-sidecar`,
  `fd-exhaust-leaf-shipper`, ...). Hardest: real multi-service cascades
  (`slack_tgw_fd_exhaustion`, `launchdarkly_cold_cache`, `github_network_partition`).

## Shared-core safety
No `rex/*.py`, `sim/*.py`, `agent/*.py`, or `experiments/*.py` was edited. The
artifact maps directly onto the existing SIMPLE→HARD tiers in `rex/curriculum.py`
(read-only reference) and uses registry-key ids that `rex/harness.py:load_scenario`
already consumes, so it is drop-in for a curriculum-learning loop.

## Run commands
```
python3 experiments/ralph_outputs/A12/artifacts/build_curriculum.py --print
python3 experiments/ralph_outputs/A12/artifacts/test_curriculum.py
```
