# A6 — 07 Test Results

## T1 — YAML parse (`yaml.safe_load` each file)
```
PARSE OK 80-gitlab-db-deletion
PARSE OK 81-cloudbleed-parser-overrun
PARSE OK 82-travis-ci-leaked-secret
PARSE OK 83-roblox-consul-streaming
PARSE OK 84-fastly-pop-config
PARSE OK 85-reddit-piday-k8s-route
PARSE OK 86-honeycomb-retry-storm
PARSE OK 87-aws-s3-typo-capacity
PARSE OK 88-stripe-redis-fork-latency
PARSE OK 89-monzo-cassandra-compaction
```
**PASS** — all 10 parse.

## T2 — `python3 -m sim.spec validate` (my 10 files)
```
OK    .../80-gitlab-db-deletion.yaml        [gitlab-db-deletion]        5 nodes / 4 edges / rc=cache_flush
OK    .../81-cloudbleed-parser-overrun.yaml [cloudbleed-parser-overrun] 4 nodes / 3 edges / rc=bad_revision
OK    .../82-travis-ci-leaked-secret.yaml   [travis-ci-leaked-secret]   4 nodes / 3 edges / rc=dep_revoked
OK    .../83-roblox-consul-streaming.yaml   [roblox-consul-streaming]   5 nodes / 4 edges / rc=churn_spike
OK    .../84-fastly-pop-config.yaml         [fastly-pop-config]         5 nodes / 4 edges / rc=bad_revision
OK    .../85-reddit-piday-k8s-route.yaml    [reddit-piday-k8s-route]    5 nodes / 4 edges / rc=config_bloat
OK    .../86-honeycomb-retry-storm.yaml     [honeycomb-retry-storm]     4 nodes / 3 edges / rc=thread_exhaust
OK    .../87-aws-s3-typo-capacity.yaml      [aws-s3-typo-capacity]      5 nodes / 4 edges / rc=node_notready
OK    .../88-stripe-redis-fork-latency.yaml [stripe-redis-fork-latency] 4 nodes / 3 edges / rc=mem_leak
OK    .../89-monzo-cassandra-compaction.yaml[monzo-cassandra-compaction]5 nodes / 4 edges / rc=churn_spike

10/10 specs valid
```
**PASS** — validator (closed-vocab kind/edge/tool checks + structural cascade/smoking-gun checks)
reports 0 errors across all 10.

## T3 — duplicate `meta.id` scan across the whole generated dir
```
DUPLICATE IDS: none
```
**PASS** — my 10 ids do not collide with the existing 40–79 set or with each other.

## T4 — closed-vocabulary coverage
Covered transitively by T2: the validator rejects any `root_cause.kind`/`edge.type`/tool outside
the closed vocab, so a green T2 proves every kind and fix/trap tool is in-vocab. Root-cause kinds
used: cache_flush, bad_revision, dep_revoked, churn_spike, config_bloat, thread_exhaust,
node_notready, mem_leak (8 distinct).

## Fixes applied during testing
None required — all 10 files passed parse + validate on first run. (Initial broad glob `8?-*.yaml`
also surfaced unrelated leaf/cascade files authored by other parallel workers; those are not mine
and were excluded by validating my 10 explicit paths.)
