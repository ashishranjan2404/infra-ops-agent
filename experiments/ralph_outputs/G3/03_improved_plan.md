# G3 — 03 Improved Plan

## What changed after the grill
1. **Banner placement (SMR/RLE):** The non-equivalence banner is rendered IMMEDIATELY
   above the ranked table inside the same markdown block — not a footnote. Implemented
   in `render()`.
2. **REx tagged inline (PSRE):** The REx row carries `[OUT-OF-REGIME]` in its system
   label and a `regime` column reading "multi-attempt + ORACLE (no SREGym analogue)".
   The positioning text calls its rank-1 placement a "CATEGORY ERROR", not a win.
3. **Lead with the fair band (RLE/DOL/AAAI):** The headline honest finding is
   best_of_n/retry ~34.9% at rank 8/13 — lower part of SREGym's band, above only the 2
   weakest Kimi-K2.5 rows. rex_no_oracle is labeled "fair but more compute", not headline.
4. **Noise-axis gap (DOL):** Added as an explicit caveat — we have no noise axis; SREGym
   does, and frontier agents degrade under it (e.g. Codex 53.3->45.9).
5. **Grader non-equivalence (AAAI):** Kept front-and-center — our reward@0.8 pass is
   cheaper than verified live recovery; surfaced in banner + caveats.

## Critiques accepted
- Place ourselves but caveat in-table (RLE over SMR's "don't rank").
- Inline out-of-regime tag for REx (PSRE).
- Fair band as the lede (RLE/DOL).
- Noise + grader caveats (DOL/AAAI).

## Critiques rejected (and why)
- **SMR: "don't rank at all."** Rejected — the task explicitly asks "where would we
  rank." Refusing is non-responsive. We rank AND disown the fairness, which satisfies
  the rigor concern without dodging the question.
- **DOL: "rex_no_oracle isn't fair."** Partially rejected — it is single-attempt in the
  sense of one final answer scored, so it stays tagged "fair", but the report flags its
  extra tree compute. Not promoting it to the headline addresses the spirit.

## Final deliverables (unchanged set, refined semantics)
- `artifacts/rank_leaderboard.py` (+ `--selftest`)
- `artifacts/sregym_reported.json` (cited)
- `artifacts/ranked_leaderboard.md` (banner-above-table + honest positioning)
