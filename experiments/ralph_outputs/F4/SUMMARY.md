# F4 — SUMMARY

**Task:** Create publication-quality figures (matplotlib) grounded in real result JSONs
(A1/A2/B-series, frontier, learned harness). No edits to shared core files.

## Deliverable
`experiments/ralph_outputs/F4/artifacts/make_figures.py` — a single headless (Agg),
network-free, 200-DPI matplotlib generator using a colour-blind-safe palette. Run once;
produced **6 real PNGs** in `artifacts/figures/`, every value read at runtime from committed
result JSONs (nothing fabricated).

| Figure | Source | Headline |
|---|---|---|
| fig1_passk_ci | A1 (glm-5p2, 126 ep/cond) | REx pass@1 0.90 [0.83,0.94] vs zero-shot 0.23, disjoint Wilson CIs |
| fig2_passk_by_family | A1 | REx holds on cascade 0.85 / novel 1.0 where zero-shot collapses (0.07/0.17) |
| fig3_passk_curve | A1 | pass@k k=1,2,5 — REx ceilings by k=2 |
| fig4_mcnemar | A2 (deepseek, 750 ep) | REx beats every baseline, p<1e-4 (99/88/88/91 discordant) |
| fig5_frontier | rex/runs/frontier.json | REx lifts all 5 models to a common ~0.86 frontier |
| fig6_harness | rex/runs/harness_synth_v2.json | Learned 3-rule harness: held-out acc 0.897, false-allow 0.308 (vs oracle 0.949/0.154) |

## Verification
T1 exit 0 · T2 all 6 PNGs PIL-valid, >10 KB, 200 DPI · T3 5 number spot-checks vs source JSON
PASS · T4 no shared `.py` modified (find -newermt empty). Visually inspected fig1/fig4/fig6.

## Honesty
The figures draw the honest negatives: no-oracle REx sits with the baselines, the learned
harness sits below the hand oracle, and the 0.86 frontier plateau is named in-title. Main
weakness (09): bars use glm-5p2 while the significance test uses deepseek — a future task
should put both on one model.

**Status: completed.**
