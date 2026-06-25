# D9 — 08 Verification

## Success criteria vs outcome
| Criterion | Status | Evidence |
|---|---|---|
| Reuse A12 curriculum_order.json | ✅ | `load_order()` reads it; FileNotFoundError if absent; difficulty never recomputed |
| Curriculum-scheduled training config | ✅ | `training_config.json`: GRPO, 51 incidents, 5 stages, 616-sample budget, progressive unlock + rehearsal, advance criterion, embedded blocker |
| Curriculum-vs-random comparison harness | ✅ | `curriculum_vs_random.py` → `comparison.json`: 3 orderings, multi-seed random, AUC verdict |
| Real, runnable, deterministic artifacts | ✅ | py_compile clean; both JSONs parse; reruns identical |
| Tests pass | ✅ | 10/10 pytest |
| Curriculum ≥ random ≥ anti (mechanism) | ✅ | AUC 0.1677 > 0.0929 > anti; tests 9 & 10 enforce |
| Compute cap ~15 min | ✅ | whole pipeline runs in <1s, no network/GPU |
| Training blocker documented | ✅ | 06/07/09 + `comparison.json.kind` + config `blocker` field |
| No shared core edits | ✅ | only D9/artifacts/ written; A12 read-only |

## Are outputs real (not placeholder)?
- `training_config.json` is generated from the actual A12 order — stage 0 lists
  real incident ids (`cert-expire-leaf-sidecar`, `fd-exhaust-leaf-shipper`, ...);
  budget arithmetic is computed, not stubbed.
- `comparison.json` curves come from running the simulation, not hand-typed.
- Tests exercise real invariants (band coverage, determinism, unit-interval,
  hypothesis), not `assert True`.

## Honest caveat
The comparison's reward numbers are a **declared simulation**, not measured model
reward — verification confirms the *infrastructure and mechanism* are real and
correct, and that the schedule/config are valid inputs for a future real run. It
does NOT verify a claim about the actual policy's curriculum benefit; that
requires the blocked training run.
