# F4 — 09_critique (honest)

## What a reviewer attacks
1. **Mixed models across figures.** fig1–3 are glm-5p2 (A1); fig4 is deepseek-v4-pro (A2);
   fig5 spans 5 models. Each is labeled, but a skeptic notes there is no *single* model carried
   through bars + significance + frontier. A stronger artifact would re-run McNemar on glm-5p2 so
   fig1 and fig4 share a model. Blocked here only by not re-running A1's per-episode pass matrix
   (the McNemar artifact only exists for A2). Documented, not faked.
2. **No CSV sidecar.** Figures are reproducible from the script + JSONs, but I did not emit the
   plotted values as a flat table. A reviewer who wants to re-plot must read my accessors. Minor.
3. **frontier.json `rex_mean` is identical (0.86) for all 5 models.** Real (the 5-scenario set
   ceilings the same way: 4 scenarios → 1.0, singleton_node_notready caps at 0.3 for everyone),
   but it makes the frontier figure look "too clean." The per-scenario detail that justifies it
   lives in frontier.json but isn't drawn — a per-scenario heatmap would be more convincing.
4. **fig6 conflates two evaluation regimes.** harness_synth_v2 measures *block-decision accuracy*
   on held-out incidents, which is a different metric from the pass@k reward used in figs 1–5.
   The two should not be read on the same axis; the figure is correct in isolation but a careless
   reader might conflate "0.897 accuracy" with "0.90 pass@1." Caption mitigates, doesn't erase.

## What's weak / missing
- No bootstrap or per-seed scatter overlay on the bars; CIs are Wilson on the pooled
  incident×seed Bernoulli, which slightly understates between-seed variance.
- Six static PNGs; no combined multi-panel "Figure 1" composite a paper would actually use.
- The frontier figure would benefit from a per-scenario small-multiple to defend the 0.86 plateau.

## What is genuinely solid
- Every value is read from real, committed run artifacts; nothing fabricated.
- Wilson CIs (not normal approx) — correct near the 0/1 boundary.
- The honest negatives (no-oracle≈baseline, learned-harness < oracle, 0.3 plateau scenario) are
  *drawn*, not airbrushed. That is the most defensible property of this figure set.
- Fully reproducible, headless, network-free, no shared-file edits.
