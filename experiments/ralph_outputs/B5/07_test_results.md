# 07 — Test Results

## 1. Syntax / compile
```
$ python3 -m py_compile experiments/ralph_outputs/B5/artifacts/frontier_pass_at_k.py
COMPILE OK
```

## 2. Scenario availability (all 5 frontier.py incidents load)
```
ok oom_kill
ok cpu_saturation_leaf
ok bad_deploy_leaf
ok gcp_service_control
ok singleton_node_notready
```

## 3. Unit tests (no network) — pinning summarize()
```
$ python3 -m pytest experiments/ralph_outputs/B5/artifacts/test_frontier_pass_at_k.py -q
......                                                                   [100%]
6 passed in 0.03s
```
Two tests initially FAILED and were fixed (honest record):
- `test_basic_passk_monotone_and_bounded`: tolerance `1e-9` was tighter than
  `summarize`'s 4-dp rounding (0.6667 vs 0.66666…) → relaxed to `1e-3`.
- `test_partial_credit_does_not_pass` (old): asserted `pass@5 == 0` for `[0.4,0.4,0.4]`,
  but the single-source estimator returns **1.0** when n−c < k (n=3, c=0, k=5). That is the
  estimator's *documented* contract, not a bug. Split into
  `test_partial_credit_does_not_pass_at_1` (headline pass@1 = 0, correct) plus a new
  `test_passk_extrapolation_edge_when_n_lt_k` that PINS the n<k=1.0 edge so it's explicit.

## 4. Connectivity probe (which models actually run)
```
deepseek-v4-pro  reward=0.400 wall=6.8s   (gateway OK)
gpt-5.5          reward=0.400 wall=7.5s   (gateway OK)
gemini-3.1-pro   reward=1.000 wall=7.0s   (gateway OK, but slow/variable under load)
claude-haiku-4-5 -> HTTP 400 (Anthropic direct: model id / out-of-credits)  [BLOCKED]
```
Per machine memory ("Anthropic out of credits → use gateway/deepseek"), Anthropic-direct
models are excluded from the real run; gateway models used instead.

## 5. Real subset frontier run (under the 15-min cap)
```
=== Frontier pass@k — 2 models x 2 incidents x 3 seeds, REx budget 3, threshold 0.8 ===
--- deepseek-v4-pro ---
  [deepseek-v4-pro] oom_kill            baseline_mean=0.600  rex_mean=1.000  (seeds=3)
  [deepseek-v4-pro] gcp_service_control baseline_mean=0.550  rex_mean=1.000  (seeds=3)
--- gpt-5.5 ---
  [gpt-5.5] oom_kill            baseline_mean=0.400  rex_mean=1.000  (seeds=3)
  [gpt-5.5] gcp_service_control baseline_mean=0.300  rex_mean=1.000  (seeds=3)

model             cond        pass@1          95% CI  pass@2  pass@5   mean    std    n
deepseek-v4-pro   baseline     0.167     [0.03,0.56]   0.333   0.833   0.57   0.23    6
deepseek-v4-pro   rex          1.000     [0.61,1.00]   1.000   1.000   1.00   0.00    6
gpt-5.5           baseline     0.000     [0.00,0.39]   0.000   0.000   0.35   0.16    6
gpt-5.5           rex          1.000     [0.61,1.00]   1.000   1.000   1.00   0.00    6

model                 pass@1 lift (REx-base)     mean lift
deepseek-v4-pro                       +0.833        +0.425
gpt-5.5                               +1.000        +0.650

-> frontier_pass_at_k_result.json  (558.7s)
```
**0 errors**, wall **558.7s (~9.3 min)**. JSON validated: 6 top-level keys, both models
present with full baseline+rex pass@k blocks, `n_errors=0` each.

## Verdict
Script compiles, unit-tested (6/6), and produced REAL frontier pass@k for 2 working
gateway models × 2 incidents × 3 seeds within the compute cap. PASS.
