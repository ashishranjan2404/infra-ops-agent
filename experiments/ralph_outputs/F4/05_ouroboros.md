# F4 — 05_ouroboros (self-critique as 3 engineers in sequence)

## Engineer A — "data-integrity"
**Problems found:**
1. A1 stores Wilson CIs; if I used `yerr=std/sqrt(n)` (normal approx) the REx bar's upper
   whisker would punch through 1.0 (p1=0.897, that's wrong). **Fix:** read `ci` and build
   asymmetric `[p-lo, hi-p]`. (Done in code.)
2. fig6: I initially assumed `heldout_table` was a list of per-incident rows. It is actually a
   `{policy: metrics}` dict (`seed (empty)`, `synthesized (v2)`, `hand-written is_safe`). A
   list-based accessor would have silently produced an empty/blank figure. **Fix:** inspected
   the JSON first, rewrote fig6 to a 2-panel accuracy + false-allow comparison.
3. Mixed models across figures (glm-5p2 vs deepseek-v4-pro) could read as cherry-picking.
   **Fix:** model name in every title; A2's own honest one-liner (oracle does the lift) is
   preserved by keeping `rex_no_oracle` visible.

## Engineer B — "reviewer-skeptic"
**Problems found:**
1. fig5 shows every model's `rex_mean` == 0.86 exactly. A reviewer will ask "why identical?"
   This is real (frontier.json budget=3, REx ceilings the 5-scenario set the same way) but it
   *looks* suspicious without context. **Mitigation:** title says "lifts every model to a common
   frontier (~0.86)" — naming the effect instead of hiding it. The per-scenario data in
   frontier.json backs it (singleton_node_notready caps at 0.3 for all, the rest go to 1.0).
2. fig4 hides that 750 ep = 30 incidents × 5 seeds, and McNemar is over incident×seed pairs
   (n_discordant up to 100). Without the n, a reviewer can't judge power. **Fix:** title carries
   "750 ep"; bars are literal discordant-pair counts with p annotated.
3. No raw CSV/data table beside the PNGs — a reviewer can't re-plot. **Accepted as minor:** the
   source JSONs *are* the data; the script is deterministic. Documented in 09 as a known gap.

## Engineer C — "maintenance / over-engineering"
**Problems found:**
1. Six figures is arguably over-supply. **Kept** (grill resolved this): single-responsibility,
   independently regenerated, writer cherry-picks. Each `figN` is <40 lines.
2. Hard-coded deepseek/glm filenames make the script brittle if A2 reruns under another model.
   **Accepted trade-off:** these are the *real* committed result files for this paper; a glob
   would risk silently picking a `.partial`. Explicit > clever here. Documented.
3. fig2 legend (5 conditions) may overlap bars at the top. **Fix:** `bbox_to_anchor` upper-center,
   `ylim` headroom to 1.12. Verified visually.

## Final filtered spec delta
- fig1 errorbars asymmetric Wilson (not normal). [A]
- fig6 reworked to `{policy: metrics}` 2-panel. [A]
- All titles model-labeled; frontier "common frontier" effect named not hidden. [B]
- Explicit filenames retained on purpose; lack of CSV sidecar noted as a known minor gap. [B/C]
