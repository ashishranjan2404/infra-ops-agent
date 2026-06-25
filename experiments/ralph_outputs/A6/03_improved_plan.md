# A6 — 03 Improved Plan

## What changed after the grill
1. **Maximize root-cause diversity (accepted SR/SRE).** Final set spans 8 distinct
   `ROOT_CAUSE_KINDS`: cache_flush, bad_revision (×2: Cloudbleed, Fastly), dep_revoked,
   churn_spike (×2: Roblox, Monzo), config_bloat, thread_exhaust, node_notready, mem_leak.
   No file reuses the same {incident, kind, fix} triple.
2. **Document every lossy abstraction in `ordering_notes` (accepted REV/SRE).**
   - GitLab deletion → `clear_cache` on db-primary, note = "restore working set / reseed from backup".
   - AWS S3 typo → `restart_service` on index-subsystem, note = "rebuild in-memory index".
   - Roblox/Reddit config faults → `modify_network_policy ... disable_bad_path`.
   - Monzo/Honeycomb metastable → `restart_service` with a note that *adding capacity feeds the churn*.
3. **Trap always on a downstream victim, never the root (accepted RLE).** Every `trap_actions`
   entry is `scale_deployment` against a service node that is NOT the root cause node, so the
   judge can mark it unambiguously wrong.
4. **Kept topologies small (rejected DOL's "go bigger").** Reason: the canonical house files
   (Facebook=5, Knight=4 nodes) set the norm; bigger graphs add read-cost, not learning signal.
   Cascade property is satisfied by `required`/`discovery` edges from each victim toward the root.

## Rejected critiques (with reason)
- **"GitLab→clear_cache is misleading" (SRE R1):** rejected. The registry documents `clear_cache`
  as "reseed the working set"; with an explicit ordering_note it is the honest in-vocab mapping.
  Inventing a `restore_backup` tool would break the closed action space (out of A6 scope).
- **"Cite source URLs now" (REV):** partially rejected for A6. The schema allows `urls: []` and
  every existing file leaves it empty; I keep the `source` string descriptive and flag URL
  enrichment as future work in 09 rather than fabricating links.

## Final file plan: 80–89 (unchanged slugs from 01, now locked)
gitlab-db-deletion · cloudbleed-parser-overrun · travis-ci-leaked-secret ·
roblox-consul-streaming · fastly-pop-config · reddit-piday-k8s-route ·
honeycomb-retry-storm · aws-s3-typo-capacity · stripe-redis-fork-latency ·
monzo-cassandra-compaction.
