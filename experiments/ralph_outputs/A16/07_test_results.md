# A16 — Test Results

## Commands run
```
$ python3 -m py_compile experiments/ralph_outputs/A16/artifacts/validate_scenarios.py
compile OK

$ python3 experiments/ralph_outputs/A16/artifacts/validate_scenarios.py
validated 61 scenarios: 54 pass / 4 fail / 3 error
  FAIL  scenarios/cidg/03-railway-gcp-suspension.yaml  (asserts_fix_resolves=True) root_cleared=False
  ERROR scenarios/cidg/05-azure-ddos-amplification.yaml  (asserts_fix_resolves=True) KeyError: 'latency_p99_ms'
  FAIL  scenarios/cidg/06-aws-dynamodb-dns.yaml  (asserts_fix_resolves=True) root_cleared=False
  ERROR scenarios/cidg/20-leaf-cpu-saturation-positive.yaml  (asserts_fix_resolves=True) KeyError: 'latency_p99_ms'
  ERROR scenarios/cidg/21-leaf-oom-positive.yaml  (asserts_fix_resolves=True) KeyError: 'pod_restarts'
  FAIL  scenarios/cidg/generated/82-travis-ci-leaked-secret.yaml  (asserts_fix_resolves=True) root_cleared=False
  FAIL  scenarios/cidg/generated/87-aws-s3-typo-capacity.yaml  (asserts_fix_resolves=True) root_cleared=False
report -> experiments/ralph_outputs/A16/validation_report.json
```

> NOTE: the scenario set is being grown live by other parallel Ralph workers.
> Earlier in this session the run saw 42 → 54 → 61 scenarios; the validator globs
> the live set each run so totals move. The numbers below are the final run (61).
> The 6-then-7 broken `fix_resolves` promises are stable across every run; the
> 7th (`87-aws-s3-typo-capacity`) appeared when that YAML was added mid-session.

## Final tally (61 scenarios)
| status | count |
|--------|-------|
| pass   | 54    |
| fail   | 4     |
| error  | 3     |

- `all_pass = false`. Validator exit code is non-zero (as designed).
- **No vacuous passes**: every one of the 54 passes had `fault_active_at_t0=true`
  AND ended `root_cleared=true` AND `is_resolved=true`. So the 54 are genuine.

## Failures (engine says the canonical fix does NOT resolve)
1. `03-railway-gcp-suspension` — wrong target: fault node `gcp-network-api`,
   fix targets `railway-control-plane`. root_cleared=False.
2. `06-aws-dynamodb-dns` — wrong target: location `dynamodb->dns` ⇒ fault node
   `dynamodb`, fix targets `dns`. root_cleared=False.
3. `82-travis-ci-leaked-secret` — wrong tool for kind: `dep_revoked` not
   remediated by `rotate_secret`. root_cleared=False.
4. `87-aws-s3-typo-capacity` — wrong tool/target: single step
   `restart_service@index-subsystem` does not clear this scenario's root.
   root_cleared=False.

## Errors (engine cannot evaluate the SLO — unmodeled metric)
5. `05-azure-ddos-amplification` — `KeyError: 'latency_p99_ms'`.
6. `20-leaf-cpu-saturation-positive` — `KeyError: 'latency_p99_ms'`.
7. `21-leaf-oom-positive` — `KeyError: 'pod_restarts'`.

The engine node vector only carries `error_rate_pct` and `p99_latency_ms`
(see `sim/engine.py:72`); these SLOs name metrics outside that vector.

## Fixes applied
NONE to shared core — per the brief, failures are documented, not silently
patched. The only code written is the task-namespaced validator + its report.
