# A6 — 06 Implementation

## What I built
10 NEW scenario YAMLs in `scenarios/cidg/generated/`, one per additional famous postmortem,
all in the exact schema consumed by `sim/spec.py` and matching the house style of
`70-facebook-bgp-backbone.yaml` / `72-knight-capital-conflict.yaml`:

| file | id | root_cause.kind | canonical fix tool |
|------|----|------|------|
| 80-gitlab-db-deletion.yaml | gitlab-db-deletion | cache_flush | clear_cache |
| 81-cloudbleed-parser-overrun.yaml | cloudbleed-parser-overrun | bad_revision | rollback_deployment |
| 82-travis-ci-leaked-secret.yaml | travis-ci-leaked-secret | dep_revoked | rotate_secret |
| 83-roblox-consul-streaming.yaml | roblox-consul-streaming | churn_spike | modify_network_policy |
| 84-fastly-pop-config.yaml | fastly-pop-config | bad_revision | rollback_deployment |
| 85-reddit-piday-k8s-route.yaml | reddit-piday-k8s-route | config_bloat | modify_network_policy |
| 86-honeycomb-retry-storm.yaml | honeycomb-retry-storm | thread_exhaust | restart_service |
| 87-aws-s3-typo-capacity.yaml | aws-s3-typo-capacity | node_notready | restart_service |
| 88-stripe-redis-fork-latency.yaml | stripe-redis-fork-latency | mem_leak | increase_memory_limit |
| 89-monzo-cassandra-compaction.yaml | monzo-cassandra-compaction | churn_spike | restart_service |

8 distinct root-cause kinds across 10 files. Each file: a root node (control_plane/datastore/
service) plus 2–4 downstream victim services and an ingress LB; victims have required/discovery
edges toward the root so the cascade and "loudest alert ≠ cause" properties hold; one buried
`get_logs` smoking gun on the root; a `scale_deployment` trap on a downstream victim (never the
root); the in-vocab canonical fix on the root with an `ordering_notes` string documenting any
abstraction (e.g. clear_cache = restore working set; restart_service = rebuild in-memory index).

## Files touched
- CREATED: `scenarios/cidg/generated/80..89-<slug>.yaml` (10 files).
- NOT touched (per parallel-safety rules): any existing YAML, `registry.json`, `sim/*.py`,
  `rex/*.py`, `tools_registry.json`.

## Known follow-up (not done by design)
- `registry.json` is a shared file the brief forbids editing; harnesses that read registry-level
  `gold_root`/`red_herrings`/`family` metadata would need 10 entries added later. The YAMLs
  themselves are self-contained and load directly via `sim.spec.load_spec`.
