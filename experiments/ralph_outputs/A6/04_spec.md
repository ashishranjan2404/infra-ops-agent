# A6 — 04 Spec

## File format (per `sim/spec.py::_spec_from_dict`)
Top-level keys: `meta`, `topology{nodes,edges}`, `root_cause`, `fault`, `observation`,
`slo[]`, `trap_actions[]`, `canonical_fix{ordering_notes,steps[]}`, `assertions`, `chance`, `seed`.

### Closed vocabularies enforced by `validate()`
- `node.kind` ∈ {service, datastore, cache, queue, pool, control_plane, monitoring, node, lb, external}
- `edge.type` ∈ {required, optional, pool, queue, discovery, observes}
- `root_cause.kind` ∈ {cpu_starve, mem_leak, pool_leak, thread_exhaust, fd_exhaust, churn_spike,
  config_bloat, bad_content, bad_revision, cert_expire, cache_flush, disk_fill, node_notready,
  net_delay, dns_race, dep_revoked, defense_amplify, host_agent_crash}
- `slo.direction` ∈ {higher_bad, lower_bad}
- tool names ∈ `tools_registry.json` (25 tools).

### Validator rules a file MUST satisfy (else FAIL)
- unique node names; every edge src/dst is a node; `pool` dst needs `resources.pool_size`.
- `root_cause.location` is a node (or "A->B" edge); if `persistent` then `reset_by` non-empty.
- ≥1 SLO; each SLO direction valid; SLO node in topology.
- canonical_fix + trap tools all in registry.
- smoking_gun.node in topology.
- if `assertions.cascades` → ≥1 required/pool/queue edge.
- if `assertions.buried_gun_exists` → ≥1 smoking_gun.

## Per-scenario contract (id → root node/kind → SLO victims → trap → fix tool)
| # | id | root node / kind | victims (SLO) | trap (scale_deployment) | canonical fix |
|---|----|------|----|----|----|
|80|gitlab-db-deletion|db-primary / cache_flush|web-app,api-svc,ci-runner|web-app|clear_cache db-primary|
|81|cloudbleed-parser-overrun|html-parser / bad_revision|edge-proxy,cache-tier|edge-proxy|rollback_deployment html-parser|
|82|travis-ci-leaked-secret|secrets-vault / dep_revoked|build-runner,artifact-svc|build-runner|rotate_secret secrets-vault|
|83|roblox-consul-streaming|consul-streaming / churn_spike|game-svc,matchmaker,player-api|game-svc|modify_network_policy consul-streaming|
|84|fastly-pop-config|edge-config / bad_revision|pop-edge,content-svc,origin-shield|pop-edge|rollback_deployment edge-config|
|85|reddit-piday-k8s-route|route-controller / config_bloat|front-web,thing-svc,vote-svc|front-web|modify_network_policy route-controller|
|86|honeycomb-retry-storm|query-worker / thread_exhaust|ui-svc,ingest-svc|ui-svc|restart_service query-worker|
|87|aws-s3-typo-capacity|index-subsystem / node_notready|get-svc,put-svc,placement-svc|get-svc|restart_service index-subsystem|
|88|stripe-redis-fork-latency|redis-store / mem_leak|charge-api,idempotency-svc|charge-api|increase_memory_limit redis-store|
|89|monzo-cassandra-compaction|cassandra-ring / churn_spike|ledger-svc,card-svc,account-svc|ledger-svc|restart_service cassandra-ring|

## Shared structural choices
- Each victim has a `required` edge toward the root (or `discovery` for control-plane roots) →
  satisfies `assertions.cascades` and "loudest alert ≠ cause".
- One `get_logs` smoking_gun on the root node, `buried_under: 40` → satisfies `buried_gun_exists`.
- `assertions`: cascades/loudest_alert_not_cause/fix_resolves/buried_gun_exists = true;
  hysteresis/monitoring_degrades = false (no `observes` edges, no `persistent`).
- `chance`: flap 0.05, jitter 0.03, partial_recovery 0.0. `seed = 1000 + file_number`.

## Test cases
- T1 (parse): `yaml.safe_load` each file → no exception.
- T2 (validate): `python3 -m sim.spec validate scenarios/cidg/generated/8?-*.yaml` → 0 FAIL on my 10.
- T3 (unique ids): scan all generated YAML, assert no duplicate `meta.id`.
- T4 (closed vocab): implicitly covered by T2 (validator rejects out-of-vocab kind/tool/edge).
