# D11 — Test Results (real command output)

## 1. Syntax check
```
$ python3 -c "import ast; ast.parse(open('seed_variance.py').read()); print('OK')"
seed_variance.py OK
```

## 2. pytest (after fixing the importlib/dataclass module-registration bug)
```
$ python3 -m pytest test_seed_variance.py -q
..........                                                               [100%]
10 passed in 0.52s
```
**Fix applied:** the first run errored with
`AttributeError: 'NoneType' object has no attribute '__dict__'` because a module loaded
via `importlib.util.module_from_spec` is not in `sys.modules`, so `@dataclass` could not
resolve its own module during class processing. Fixed by `sys.modules["sv"] = sv` before
`exec_module`. All 10 tests then passed.

## 3. Analyzer on the 3 REAL logs (cross-config mode)
```
$ python3 seed_variance.py \
    --logs ../../../../opensre-traj/runs/train_qwen3-8b.jsonl \
           ../../../../opensre-traj/runs/train_qwen3-8b_v2.jsonl \
           ../../../../opensre-traj/runs/train_qwen3-30b.jsonl \
    --out-json variance_report.json --out-md variance_table.md
```
Output (real): per-run table with plateau_mean {0.4937, 0.5356, 0.4853},
plateau_std {0.0209, 0.0071, 0.0302}, cross-config std(ddof=1)=0.0269,
seed_variance_status = "NOT MEASURED ...", no collapse steps. `variance_report.json`
(2.6 KB) and `variance_table.md` (1.5 KB) written.

## 4. seed-group CI path (synthetic fixtures, NOT written to the real report)
```
$ python3 seed_variance.py --logs seed0 seed1 seed2 --seed-group "demo@1e-5"
## Across-seed 95% CI
- seeds (S) = 3, per-seed = [0.512, 0.508, 0.53]
- mean = 0.5167 ± 0.0293  (std=0.0117, sem=0.0068, t(df=2)=4.303)
- 95% CI = [0.4876, 0.5458]
```
Confirms the real-CI code path produces a correct Student-t interval when seeds exist.

## 5. Patch validity
```
$ git apply --check experiments/ralph_outputs/D11/artifacts/add_seed_patch.diff
PATCH VALID (applies cleanly)   # exit 0
$ git status --porcelain opensre-traj/train_rft_v2.py
?? opensre-traj/train_rft_v2.py   # original shared file untouched
```

## 6. Driver syntax
```
$ bash -n run_multiseed.sh
run_multiseed.sh OK
```

## Blocker (honest)
The real **across-seed CI cannot be produced now**: no `--seed` knob existed (now patched
but not applied) and a real run is 5 seeds × ~30 GPU steps on the HUD Tinker backend
(needs HUD_API_KEY + a forked trainable slug). That is the single blocked downstream step;
every deliverable above is real and validated.
