# D7 — 07 Test Results

All commands run from `/Users/mei/rl`. Real command output below.

## T1 — py_compile (harness compiles)
```
$ python3 -m py_compile experiments/ralph_outputs/D7/artifacts/d7_train_eval.py && echo PY_OK
PY_OK
```
**PASS.**

## T2 — YAML parse + mini-YAML fallback parity
```
YAML_OK keys: ['baselines', 'eval_families', 'max_tokens', 'model', 'n_eval_incidents', 'n_exemplars']
 yaml vs mini keys match: True | eval_families: ['simple', 'cascade']
```
**PASS.** `pyyaml` and the built-in fallback parser produce identical keys.

## T3 — Dry-run (zero network) produces full result object
```
$ python3 .../d7_train_eval.py --dry-run --config .../d7_cascade_only.yaml --out .../d7_results_dryrun.json
DRYRUN_OK
```
Result object has `_meta`, `cascade`/`mixed`/`none` × `simple`/`cascade`, `transfer`.
CI bounds within [0,1]. **PASS.**

## T4 — Leakage guard (train ∩ eval == ∅) — including the Ouroboros `mixed` fix
```
NO_LEAKAGE_ASSERT: True
```
Asserted across all 3 configs × 2 families. After the Eng-A fix, the `mixed` pool also
subtracts eval names. **PASS.**

## T5 — Determinism of split
`Random(1337)` → identical `train_names`
(`['github_network_partition', 'aws_kinesis_cell_manager', 'azure_ddos']`) on repeated
dry-runs. **PASS.**

## T6 — REAL reduced LLM run (glm-5p2, deterministic judge)
Config: `d7_smoke.yaml` (n_eval_incidents=2, seeds=2 → 24 LLM calls). First real run
completed exit 0 in **278 s (~4.6 min)** — within the 15-min cap. Per-cell results
(this is the leakage-clean re-run after the `mixed` fix; see `d7_results_smoke.json`):

| config | family | pass@1 | CI95 | mean | std | n |
|---|---|---|---|---|---|---|
| cascade | simple | 1.0 | [0.51, 1.0] | 1.000 | 0.000 | 4 |
| cascade | cascade | 0.0 | [0.0, 0.49] | 0.000 | 0.000 | 4 |
| mixed | simple | 1.0 | [0.51, 1.0] | 1.000 | 0.000 | 4 |
| mixed | cascade | 0.0 | [0.0, 0.49] | 0.375 | 0.375 | 4 |
| none | simple | 1.0 | [0.51, 1.0] | 1.000 | 0.000 | 4 |
| none | cascade | 0.0 | [0.0, 0.49] | 0.188 | 0.325 | 4 |

Transfer deltas: H1 = 0.0, H2 = 0.0 (both pass@1-based; both saturated).

Observation worth flagging: while pass@1 is floor (0.0) on cascade for all configs, the
**mean partial reward** ranks `mixed` (0.375) > `none` (0.188) > `cascade-only` (0.0).
i.e. at this budget cascade-only exemplars gave the *lowest* partial credit on cascade —
the opposite of the "helps cascade" hypothesis — though no config clears the 0.8 pass
bar, so this is a sub-threshold trend on n=4, not a result. Run-to-run this mean varied
(first pre-fix run had cascade-only cascade mean=0.188), underscoring the under-powered
caveat. Simple stays at ceiling (1.0, std 0) under every config → no over-diagnosis
harm visible at this budget.

The frozen glm-5p2 solves simple incidents and fails the cascade pass bar regardless of
the exemplar pool at this tiny budget.

**PASS** (real numbers produced; see verification for interpretation + the
under-powered caveat).

## Fixes applied during testing
1. **Ouroboros Eng-A #1:** `mixed` baseline now subtracts eval incidents from its pool
   (`exemplar_block_for` takes `eval_names`). Re-validated: T1, T3, T4 still pass.
2. No other fixes required — dry-run and real path both succeeded first try.
