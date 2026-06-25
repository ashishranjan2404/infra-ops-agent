# A6 — 01 Plan

## Objective
Convert 10 additional famous danluu-style postmortems into CIDG scenario YAMLs in the
exact schema used by `scenarios/cidg/generated/*.yaml`, validated by `sim/spec.py`.
The existing set (40–79) already covers Cloudflare, GitHub, Slack, Knight Capital,
Facebook, AWS Kinesis, Azure leap-year, Firefox, etc. I must pick 10 NEW incidents and
write uniquely-named/numbered files (80–89) that parse and pass `python -m sim.spec validate`.

## Approach
1. Read the schema (`sim/spec.py`) to learn the closed vocabularies:
   - `NODE_KINDS`, `EDGE_TYPES`, `ROOT_CAUSE_KINDS`, `SLO_DIRECTIONS`.
   - tools must come from `tools_registry.json` (25 tools incl. clear_cache, rollback_deployment,
     rotate_secret, restart_service, increase_memory_limit, modify_network_policy, ...).
2. Study `70-facebook-bgp-backbone.yaml` and `72-knight-capital-conflict.yaml` as templates,
   and the `registry.json` metadata for `gold_root`/`red_herrings`/`family` conventions.
3. Map each postmortem onto one `ROOT_CAUSE_KIND` + one canonical fix tool, building a small
   topology (control-plane/datastore root + 2–4 downstream victim services + ingress LB) so the
   cascade and "loudest alert is not the cause" properties hold.
4. Write 10 YAMLs to `scenarios/cidg/generated/80..89-<slug>.yaml`.
5. Validate every file with `python3 -m sim.spec validate` and a YAML parse check.

## Files to create (10 new, unique numbers 80–89)
- 80 GitLab DB directory deletion (2017) → cache_flush / clear_cache (restore working set)
- 81 Cloudflare Cloudbleed parser overrun (2017) → bad_revision / rollback_deployment
- 82 Travis CI leaked build secret (2021) → dep_revoked / rotate_secret
- 83 Roblox Consul streaming meltdown (2021) → churn_spike / modify_network_policy
- 84 Fastly global edge config trigger (2021) → bad_revision / rollback_deployment
- 85 Reddit Pi-Day k8s upgrade route (2023) → config_bloat / modify_network_policy
- 86 Honeycomb retry-storm thread exhaustion (2023) → thread_exhaust / restart_service
- 87 AWS S3 command-typo capacity removal (2017) → node_notready / restart_service
- 88 Stripe Redis fork/dirty-page memory pressure (2019) → mem_leak / increase_memory_limit
- 89 Monzo Cassandra scale-up-during-compaction (2019) → churn_spike / restart_service

## Dependencies
- `sim/spec.py` validator, `tools_registry.json`, PyYAML (already installed).
- No edits to any shared `.py` or existing YAML — only NEW files.

## Risks
- Picking an incident already in the set (mitigated: dup-id check across the whole dir).
- Using a tool/kind outside the closed vocab (mitigated: validator run on every file).
- Colliding file numbers with other parallel workers (mitigated: descriptive slugs + dup check).

## Success criteria
- 10 new, uniquely-named YAMLs, each parses as YAML and passes `sim.spec validate` (0 errors).
- Each maps to a distinct real postmortem with a coherent root cause, trap, and canonical fix.
