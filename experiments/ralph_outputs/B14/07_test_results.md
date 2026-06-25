# B14 — Test Results

## 1. Syntax / compile
```
$ python3 -m py_compile cost_model.py cost_per_dollar.py test_cost_model.py
compile OK
```
PASS — all three modules compile under Python 3.13.7.

## 2. Unit tests (cost_model)
```
$ python3 test_cost_model.py
ok  test_cost_scales_with_price
ok  test_judge_is_deterministic_zero_cost_by_default
ok  test_opus_price_values
ok  test_real_claude_prices_not_assumed
ok  test_rex_costs_more_than_zero_shot_same_model
ok  test_unknown_condition_raises
ok  test_unknown_model_uses_assumed_default
ok  test_utilization_scales_output_cost_only
ok  test_zero_shot_is_one_call_rex_is_budget

9 tests passed
```
PASS — 9/9. Covers: real-vs-assumed price flags, Opus price values, call counts per condition,
rex≈N×zero_shot cost, price ordering, utilization affecting output cost only, KeyError on unknown
condition, assumed-default for unknown model, judge=$0.

## 3. cost_model demo (sanity of absolute numbers)
```
opus-4-8 zero_shot       calls= 1.0  in= 1200 out=  840  $0.027000/job
opus-4-8 best_of_n       calls= 4.0  in= 4800 out= 3360  $0.108000/job
opus-4-8 retry_realistic calls= 2.3  in= 2760 out= 1932  $0.062100/job
opus-4-8 rex             calls= 4.0  in= 4800 out= 3360  $0.108000/job
opus-4-8 rex_no_oracle   calls= 4.0  in= 4800 out= 3360  $0.108000/job
```
PASS — rex is exactly 4× zero_shot ($0.108 vs $0.027); deterministic-judge path adds nothing.

## 4. Main script on REAL result JSONs
```
$ python3 cost_per_dollar.py
Ingesting result JSONs:
  [ok]  experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json  model=glm-5p2  n_incidents=42
  [ok]  experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json  model=deepseek-v4-pro  n_incidents=30
Wrote: cost_efficiency.json, cost_efficiency_table.md
10 rows across 2 model(s).
```
PASS — ingested both real A1/A2 pass@1 artifacts, produced 10 rows (5 conditions × 2 models),
wrote both output files. `n_incidents=30` for A2 confirms the `incidents_by_family` fallback works
(A2 has `n_incidents: null` in the JSON).

## 5. Output validation
```
$ python3 -c "import json;d=json.load(open('cost_efficiency.json'));print(list(d.keys()));print(len(d['rows']))"
['metric','definition','cost_basis','output_token_utilization_assumed','sources','price_table','proposer_calls_per_condition','rows']
10
```
PASS — JSON is well-formed, has the metric definition, sources, price table (with assumed flags),
and 10 data rows.

## Fixes applied during testing
- None required for code — it ran clean on first execution. The `null` `n_incidents` in A2 was
  anticipated in the spec (Engineer-1 critique) and the fallback handled it; verified by the
  `n_incidents=30` output.

## Blockers
- **Tokens are not logged** in the result JSONs, so all $ figures are ESTIMATES from the
  call-shape + price model. This is a data-availability blocker on the *measurement*, not on the
  deliverable — the brief explicitly permits documented assumptions here. The script is structured
  to read measured tokens if a future run logs them (see 06).
