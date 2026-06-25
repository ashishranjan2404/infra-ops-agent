# A9 — SUMMARY

Task: Label each CIDG incident with the real-world MTTR from its source postmortem,
for downstream correlation analysis.

## Deliverables (experiments/ralph_outputs/A9/artifacts/)
- mttr_labels.csv — source-of-truth labels, 51 rows (one per scenario YAML), columns:
  incident_id, yaml_file, title, is_real_incident, mttr_minutes, mttr_basis,
  source_citation, confidence, notes.
- mttr_labels.json — generated sidecar with summary block; unknown MTTR = null.
- build_mttr_json.py — --check validator (schema/range/invariants) + JSON renderer.
- correlate_mttr.py — stdlib Pearson/Spearman correlation stub; joins MTTR to a
  pluggable difficulty signal (--scores) with a YAML structural-proxy fallback; drops
  unknown-MTTR rows transparently.

## Coverage (51 incidents total)
- 30 real (dated public postmortems), 21 synthetic/benchmark/novel.
- 18 real incidents have a sourced MTTR (citation + confidence): e.g. Cloudflare WAF
  27m, Knight Capital 45m, Fastly 49m, Monzo 99m, AWS S3 283m, Reddit Pi-Day 314m,
  Facebook BGP 373m, GitLab DB-deletion ~1080m, GitHub 2018 1451m, Roblox 4380m (73h).
- 12 real incidents marked unknown (no reliable MTTR / date-signature conflation /
  future-dated / security-disclosure) — never invented.
- 21 synthetic marked not_applicable. Coverage of real incidents: 60%.

## Validation
T1 validator OK; T2 rejects bad input (exit 1); T3 id<->YAML cross-check clean
(51/51); T4 correlation runs (18 paired, 33 dropped w/ reasons); T5 unknown -> null.

## Honest limitations (see 09)
MTTR sourced from knowledge of well-known postmortems (URLs not live-verified this
run); outage-level granularity vs per-node sim SLOs; n=18 low; default difficulty
proxy is a placeholder — real correlation needs external pass@k/step-count via
--scores. With the default proxy: Pearson -0.25, Spearman 0.06 (placeholder signal).

## Status: completed
