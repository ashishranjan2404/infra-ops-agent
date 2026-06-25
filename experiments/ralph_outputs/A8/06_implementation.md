# A8 — 06 Implementation

## What I built (real artifacts under A8/artifacts/)
1. **`build_heldout_split.py`** — reads the cidg registry (32 incidents) + each
   scenario YAML's `meta.failure_class`/`meta.source`, reads both training corpora,
   classifies each candidate via the Tier 1/2/3 criterion, and emits the manifest
   + CSV. Exits 0 iff the held-out set has zero overlap and is non-empty.
2. **`assert_no_overlap.py`** — standalone guard that re-derives the training
   incident set from the raw jsonl and independently asserts zero overlap for the
   manifest's `held_out` list. Usable as a CI gate.
3. **`heldout_manifest.json`** — the split manifest (criteria + per-incident
   decisions + training stats + sha256).
4. **`heldout_split.csv`** — flat table of all 32 incidents with held_out flag and
   the three tier signals.

## Result of the build
- Training corpora touch **34 distinct incidents** across 268 trajectory lines
  (`trajectories.jsonl` synthetic + `hud_trajectories.jsonl` real/synthetic).
- Candidate pool: **32** cidg incidents.
- **Held-out: 15** (8 `simple`, 7 `novel`). **Contaminated: 17** (all 14 `cascade`
  + 3 `novel` whose source company/event is in training).
- Held-out keys:
  `auth_cert_expiry, azure_leapyear_cert, billing_disk_fill, checkout_bad_rollout,
   conntrack_exhaustion, facebook_bgp_backbone, firefox_addon_cert, gke_ip_exhaustion,
   ingest_fd_exhaust, kafka_poison_pill, knight_capital_conflict, media_oom_leak,
   payments_dep_revoked, redis_cache_flush, search_cpu_starve`.

## Why those are excluded
- Every `cascade` incident is a real public post-mortem from a company that appears
  in training (github / cloudflare / slack / aws / datadog / circleci / incidentio /
  launchdarkly) → Tier 2 company-axis hit.
- 3 `novel` items excluded: `cloudflare_leap_second`, `cloudflare_waf_regex`
  (cloudflare in train), `github_zk_splitbrain` (github in train).

## Novelty criteria (recorded in manifest.criteria)
- Tier 1: exact normalized id match OR >=2 shared meaningful tokens with a training
  incident.
- Tier 2 (HARD): cidg incident names a company present in training.
- Tier 3 (SOFT/flag): failure_class also seen in training; hard only via
  `--strict-class` (yields a 13-incident strict subset).

## Shared-core safety
No shared core files edited. The registry/YAML/jsonl are read-only inputs. All new
code/data live under `experiments/ralph_outputs/A8/artifacts/`. No proposed change
to a core file was needed.
