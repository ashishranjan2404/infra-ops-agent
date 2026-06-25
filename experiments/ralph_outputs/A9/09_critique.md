# A9 — 09 Critique (honest)

## What's weak

1. **MTTR provenance is from memory, not fetched.** I labelled from knowledge of these
   well-known postmortems rather than live-fetching each URL (no web access invoked in
   this run). The high-confidence rows (Cloudflare WAF 27m, Monzo 99m, AWS S3, GitHub
   2018, Roblox 73h, Fastly 49m, Reddit Pi-Day) are stable, widely-cited facts, but a
   reviewer is right to demand each citation be re-verified against the primary source
   before publication. This is the single biggest attack surface.

2. **MTTR is outage-level; the sim is per-node.** Postmortems give a global impact
   window; the CIDG scenarios have per-service SLOs and a canonical fix path. The unit
   mismatch is a genuine **construct-validity** problem (the AAAI reviewer's point):
   correlating human outage MTTR with agent per-incident difficulty conflates blast
   radius, org maturity, and detection lag — none modelled by the sim. Any correlation
   found must be presented as suggestive, not causal.

3. **MTTR definition varies row to row.** "Mitigation" (kill switch) vs "full
   recovery" (backfill done) differ by hours for staged incidents (Cloudbleed, Firefox
   armagaddon, Azure leap-year, Datadog multi-region). I picked the most-cited window
   per row and tagged `approximate`/medium confidence, but the dataset is not built on
   one consistent stopwatch definition. A stricter version would add separate
   `time_to_mitigate` and `time_to_full_recovery` columns.

4. **Low n and low coverage for correlation.** Only 18 of 51 incidents (and 18 of 30
   real) have a known MTTR. Spearman on 18 points is fragile; a single mis-labelled
   long-tail incident (Roblox 4380m, Firefox 4320m) dominates Pearson. The stub
   deliberately emits no p-value to avoid false rigor.

5. **The default difficulty proxy is near-constant.** Most real scenarios are 5-node
   cascades, so the structural proxy clusters around ~10 and the default correlation is
   not meaningful. It exists only to make the script runnable; the real analysis needs
   an external `--scores` file (pass@k / step-count), which A9 does not own.

6. **Race-condition coverage is a snapshot.** Other workers added YAMLs mid-run; I
   labelled up to 51, but if more land afterward the labels lag. Mitigation: re-running
   `build_mttr_json.py --check` plus the T3 cross-check flags any new uncovered YAML.

## What a reviewer attacks first
"Show me the primary source and the exact stopwatch definition for each MTTR." The
mitigation already in place: every real row carries `mttr_basis` + `confidence` +
`source_citation` + `notes`, and unknowns are honestly null. But verification of the
URLs against primary postmortems is required follow-up work.

## What's missing (honest)
- Live URL verification of each citation.
- Separate mitigate-vs-recover columns.
- A real agent-difficulty score to make the correlation meaningful (blocked: not
  owned by A9; the `--scores` seam is provided).
