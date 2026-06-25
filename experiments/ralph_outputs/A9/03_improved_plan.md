# A9 — 03 Improved Plan

## What changed vs 01 (driven by the grill)

**Accepted:**
1. (PSRE) Added explicit `mttr_basis` ∈ {documented, approximate, unknown,
   synthetic, novel_synthetic, benchmark_synthetic} and a `notes` caveat per row, so
   the MTTR *definition* (mitigation vs full recovery, outage-level granularity) is
   never ambiguous.
2. (PSRE/DOL) Keep synthetic incidents in the dataset as a labeled **control group**
   (`is_real_incident=false`, `confidence=not_applicable`) rather than dropping them.
3. (DOL/RLE) Correlation stub must run on **repo assets alone** -> added a structural
   difficulty proxy derived from the YAML (node count + cascade + buried-gun) as the
   default signal, with `--scores` to plug in real pass@k/step-count later.
4. (AAAI) Report **coverage, not significance**; emit summary stats (n real, n
   labeled, coverage %) and push the construct-validity caveat into 09_critique.
5. (RLE) Key strictly on the `meta.id` `incident_id` the sim uses, verified against
   the YAMLs.

**Rejected (with reason):**
- (RLE) "Block until a real difficulty score exists" — rejected as scope creep; A9
  owns labels + harness, not the agent eval. The stub's pluggable `--scores` is the
  clean seam.
- (SMR R1 implied) per-service MTTR — rejected; postmortems give outage-level windows
  only. Forcing per-node numbers would be fabrication.
- (AAAI) "n too low, don't ship" — rejected; partial real labels + honest coverage is
  a valid, reusable deliverable. The dataset grows as more postmortems are sourced.

## Final shape
- `mttr_labels.csv` (source of truth, 32 rows, 9 columns).
- `build_mttr_json.py` (`--check` validator + JSON renderer with summary).
- `correlate_mttr.py` (stdlib Pearson/Spearman, structural proxy default, unknown-drop
  reporting).
- Validator enforces invariants: known-MTTR rows cannot have unknown/na confidence;
  not_applicable rows cannot be flagged real.
