# A11 — 06 Implementation

## What I built
A generator/validator `make_pairs.py` and the 7 real artifacts it produces.

### New scenario YAMLs (in `scenarios/cidg/generated/`, numbers 80-85 — verified unused)
- `80-fd-exhaust-leaf-shipper.yaml` — P1-A: fd_exhaust, leaf, root visible.
- `81-fd-exhaust-cascade-gw.yaml` — P1-B: fd_exhaust on api-gw, buried, two
  downstream callers breach SLO. Fix tool identical to P1-A (`restart_service`).
- `82-cert-expire-leaf-sidecar.yaml` — P2-A: cert_expire, leaf (payments-svc).
- `83-cert-expire-cascade-ingress.yaml` — P2-B: cert_expire on tls-ingress,
  buried, web-frontend + mobile-bff 5xx. Fix `renew_certificate` (same as A).
- `84-mem-leak-leaf-transcoder.yaml` — P3-A: mem_leak, leaf (transcoder).
- `85-mem-leak-cascade-cache.yaml` — P3-B: mem_leak on object-cache, buried,
  catalog-api + recsys degrade. Fix `increase_memory_limit` (same as A).

### Manifest
- `scenarios/cidg/generated/pairs_manifest.json` (+ copy in this task's artifacts/)
  maps each pair A<->B and records the shared root cause + per-variant symptom text.

### Design realization
Within each pair the generator asserts:
`failure_class(A)==failure_class(B)`, `fix_tool(A)==fix_tool(B)`,
`len(nodes A) != len(nodes B)` (symptom differs). `persistent` and `severity`
held identical; only `hidden` + topology + SLO node + smoking-gun + cascade flags
vary — i.e. observation/surface differs, cause is invariant.

## What I deliberately did NOT do
- Did not edit `registry.json` or any existing YAML (parallel-safety).
- Did not add new failure classes, fix tools, or node kinds — reused only those
  already present in shipped scenarios so the existing loader + deterministic
  judge score them unchanged.
- Did not wire a transfer-eval runner; that's a downstream task. The manifest is
  the contract such a runner would consume (train on A, test on B).

## How to use
Load A as the training/seen scenario and B as the held-out transfer test (or
reverse, to control for difficulty — see manifest description). An agent that
learned the mechanism should solve B from A because the canonical fix is identical.
