# F8 · 07 Test Results (real command output)

## A. `verify_repro.py` against the live repo — PASS, exit 0
```
# verify_repro  sha=8a12b41465  py=3.13.7
PASS     AVAILABLE  code.repo_public            observed=True
PASS     AVAILABLE  code.entrypoints            observed=True
PASS     AVAILABLE  code.deps_runtime           observed=True
PASS     AVAILABLE  code.deps_gpu               observed=True
PASS     AVAILABLE  code.dep_yaml               observed=True
PASS     AVAILABLE  code.dep_requests           observed=True
PASS     SEEDED     seed.tree                   observed=True
PASS     SEEDED     seed.eval_sweep             observed=True
PASS     SEEDED     seed.ablation               observed=True
PASS     AVAILABLE  seed.det_judge              observed=True
PASS     AVAILABLE  repro.replay_double_grade   observed=True   <-- empirical: graded twice, equal
PASS     AVAILABLE  data.trajectories_committed observed=True
PASS     AVAILABLE  data.scenarios_base         observed=True
PASS     AVAILABLE  data.simple_generator       observed=True
WARN     PARTIAL    data.generated_committed    observed=False  <-- 53 YAMLs untracked (expected)
WARN     PARTIAL    data.doc_drift              observed=True
PASS     AVAILABLE  weights.roster              observed=True
PASS     AVAILABLE  weights.open_recipe         observed=True
WARN     BLOCKED    weights.checkpoint          observed=False  <-- no committed weights (expected)
counts: {'AVAILABLE': 13, 'SEEDED': 3, 'PARTIAL': 2, 'BLOCKED': 1} | hard_fail: False
EXIT=0
```
Every AVAILABLE/SEEDED claim verified True. The two WARNs and the BLOCKED are the
*intended* honest gaps — they do not fail the run. `replay_double_grade` empirically
confirms the deterministic judge is stable (the Ouroboros Engineer-A concern).

## B. Manifest JSON validity + invariants — PASS
```
manifest OK: n_items=21 counts={'AVAILABLE':13,'SEEDED':4,'PARTIAL':3,'BLOCKED':1} sha=8a12b41465
```
`sum(counts) == n_items == len(items) == 21`. Valid JSON, SHA present.
(Note: the manifest tallies 4 SEEDED / 3 PARTIAL vs the script's 3 / 2 because the
manifest includes two extra documentation-only rows — `code.control_flow_det` (SEEDED)
and `compute.cost_ledger` (PARTIAL) — that aren't mechanically checkable. This is
intentional and noted; the script only asserts the *checkable* subset.)

## C. Checklist structural parse — PASS (all 6 sections present)
```
FOUND: ## 1. Code
FOUND: ## 2. Data
FOUND: ## 3. Model weights
FOUND: ## 4. Randomness
FOUND: ## 5. Compute
FOUND: ## Summary
```

## D. Manifest SHA == git HEAD — PASS
```
SHA MATCHES HEAD   (8a12b414652f6a014dac9abce1e1681067185db8)
```

## E. Python syntax — PASS
```
py_compile OK
```

## Fixes applied during testing
- None required: `verify_repro.py` ran clean on the first execution and the
  `replay_double_grade` import path resolved against `rex.scoring`. The only manual
  reconciliation was documenting the manifest-vs-script count delta (B), which is
  expected, not a bug.
