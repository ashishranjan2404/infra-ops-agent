# B15 — 03 Improved Plan

## What changed after the grill

### Accepted critiques
1. **(SMR/PSRE/RLE) Report a comparator band, not one number.** The report now shows our
   pass@1 for *all five* conditions and explicitly labels which are "single-run-ish"
   (zero_shot 0.23, best_of_n 0.34, retry_realistic 0.35, rex_no_oracle 0.33) vs which is
   "multi-attempt + oracle" (rex 0.90). SREGym agents are scaffolded single-attempt loops, so
   the fairest cross-benchmark line is our **best_of_n / rex_no_oracle (~0.33)** band, NOT
   zero_shot alone and NOT rex.
2. **(DOL/AAAI) Primary cross-axis row = SREGym E2E (no-noise).** Both our reward and SREGym E2E
   bundle diagnose+mitigate. Use SREGym no-noise as primary (our sim is noise-off), and also list
   their with-noise column.
3. **(AAAI/RLE) We cannot decompose diagnosis vs mitigation.** Added as an explicit caveat: our
   single scalar reward has no diagnosis-only counterpart to SREGym's diagnosis success rate.
4. **(RLE) Disclose the 0.8 threshold knob.** Added a caveat that our pass@1 is a *thresholded
   graded reward* and is sensitive to the 0.8 cutoff, which SREGym's binary oracle does not have.
5. **(DOL) Noise alignment.** State explicitly that our sim is closest to SREGym's *no-noise*
   column and that SREGym degrades under noise.

### Rejected critiques (and why)
- **"Just use zero_shot as the comparator" (early SMR).** Rejected as the *sole* line — PSRE is
  right that SREGym agents iterate within a run. We keep zero_shot in the band as the floor, but
  the headline cross-benchmark comparator is the best_of_n/rex_no_oracle band (~0.33).
- **"Map families to partitions 1:1 and report per-partition deltas as if comparable."** Rejected.
  Only novel↔New is defensible. We present the mapping as a labeled *loose analogy*, and do not
  compute per-partition "win/loss" deltas, only side-by-side display.
- **"Drop REx from the table because it's not single-attempt" (implied by AAAI).** Rejected — REx
  is our headline method and omitting it hides the regime difference. Instead we *keep* it but tag
  it `multi-attempt+oracle (no SREGym counterpart)` so it can't be misread as a like-for-like win.

## Final shape of deliverable
- `sregym_reported.json`: 8 leaderboard rows + partition breakdowns, each with a source field.
- `our_pass_at_1.json`: generated from A1 (full-42, glm-5p2) and A2 (30-inc, deepseek-v4-pro),
  overall + per-family, all 5 conditions, with CIs.
- `gen_comparison.py`: stdlib script → `comparison_table.md`; report stitched in `comparison_report.md`.
- Caveats section: >= 8 axes (substrate, grader, metric decomposition, threshold knob, model
  mismatch, attempt budget, oracle feedback, noise, task overlap, partition-mapping looseness).
