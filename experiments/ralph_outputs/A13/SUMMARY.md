# A13 — Summary: Multi-fault incidents (2 simultaneous faults)

## Goal
The CIDG scenario suite was 100% single-fault. Add incidents with 2 simultaneous faults so
agents can't win by chasing the loudest single symptom and stopping after one fix.

## Delivered
- 3 schema-valid multi-fault scenarios in scenarios/cidg/generated/, each with a primary +
  one secondary fault, distinct SLO victims, two smoking guns, traps, and a 2-step canonical fix:
  - 80-multi-cert-poolleak.yaml      — cert_expire + pool_leak (independent coincidence)
  - 81-multi-rollout-cacheflush.yaml — bad_revision masking cache_flush (masking pair)
  - 82-multi-fdexhaust-cpustarve.yaml— fd_exhaust + cpu_starve (shared blast radius, with trap)
- artifacts/test_multifault.py     — 6 pytest cases, all passing against the real current engine.
- artifacts/engine_multifault.patch— verified 92-line unified diff making the engine inject both
  faults and treat resolution conjunctively (delivered, NOT applied per no-edit rule).

## Verification
- python -m sim.spec validate -> all 3 OK; full suite 51/51 valid (no regression).
- pytest -> 6 passed.
- Patch verified on a throwaway copy: for every spec, fixing one fault != resolved, fixing both =
  resolved (genuine conjunctive 2-fault behavior).
- Repo sim/engine.py and sim/spec.py confirmed byte-identical to pre-task snapshots.

## Honest status
Data + mechanism are real and verified. Live grading ("must fix both to resolve") is a one-commit
follow-up that applies the patch — the engine today injects only the primary fault, so the second
fault is inert until then. Status: completed.
