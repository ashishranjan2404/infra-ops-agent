# F4 — 06_implementation

## What I built
A single headless matplotlib generator, `experiments/ralph_outputs/F4/artifacts/make_figures.py`
(~290 lines), that renders **six publication-quality PNGs** from real committed result JSONs.
It uses the Wong colour-blind-safe palette, `constrained_layout`, 200 DPI, no top/right spines,
and bakes the source model + sample size into each figure so figures stand alone.

## Figures produced (all from real numbers)
| File | Source JSON | Headline content |
|---|---|---|
| `figures/fig1_passk_ci.png` | A1 summary_table | pass@1 by condition + asymmetric Wilson 95% CI; REx 0.90 vs zero-shot 0.23 (n=126/cond) |
| `figures/fig2_passk_by_family.png` | A1 summary_table | pass@1 × {simple,cascade,novel} × 5 conditions; REx holds on cascade(0.85)/novel(1.0) |
| `figures/fig3_passk_curve.png` | A1 summary_table | pass@k for k=1,2,5; REx reaches ceiling by k=2 |
| `figures/fig4_mcnemar.png` | A2 mcnemar | divergent discordant-pair bars + exact p; REx beats every baseline (p<1e-4) |
| `figures/fig5_frontier.png` | rex/runs/frontier.json | baseline vs REx mean reward, 5 models, lift arrows; all lifted to ~0.86 |
| `figures/fig6_harness.png` | rex/runs/harness_synth_v2.json | learned harness held-out accuracy 0.897 & false-allow 0.308 vs seed/oracle |

## Schema handling
A1 uses `p1`/`ci`; A2 uses `pass@1`/`ci95`; `heldout_table` is a `{policy: metrics}` dict.
Each figure has its own accessor so no schema is assumed across files.

## Shared-file safety
No shared core file touched. Verified via `git status` — only paths under
`experiments/ralph_outputs/F4/` are dirty. Output is hard-pinned to the F4 namespace;
`experiments/figures/` (the existing committed figures) is left untouched.

## Proposed (NOT applied) integration
If the maintainers want these in the canonical `experiments/figures/`, the clean path is to
add a `--out` flag to `experiments/generate_paper_tables.py` and import these `figN_*` helpers.
I deliberately did **not** edit that shared script (parallel-safety rule). The generator stands
alone and can be invoked directly.
