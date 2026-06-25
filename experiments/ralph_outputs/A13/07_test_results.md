# A13 — Test Results

## 1. Schema validation of the 3 new specs
```
$ python3 -m sim.spec validate "scenarios/cidg/generated/8?-*.yaml"
OK    scenarios/cidg/generated/80-multi-cert-poolleak.yaml  [multi-cert-poolleak]  4 nodes / 2 edges / rc=cert_expire
OK    scenarios/cidg/generated/81-multi-rollout-cacheflush.yaml  [multi-rollout-cacheflush]  4 nodes / 2 edges / rc=bad_revision
OK    scenarios/cidg/generated/82-multi-fdexhaust-cpustarve.yaml  [multi-fdexhaust-cpustarve]  4 nodes / 2 edges / rc=fd_exhaust
...
19/19 specs valid   (glob also matched pre-existing 8x specs; all OK)
```

## 2. Full-suite regression (no other spec broken)
```
$ python3 -m sim.spec validate "scenarios/cidg/generated/*.yaml" | tail -1
51/51 specs valid
```
(48 pre-existing + my 3 = 51.)

## 3. Pytest — patch-free tests against the current engine
```
$ python3 -m pytest experiments/ralph_outputs/A13/artifacts/test_multifault.py -q
......                                                                   [100%]
6 passed in 0.07s
```
Cases: `test_found_three_specs`, `test_specs_validate`, `test_two_distinct_fault_locations`,
`test_each_fault_has_its_own_slo_victim`, `test_each_fault_has_engine_valid_fix_step`,
`test_primary_runs_and_clears_in_unpatched_engine`.

## 4. Patch verification (on throwaway copy `/tmp/mfpatch/b`, repo untouched)
```
80-multi-cert-poolleak       faults=['auth-gw','session-pool']   resolved_pre=False
   after_one=False  after_both=True
81-multi-rollout-cacheflush  faults=['api-edge','result-cache']  resolved_pre=False
   after_one=False  after_both=True
82-multi-fdexhaust-cpustarve faults=['conn-router','rank-svc']   resolved_pre=False
   after_one=False  after_both=True
PATCH OK: all 3 are genuine conjunctive 2-fault scenarios
```
Interpretation: with the patch applied, fixing **one** fault is NOT enough (`after_one=False`); both
must be cleared (`after_both=True`). This is exactly the conjunctive multi-fault property.

## 5. Core-file integrity
```
$ diff -q /tmp/engine_orig.py sim/engine.py   # → identical (engine.py untouched)
$ diff -q /tmp/spec_orig.py   sim/spec.py     # → identical (spec.py untouched)
```

## Fixes applied during development
- Confirmed via early directory scan that numbers 80/81/82 already host OTHER files; used unique
  `*-multi-*` filenames to avoid any collision (verified: `ls | grep multi` → exactly my 3).
- Ensured each spec has a `required` edge and two smoking_guns so `assertions.cascades` and
  `assertions.buried_gun_exists` validate (would otherwise FAIL per `sim/spec.py:346,352`).
- Gave each fault a distinct downstream SLO victim so the secondary fault can't be incidentally
  satisfied by the primary fix (construct-validity fix from `05_ouroboros.md` P2.1).

No failing tests remain.
