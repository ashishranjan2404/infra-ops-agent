# B15 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/B15/artifacts/`)

1. **`sregym_reported.json`** — frozen, *cited* SREGym numbers:
   - 8 leaderboard rows (Claude Code / Stratus / Codex × Sonnet-4.6 / GPT-5.4 / Kimi-K2.5,
     no-noise & with-noise) with diagnosis / mitigation / E2E and a per-row `source`.
   - Per-partition breakdowns (Ported 34 / Similar 43 / New 13) for the 3 no-noise agents.
   - Explicit `metric_semantics` note: SREGym "success rate over 3 runs, 1 attempt/run" == pass@1.
   - Sourced from arXiv:2605.07161v1 + sregym.com/leaderboard (retrieved 2026-06-25).

2. **`gen_comparison.py`** — pure-stdlib generator:
   - `load_our()` reads the **real** A1 (`full_pass_at_k_glm-5p2.json`) and A2
     (`ablation_pass_at_k_deepseek-v4-pro.json`) artifacts, tolerant of key spellings
     (`pass@1`/`p1`, `ci95`/`ci`) and of A1's per-family nesting under `by_family`.
   - `render_table()` emits two Markdown tables: (1) headline cross-benchmark with an
     `attempt_regime` column that flags REx as having **no SREGym counterpart**; (2) a LOOSE
     family↔partition analogy.
   - `--selftest` with 6 asserts (fmt_pct, sregym row count, rex overall ≈0.897, 5 conditions,
     per-family populated, novel rex==1.0). Paths resolve relative to `__file__`.

3. **`our_pass_at_1.json`** — *generated* (not hand-typed) distillation of A1/A2 pass@1 +
   per-family + CIs, with `source_runs` provenance.

4. **`comparison_table.md`** — script output (both tables).

5. **`comparison_report.md`** — primary deliverable: TL;DR (no-ranking framing), metric-
   equivalence note, both inlined tables, a **10-point caveats** section, honest bottom line,
   and cited sources.

## Key numbers surfaced
- Ours (overall pass@1): zero_shot 0.23 / best_of_n 0.34 / retry 0.35 / rex_no_oracle 0.33 /
  **rex 0.90** (A1 glm-5p2); rex 0.89 (A2 deepseek-v4-pro).
- SREGym E2E (no noise): 32.9%–60.7% range; best = Claude Code 60.7%.
- Fair single-attempt comparison: our ~0.31–0.34 band sits **below** SREGym's E2E range →
  SREGym's live tasks are harder than our sim's single-run conditions.

## Parallel-safety / core-file policy
- No shared core file edited. The script only **reads** A1/A2 artifacts and `rex/*` for semantics.
- All outputs live in B15's own `artifacts/`. No `experiments/results/` writes.
- SREGym numbers are frozen + cited (no live scrape at run time) for reproducibility.
