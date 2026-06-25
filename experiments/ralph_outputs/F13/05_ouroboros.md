# 05 — Ouroboros (3 self-critiques, each finds real problems)

## Engineer A — "the validator is theater"
- **Problem (real):** A tag-stack HTML check that ignores void elements (`<br>`, `<meta>`,
  `<img>`, `<link>`) will false-positive on a perfectly valid poster. If the validator is
  wrong, step 07 "passes" mean nothing.
- **Problem (real):** "every `[src:]` path exists" — if I cite `rex/runs/ablation.json` and
  it doesn't exist on disk, the validator should catch it, else I'm citing phantom files.
- **Fix:** Validator hard-codes the HTML void-element set and skips them. Add a source-path
  existence check over the distinct `[src: ...]` paths, but only fail on paths that look like
  repo files (contain `/` or end in a known ext) and tolerate `rex/scoring.py`-style refs.

## Engineer B — "the honesty framing can still mislead"
- **Problem (real):** Putting frontier 0.86 and the ablation side by side is good, but if the
  frontier panel uses bigger font / color and the ablation is grey small text, the layout
  *re-buries* it despite "equal weight" in the spec. Reviewers read hierarchy, not intent.
- **Problem (real):** "0.86 = (4×1.0+0.30)/5" is a clean story but a skeptic will ask: is
  0.30 for the escalated incident a real graded value or a narrative convenience? I must not
  present the decomposition as if it's an empirical per-incident measurement if it's the
  *designed* ceiling. Label it "designed safe ceiling," not "measured."
- **Fix:** Give the ablation panel the same card style, same heading size, and an explicit
  "⚠ rigor check" tag so it reads as a peer claim. Reword the ceiling as "the *designed* safe
  ceiling the sweep converges to," not a measured decomposition.

## Engineer C — "it won't survive an actual print shop / is over-built"
- **Problem (real):** A0 is 841×1189mm. If I set the container to `width:841mm` and the
  browser print path uses `@page size:A0` but the body has a default margin, content clips.
  Also fixed `mm` sizing with a 3-column CSS grid at large font can overflow vertically — the
  poster scrolls instead of fitting one page.
- **Problem (over-engineering):** I don't need a pixel-perfect 300dpi guarantee in HTML —
  that's the print shop's raster step. Over-claiming "300dpi CMYK-safe" in HTML is false
  precision. Scope the deliverable to "valid, print-CSS'd A0 source that a designer can take
  to final."
- **Fix:** `body{margin:0}` + `@page{margin:0}`; container uses A0 mm with `overflow` guarded
  by modest font sizes; accept that final raster/CMYK is a downstream design step and say so
  in a footer note rather than overclaiming.

## Final filtered spec (deltas applied)
1. Validator: skip HTML void elements; add tolerant `[src:]` path-existence check.
2. Layout: ablation panel = same card/heading weight as frontier, tagged "⚠ rigor check".
3. Wording: 0.86 described as the **designed** safe ceiling the sweep converges to.
4. Print: `margin:0` on body and `@page`; conservative font sizes to fit one A0 page;
   footer notes raster/CMYK is a downstream design step (no false 300dpi claim).
