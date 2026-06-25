# H9 — 08 Verification against success criteria

| # | Success criterion | Status | Evidence |
|---|---|---|---|
| 1 | Static HTML leaderboard renders a **models-vs-pass@k table from a JSON** (separate file) | **MET** | `leaderboard.html` `fetch("leaderboard.json")` → builds `<table>` from `data.entries`; verifier tests "HTML fetches leaderboard.json" + "HTML renders entries" pass. |
| 2 | Populated with **real A1/A2/E3 numbers**, not placeholders | **MET** | 5 anchor numbers cross-checked to 1e-3 against `A1/summary_table.json`, `A2/ablation_pass_at_k_*.json`, `E3/result_three_way.json` — all PASS. Full provenance (`source`, `episodes`) on every row. |
| 3 | **Verify it loads the JSON** | **MET** | Verifier serves the dir over HTTP, GETs `/leaderboard.html` (200) and `/leaderboard.json` (200), parses JSON, matches entry count. 29/29. |
| 4 | Clean, **public-facing** styling | **MET** | Dark theme, responsive, CI bars, gold-highlighted headline rows, family filter + search + sortable headers, zero external deps (renders offline). |
| 5 | **No shared core files edited** | **MET** | Only files written are under `experiments/ralph_outputs/H9/`. No `rex/*`, `sim/*`, `agent/*`, `experiments/*.py`, dashboard, or `ralph_status.json` touched. |

## Are the outputs real (not placeholder)?
Yes. Every pass@k value traces to a completed task's stored episode rewards:
- A1: 630-episode run (glm-5p2, 42 incidents, floor_ok).
- A2: 750-episode ablation (deepseek-v4-pro, 30 incidents, McNemar p<0.0001).
- E3: 56-episode three-way eval (zero-shot vs OpenSRE-trained Qwen3-8B; Fireball arm blocked).

The blocked Fireball arm is shown honestly in a separate panel (no fabricated number), matching
E3's own documented blocker.

## Honest caveats carried forward
- Cross-family/cross-model ranking is mitigated (family tag + filter) but not eliminated.
- pass@5 is an optimistic upper bound at low seeds (inherited A1 caveat), flagged in `metric_notes`.
