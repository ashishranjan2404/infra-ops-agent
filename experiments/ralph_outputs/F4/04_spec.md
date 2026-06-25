# F4 — 04_spec

## Artifact
`experiments/ralph_outputs/F4/artifacts/make_figures.py` — single-file, headless
(`matplotlib.use("Agg")`), network-free. Entry point `main()`; six `figN_*()` functions.

## Inputs (read-only, real)
| Var | Path (rel to repo) | Schema used |
|---|---|---|
| A1 | `experiments/ralph_outputs/A1/artifacts/summary_table.json` | `{cond:{overall|simple|cascade|novel:{n,p1,ci:[lo,hi],p2,p5,...}}}` |
| A2 mcnemar | `experiments/ralph_outputs/A2/artifacts/ablation_v2_mcnemar_deepseek-v4-pro.json` | `mcnemar_overall.{rex_vs_*}.{a_pass_b_fail,a_fail_b_pass,p_exact}` |
| frontier | `rex/runs/frontier.json` | `{budget,models:[{model,baseline_mean,rex_mean}]}` |
| harness | `rex/runs/harness_synth_v2.json` | `{n_rules,heldout_table:{policy:{accuracy,false_allow_rate,false_block_rate}},vs_v1}` |

## Shared constants
```python
COND_ORDER = ["zero_shot","best_of_n","retry_realistic","rex_no_oracle","rex"]   # == generate_paper_tables.py
C    = {cond: hex}   # Wong colour-blind-safe palette
PRETTY = {cond: human label}
```

## Function signatures
```python
def _load(rel: str) -> dict | None          # repo-relative load, warns + None if missing
def _save(fig, name: str) -> None           # savefig bbox_inches=tight into OUT, closes fig
def fig1_passk_bars_ci() -> None            # A1 overall pass@1 + asym Wilson errorbars
def fig2_passk_by_family() -> None          # A1 grouped bars over [simple,cascade,novel]
def fig3_passk_curve() -> None              # A1 line plot ks=[1,2,5] per condition
def fig4_mcnemar() -> None                  # A2 horizontal divergent bars (a_pass vs a_fail) + p
def fig5_frontier() -> None                 # frontier baseline vs rex bars, sorted by baseline, arrows
def fig6_harness_generalization() -> None   # harness 2-panel accuracy + false-allow per policy
def main() -> None
```

## Output contract
- 6 PNGs in `experiments/ralph_outputs/F4/artifacts/figures/`, 200 DPI, `figure.constrained_layout`.
- Error bars in fig1 are **asymmetric** `[p-lo, hi-p]` from the stored Wilson interval (never normal).
- Every figure title carries the source model; fig1 carries an n / seeds / CI caption.

## Test cases (07 runs these)
1. `python3 make_figures.py` exits 0, prints 6 `fig ->` lines.
2. All 6 PNG files exist, size > 10 KB, valid PNG header (PIL `Image.open` succeeds).
3. Numbers spot-check: fig1 REx pass@1 == A1 `rex.overall.p1` (0.8968 → "0.90");
   fig4 vs-zero-shot a_pass == 99, a_fail == 1; fig5 every `rex_mean` == 0.86.
4. No file written outside the F4 namespace (`git status` shows only F4 paths dirty).
