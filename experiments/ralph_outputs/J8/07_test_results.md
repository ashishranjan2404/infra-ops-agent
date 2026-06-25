# 07 — Test Results

## T1–T5: pytest (engine invariants + demo run)
```
$ python3 -m pytest experiments/ralph_outputs/J8/artifacts/test_demo_trace.py -q
....                                                                     [100%]
4 passed in 0.09s
```
- T1 fault injected, unresolved at open — PASS
- T2 `restart_pod` band-aid does NOT resolve `cpu_starve` — PASS
- T3 `scale_deployment` causal fix resolves — PASS
- T4/T5 `demo_trace.py --fast` exits 0 AND transcript contains
  `[ORACLE] root still active` and `RESOLVED` — PASS

## Demo run (real captured output via record_demo.sh)
```
[record_demo] python3: /Library/Frameworks/Python.framework/Versions/3.13/bin/python3
[record_demo] capturing plain-text transcript -> .../demo_output.txt

=== SRE-Degrees: autonomous incident response demo ===
scenario : 44-search-cpu-starve.yaml
simulator: sim/engine.py (deterministic Tier-A graph kernel)

sre-degrees$ incident open --auto
  [PAGE] SLO breach on 'search-api' — error rate over threshold
  search-api       error= 70.0%  p99=  50.0ms
  hidden root-cause kind = cpu_starve @ search-api (unknown to the agent)

sre-degrees$ agent diagnose
  hypothesis : degradation localizes to search-api
  category   : resource/cpu pressure (from metric shape)

sre-degrees$ agent act --tool restart_pod --target search-api
  search-api       error= 70.0%  p99=  50.0ms
  [ORACLE] root still active — restart did not clear the fault
  feedback -> refine: restart treats symptoms, not cpu starvation

sre-degrees$ agent act --tool scale_deployment --target search-api
  search-api       error=  0.0%  p99=  50.0ms
  [ORACLE] root cleared AND SLOs green — incident RESOLVED

sre-degrees$ incident summary
  attempts     : 2 (1 refinement)
  fix          : scale_deployment @ search-api
  resolved     : yes
=== end of trace ===

[record_demo] trace exit code: 0
[record_demo] asciinema NOT installed — skipping .cast (transcript is the fallback).
```
Exit code: **0** (resolved). The 70%→0% error transition is engine-computed, not printed
literals — confirmed by the pytest assertions.

## YAML validation
```
$ python3 -m sim.spec validate scenarios/cidg/generated/44-search-cpu-starve.yaml
OK    .../44-search-cpu-starve.yaml  [search-cpu-starve]  1 nodes / 0 edges / rc=cpu_starve
1/1 specs valid
```

## Fixes applied during testing
- **Rejected initial scenario `21-leaf-oom-positive.yaml`**: its SLO names `pod_restarts`, a
  metric `sim/engine.py` does not track → `is_resolved` raised `KeyError: 'pod_restarts'`.
  Switched the demo default to `44-search-cpu-starve.yaml` (error_rate_pct SLO). Verified clean.

## Blocker observed (expected)
- `asciinema` is NOT installed on this machine (`command -v asciinema` → empty). The animated
  `.cast` cannot be produced here; the text transcript is the captured fallback. See 09.
