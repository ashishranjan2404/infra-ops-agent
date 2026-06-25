# A6 — SUMMARY

**Task:** Convert 10 additional famous danluu-style postmortems into CIDG scenario YAMLs.

**Delivered:** 10 new, schema-valid scenario files in `scenarios/cidg/generated/` (80–89),
each a distinct real incident, spanning 8 distinct `root_cause` kinds. All parse and pass the
project validator `python3 -m sim.spec validate` (10/10, 0 errors); no duplicate `meta.id`
across the corpus; zero edits to any shared `.py`, existing YAML, or `registry.json`.

| file | incident | kind | fix |
|------|----------|------|-----|
| 80-gitlab-db-deletion | GitLab 2017 primary DB dir deletion | cache_flush | clear_cache |
| 81-cloudbleed-parser-overrun | Cloudflare Cloudbleed 2017 | bad_revision | rollback_deployment |
| 82-travis-ci-leaked-secret | Travis CI 2021 secret leak | dep_revoked | rotate_secret |
| 83-roblox-consul-streaming | Roblox 2021 73h Consul outage | churn_spike | modify_network_policy |
| 84-fastly-pop-config | Fastly 2021-06-08 edge config | bad_revision | rollback_deployment |
| 85-reddit-piday-k8s-route | Reddit 2023 Pi-Day k8s upgrade | config_bloat | modify_network_policy |
| 86-honeycomb-retry-storm | Honeycomb 2023 retry storm | thread_exhaust | restart_service |
| 87-aws-s3-typo-capacity | AWS S3 2017-02-28 command typo | node_notready | restart_service |
| 88-stripe-redis-fork-latency | Stripe 2019 Redis fork pressure | mem_leak | increase_memory_limit |
| 89-monzo-cassandra-compaction | Monzo 2019 Cassandra scale-up | churn_spike | restart_service |

**Tests:** T1 parse 10/10 · T2 validate 10/10 · T3 no dup ids · T4 closed-vocab (via T2).

**Honest gaps (see 09):** uniform `scale_deployment` traps; metastable worsen-on-scale not
encoded (schema limit); two lossy fix mappings documented in `ordering_notes`; `registry.json`
metadata entries and a dynamic `sim/engine.py` run are scoped-out follow-ups.

**Status:** completed.
