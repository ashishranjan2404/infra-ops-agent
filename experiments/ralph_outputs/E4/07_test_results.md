# E4 — 07 Test Results

## 1. Offline unit tests — PASS
```
$ python3 -m pytest test_compare_simple8.py -q
......                                                                   [100%]
6 passed in 0.04s
```
Covers: 8 pinned incidents (no dupes), all 8 validated as real `simple`-family
members, summarize pass-counting / spread / empty-safety, 0.79-fails-/-0.80-passes
threshold.

## 2. Syntax + JSON validity — PASS
```
$ python3 -c "import ast; ast.parse(open('.../compare_simple8.py').read())"  -> syntax OK
$ python3 -m json.tool run_standin.json >/dev/null                            -> valid JSON
```

## 3. Connectivity smoke (which models are usable) — PARTIAL
```
glm-5p2          OK   (returns content)
minimax-m3       OK   (returns content)
deepseek-v4-pro  empty content   (gateway reasoning model -> unusable as-is)
gpt-5.5          empty content   (gateway reasoning model -> unusable as-is)
claude-haiku-4-5 HTTP 400 Bad Request  (Anthropic key rejected / out of credits)
```
=> Only the two Fireworks models return usable plans, so the stand-in uses both
(same provider — isolates the harness from cross-provider prompt bias, per grill R3).

## 4. Real stand-in run — PASS (0 errors, real numbers)
```
E4 simple-8: glm5p2_standin (A) vs minimax_standin (B)  seeds=3  thr=0.8  (46.7s, 0 err)
incident                  A p@1     B p@1    delta   hurts?
cpu_saturation_leaf       0.667     0.000   -0.667    YES
oom_kill                  0.000     0.667    0.667     no
bad_deploy_leaf           1.000     0.333   -0.667    YES
redis_cache_flush         0.333     0.000   -0.333    YES
auth_cert_expiry          1.000     0.000   -1.000    YES
billing_disk_fill         1.000     0.000   -1.000    YES
singleton_node_notready   0.000     0.000    0.000     no
ingest_fd_exhaust         0.000     0.333    0.333     no
OVERALL                   0.500     0.167   -0.333
verdict: B_HURTS  (mean delta -0.333, 5/8 incidents B hurts)
```
These are real deterministic-judge scores over **STAND-IN** frozen models — they
demonstrate the instrument, NOT the trained-vs-trained finding.

## BLOCKER (the actual scientific question cannot be answered tonight)
- **FIREBALL model: BLOCKED.** No FIREBALL training corpus and no fireball-trained
  slug in this repo (`experiments/results/P7_fireball_status.md`; no `*fireball*`
  artifact; not in ROSTER).
- **OpenSRE-GRPO model: not pushed.** `opensre-traj/train_rft.py` exists; the trained
  Qwen slug was never pushed (CLAIMS_EVIDENCE.md).
=> trained-vs-trained "does it hurt?" is **BLOCKED on missing checkpoints**, not on the
harness. The harness is ready; drop in two slugs and re-run.

## Fixes applied during testing
None required — tests and the run passed on first execution; the singleton/oom
0-pass incidents are a property of the stand-in models' plans (real, not a bug).
