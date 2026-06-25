# A8 — SUMMARY

**Task:** Create a held-out test set that NO training data touches (strict novelty).

## Deliverables (all under `experiments/ralph_outputs/A8/artifacts/`)
- `build_heldout_split.py` — classifier/builder (tiered novelty criterion)
- `assert_no_overlap.py` — independent CI guard (re-derives training set; negative-control proven)
- `heldout_manifest.json` — split manifest: criteria + per-incident decisions + training stats + sha256
- `heldout_split.csv` — flat table of all 32 candidates with tier signals

## Result
- Training corpora touch **34 distinct incidents** (268 trajectory lines).
- Candidate pool: **32** cidg incidents.
- **Held-out: 15** (8 simple + 7 novel). **Contaminated: 17** (all 14 cascade + 3 novel).
- Guard: **PASS, zero overlap**. Negative control correctly **FAILS** (exit 1).

## Held-out incident ids (default split)
auth_cert_expiry, azure_leapyear_cert, billing_disk_fill, checkout_bad_rollout,
conntrack_exhaustion, facebook_bgp_backbone, firefox_addon_cert, gke_ip_exhaustion,
ingest_fd_exhaust, kafka_poison_pill, knight_capital_conflict, media_oom_leak,
payments_dep_revoked, redis_cache_flush, search_cpu_starve
(`--strict-class` -> 13: also drops cert/fd-class repeats.)

## Novelty criteria
- **Tier 1:** exact id match OR >=2 shared meaningful tokens with a training incident.
- **Tier 2 (HARD):** incident names a company present in training -> contaminated.
- **Tier 3 (soft flag):** failure_class reuse recorded; hard only via `--strict-class`.

## Known gaps (see 09)
Lexical-only matching; hand-curated company list; **zero held-out cascade coverage**
(every cascade derives from a training-present company); modest N.

## Reproduce
    python3 experiments/ralph_outputs/A8/artifacts/build_heldout_split.py
    python3 experiments/ralph_outputs/A8/artifacts/assert_no_overlap.py   # exit 0
