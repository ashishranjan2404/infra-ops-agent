# B4 — Summary

**Task:** Split pass@k results by incident type (simple / cascade / novel) into 3 separate tables.

## Delivered
1. **classify_incidents.py** — deterministic classifier over all 51 generated CIDG YAMLs,
   reusing the A7 difficulty sidecar + A8 novelty/family sidecar + registry.json for the 32
   labelled incidents, and a mechanics-grounded fallback (primary-type rule
   novel > cascade > simple) for the 19 unregistered ones. Output: incident_types.{csv,json}.
   Result: {simple:11, cascade:20, novel:20}; tiers {registry:32, real-outage:10, name-rule:6,
   mechanics:3}.
2. **stratify_pass_at_k.py** — discovers all pass@k result JSONs and renders 3 separate per-type
   Markdown tables (stratified_simple.md, stratified_cascade.md, stratified_novel.md) + combined
   stratified_pass_at_k.json, pulling pre-computed by_family numbers verbatim (no re-estimation)
   from the A1 glm-5p2 full run and A2 deepseek-v4-pro ablation. 10 data rows per table
   (2 models x 5 conditions).

## Key results (real numbers)
- zero_shot pass@1: simple (0.556) > cascade (~0.21) > novel (0.167) for glm-5p2; deepseek
  novel = 0.080.
- REx drives every type to pass@1 = 1.0; rex_no_oracle collapses back to ~zero_shot on novel —
  the oracle, not retries, lifts the novel stratum.

## Validation
All 9 tests pass: 51/51 classified, registry agreement 0-mismatch, T4 counts (8/14/10) match,
a11 name-rules correct, T8 parity 105/105 exact vs A1, classifier-vs-result mismatches = 0.

## Honesty notes
19/51 incidents are classified but unevaluated (not in registry); disclosed per-type in each
table. REx cells are saturated (reward_std=0). Single-label axis files novel-and-cascade
incidents as novel. No shared core files edited; stdlib+pyyaml; re-runnable.
