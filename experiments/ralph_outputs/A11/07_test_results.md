# A11 — 07 Test Results

## Test 1 — generation + round-trip parse (PASS)
```
$ python3 experiments/ralph_outputs/A11/artifacts/make_pairs.py
wrote+parsed a11-pair-fd-exhaust-leaf-shipper.yaml
wrote+parsed a11-pair-fd-exhaust-cascade-gw.yaml
wrote+parsed a11-pair-cert-expire-leaf-sidecar.yaml
wrote+parsed a11-pair-cert-expire-cascade-ingress.yaml
wrote+parsed a11-pair-mem-leak-leaf-transcoder.yaml
wrote+parsed a11-pair-mem-leak-cascade-cache.yaml
pair P1 OK: shared root=fd_exhaust/restart_service
pair P2 OK: shared root=cert_expire/renew_certificate
pair P3 OK: shared root=mem_leak/increase_memory_limit
wrote manifest .../a11_pairs_manifest.json
```
Each YAML is written then re-read with `yaml.safe_load`; failure_class and fix
tool survive the round trip (asserted in generator).

## Test 2 — pair invariants + schema (PASS)
```
P1: class=fd_exhaust fix=restart_service | nodes A=1 B=3 | hidden A=False B=True cascade A=False B=True -> PASS
P2: class=cert_expire fix=renew_certificate | nodes A=1 B=3 | hidden A=False B=True cascade A=False B=True -> PASS
P3: class=mem_leak fix=increase_memory_limit | nodes A=1 B=3 | hidden A=False B=True cascade A=False B=True -> PASS
ALL 3 PAIRS PASS
```
Verified within each pair: equal failure_class, equal fix tool, equal
`persistent`(False) and `severity`(0.7); unequal node count (symptom differs);
`hidden` and `cascades` flip leaf→cascade.

## Test 3 — schema key conformance (PASS)
Each new YAML's top-level key set ⊇ the required set
`{meta, topology, root_cause, fault, observation, slo, trap_actions,
canonical_fix, assertions, chance, seed}` and `fault.sim.set` carries the right
`<class>_active` toggle (`fd_exhaust_active`, `cert_expire_active`,
`mem_leak_active`).

## Test 4 — idempotency / no-overwrite guard (PASS)
Re-running the generator after files exist prints
`REFUSING: <file> already exists` and exits non-zero, so it can never clobber.

## Test 5 — collision handling (FIXED during run)
Initial draft used numeric prefixes 80-85; a parallel Ralph worker concurrently
claimed 80-89 with different names. Resolved by renaming all six to the
task-namespaced `a11-pair-*` prefix and the manifest to `a11_pairs_manifest.json`,
which cannot collide. Confirmed no `a11-*` file pre-existed before writing.

## Fixes applied
- Renamed artifacts from numeric to `a11-pair-*` namespace after detecting the
  parallel-worker number race.
- Held `persistent`/`severity` constant within pairs (per ouroboros Eng1).
