# F4 — 03_improved_plan

## What changed vs 01_plan (driven by the grill)

| Change | From critique | Verdict |
|---|---|---|
| Lock to **6 single-responsibility figures** | DVO/SMR (maintainability) over REV (fewer) | accepted |
| **Wilson CIs only**, read directly from JSON `ci`/`ci95` | SMR | accepted |
| Promote **by-family breakdown** to a first-class figure (fig2) | PSRE | accepted |
| Add **pass@k scaling curve** (fig3) | SMR | accepted |
| **Model label baked into every figure title + caption** | REV | accepted |
| Keep **REx(no-oracle)** as its own labeled bar; do not hide the "oracle does the work" finding | RLE | accepted |
| Add **learned-harness generalization** (fig6) so the deployable story (no hand oracle) is shown | PSRE | accepted |
| **McNemar paired discordant-pair** figure (fig4) from A2 | REV | accepted |

## Rejected critiques (and why)
- **REV: "collapse to ~3 figures."** Rejected. These are results-dir artifacts feeding a paper,
  not a camera-ready figure budget. Over-supplying labeled, independently-regenerated figures is
  the right trade for a writer who will cherry-pick. Adopted REV's *underlying* concern (each
  figure must stand alone) via per-figure labels instead.
- **RLE: "make rex_no_oracle≈best_of_n the headline."** Rejected as the *headline* (PSRE: nobody
  deploys no-oracle REx), but the bar stays visible in figs 1–3 so the finding is not airbrushed.

## Final figure list
1. `fig1_passk_ci.png` — pass@1 by condition + Wilson 95% CI (A1, glm-5p2).
2. `fig2_passk_by_family.png` — grouped pass@1 × family × condition (A1).
3. `fig3_passk_curve.png` — pass@k (k=1,2,5) per condition (A1).
4. `fig4_mcnemar.png` — McNemar discordant pairs, REx vs each baseline (A2, deepseek, 750 ep).
5. `fig5_frontier.png` — REx vs baseline mean reward across 5 models (frontier.json).
6. `fig6_harness.png` — learned-harness held-out accuracy + false-allow vs seed/oracle (harness_synth_v2).

## Guardrails
- OUT dir hard-pinned under `experiments/ralph_outputs/F4/artifacts/figures/`.
- No write outside the F4 namespace; shared `experiments/figures/` untouched.
- Per-file accessors to absorb A1 (`p1`,`ci`) vs A2 (`pass@1`,`ci95`) schema drift.
