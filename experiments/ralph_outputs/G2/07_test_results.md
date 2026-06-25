# G2 — Test Results (real command output)

## 1. pytest suite — 10/10 PASS
```
$ python -m pytest experiments/ralph_outputs/G2/artifacts/test_adapter.py -q
..........                                                               [100%]
10 passed in 0.06s
```
Covers: reset, metrics-reflect-fault, structured-fix-resolves, wrong-tool-fails,
kubectl-translation-resolves, kubectl-read-noop, kubectl-untranslated-counted,
diagnosis positive + negative, traces-low-fidelity flag.

## 2. Stub agent end-to-end — CONTRACT_OK
```
$ python experiments/ralph_outputs/G2/artifacts/stub_agent.py
... (full JSON of solve / trap / kubectl episodes) ...
CONTRACT_OK: True
```
- SOLVE: `rollback_deployment(checkout-api)` -> `mitigation.resolved == True`,
  `diagnosis_correct == True`.
- TRAP:  `restart_pod(checkout-api)` -> `mitigation.resolved == False`
  (proves the verdict is the real `sim.engine.is_resolved`, not hardcoded).
- KUBECTL: `kubectl rollout undo deploy/checkout-api` -> translated to
  `rollback_deployment` (untranslated False); `kubectl edit configmap app-flags` ->
  untranslated True; `untranslated_rate == 0.5` over 2 calls.

## 3. Adapter smoke-run on a real scenario
```
$ python experiments/ralph_outputs/G2/artifacts/sregym_adapter.py
cluster_control: {"applied": true, "tool": "rollback_deployment", "target": "checkout-api",
                  "target_matched_node": true, ... "resolved": true}
mitigation: {"resolved": true, "root_cleared": true, ...}
```

## 4. Full-scenario-set runnability sweep (REAL, measured)
```
$ python3 -c "...load each scenario, apply canonical fix, check is_resolved..."
total=61  runnable(no KeyError)=58  resolved_by_canonical_fix=58  errored=3
```
- **58/61** CIDG scenarios (hand-authored + generated) run cleanly through the adapter and
  resolve via their canonical fix.
- **3 errored** — `is_resolved` raises `KeyError` because their SLOs reference metrics the
  Tier-A engine does not populate: `20-leaf-cpu-saturation-positive` (`latency_p99_ms`,
  `cpu_utilization_pct`), `21-leaf-oom-positive` (`pod_restarts`), and one generated peer.

## 5. agents.yaml validity
```
$ python3 -c "import yaml; yaml.safe_load(open('.../agents.yaml'))"
agents.yaml parses   # agents: ['stratus', 'cidg-stub']
```

## Fixes applied during testing
- Initial default scenario (`21-leaf-oom-positive`) crashed `is_resolved` with
  `KeyError: 'pod_restarts'`. Root cause: the Tier-A engine tracks only `error_rate_pct`
  + `p99_latency_ms`, but some hand-authored SLOs name other metrics. **Fix:** switched
  the runnable default to `22-leaf-bad-deploy-positive` (error-rate-only SLO), and
  documented the 3 unsupported scenarios as an explicit excluded set + a noted (NOT
  applied) engine follow-up. No shared-core file was edited.

## Blocker (carried to 09)
Real **Stratus was not executed**: its driver + SREGym's 5 MCP servers are external (not
vendored), and the in-process adapter is not yet wrapped behind the MCP/HTTP transport
Stratus connects to. All deliverables *up to* invoking Stratus are real and verified.
