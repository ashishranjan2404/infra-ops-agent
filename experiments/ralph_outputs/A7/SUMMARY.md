# A7 — SUMMARY: Incident difficulty scoring

**Task:** add incident difficulty metadata (`expected_pass_rate`,
`trap_complexity`) to the CIDG scenario corpus.

**Delivered (all real):**
- `artifacts/score_difficulty.py` — deterministic, stdlib+pyyaml, non-mutating
  sidecar scorer. Reads `scenarios/cidg/generated/*.yaml` read-only; computes
  `trap_complexity`, `expected_pass_rate`, `difficulty_bucket` from structural
  signals (topology, cascades, loudest-alert-not-cause, hidden root,
  smoking-gun buried depth, fix steps, flap, multi-SLO).
- `artifacts/difficulty_scores.json` — incidents with full auditable
  per-component breakdowns + schema.
- `artifacts/difficulty_scores.csv` — flat table for joins/curriculum.
- 10 step docs (01–10).

**Real results (48 incidents, corpus grew 33->48 under concurrent workers):**
- expected_pass_rate 0.433–0.873 (mean 0.560); trap_complexity 0.062–0.791.
- buckets: easy 11 / medium 23 / hard 14.
- hardest: gitlab-db-deletion, aws-s3-typo-capacity, network-partition postmortems.
- easiest: synthetic single-node leaf incidents.

**Validation:** T1–T7 all PASS (range, count==disk, easy/hard face-validity,
md5 idempotency, source-mtime-unchanged non-mutation, breakdown keys present).

**Honest limitation:** `expected_pass_rate` is an uncalibrated *prior* (no
labelled pass rates in corpus) — use it ordinally; calibrate against real
pass@1 later. No source YAMLs or core .py files were modified.

**Status:** completed.
