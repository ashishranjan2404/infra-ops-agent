# B15 — SUMMARY

**Task:** Compare our pass@1 directly against SREGym leaderboard numbers — research SREGym's
reported pass@1 (cited), build a comparison table vs our A1/A2 pass@1, with honest caveats about
benchmark non-equivalence. Deliver a Markdown report + a small table-generating script.

## Deliverables (all in experiments/ralph_outputs/B15/artifacts/)
- comparison_report.md — primary report: no-ranking TL;DR, metric-equivalence note, 2 inlined
  tables, 10 numbered non-equivalence caveats, honest bottom line, cited sources.
- gen_comparison.py — stdlib script; reads real A1/A2 JSON + cited SREGym JSON, renders tables.
  --selftest (6 asserts) passes; full run exits 0.
- sregym_reported.json — 8 leaderboard rows + partition breakdowns, each with a source.
- our_pass_at_1.json — generated distillation of A1/A2 pass@1 (overall + per-family + CIs).
- comparison_table.md — script-rendered tables.

## Key result
| | pass@1 / E2E |
|---|---|
| Ours, single-attempt band (best_of_n / rex_no_oracle) | ~0.31–0.34 |
| Ours, REx (multi-attempt + oracle — no SREGym counterpart) | 0.90 (A1) / 0.89 (A2) |
| SREGym E2E, no noise (range across 4 agents) | 32.9% – 60.7% |
| SREGym best (Claude Code, Sonnet 4.6, no noise) | 60.7% |

## Honest finding
Framed as contextualization, not a ranking. On a fair single-attempt basis our baselines
(~0.31–0.34) sit below SREGym's live-task E2E range — SREGym's tasks are materially harder than
our simulator's single-run conditions. REx's 0.90 is a real lift but in a regime (multi-attempt +
oracle) SREGym does not measure, so it is NOT a SREGym win. Both benchmarks agree that
novel/unseen failures are the hardest (SREGym E2E collapses ported->new).

## Caveats surfaced
Substrate (sim vs live K8s), grader (reward@0.8 vs oracle), attempt budget, oracle feedback,
threshold knob, metric non-decomposition, model mismatch (our cheaper models vs frontier), noise,
zero task overlap, loose family<->partition mapping.

## Status: completed. No shared core files edited; SREGym numbers cited (arXiv:2605.07161v1 +
sregym.com/leaderboard, retrieved 2026-06-25). Downstream matched-model re-run is the one blocked
item (needs API budget), documented in 09.
