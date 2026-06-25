# A15 — Verification against success criteria

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | Transformed spec validates (0 errors) via `python -m sim.spec validate` | ✅ | 07 §3: `1/1 specs valid` |
| 2 | `alerting=noisy`, `monitoring_degrades=True` (obs + assertions), guns buried deeper | ✅ | variant lines 81/82/122, buried_under 40→120 |
| 3 | Physics unchanged (root_cause, canonical_fix, original topology preserved) | ✅ | `test_physics_unchanged` PASS |
| 4 | Baselines not modified in place | ✅ | 07 §5: git shows `??` not `M`; transform writes only to artifacts/ |
| 5 | pytest green | ✅ | 07 §4: 7 passed |
| 6 | Reusable transform runnable on any baseline (one command) | ✅ | ran on #55 and #44, both clean |

## Are outputs real (not placeholder)?
Yes:
- `noisy_metrics_transform.py` is executable, runs, and self-validates against the real
  `sim.spec` loader/validator.
- `55-github-network-partition-noisy.yaml` is a genuine YAML produced by the script and
  accepted by the official CLI validator as a 6-node/5-edge scenario.
- `test_...py` runs 7 real assertions, all green.

## Honest qualifier
Verification confirms the variant is **schema-valid and reward-invariant with a degraded
observation layer**. It does NOT claim a measured change in agent success rate, because the
fast sim does not yet consume the alerting/buried_under fields (documented blocker, 07 §blocker / 09).
This is the correct, scoped deliverable — not a fabricated behavioral result.
