# H9 — Public-facing leaderboard page — 01 Plan

## Objective
Build a real, clean, public-facing **static leaderboard** (like SREGym's) that renders a
**models-vs-pass@k** table from a JSON file, populated with **real numbers** from completed
tasks A1, A2, and E3. The page must demonstrably *load* the JSON at runtime (not inline it).

## Approach
- Decouple data from presentation: a `leaderboard.json` (data) + a single self-contained
  `leaderboard.html` (presentation) that `fetch()`es the JSON. This mirrors how SREGym /
  HELM-style boards work and lets new runs be added without touching markup.
- Mine real pass@k from existing artifacts:
  - **A1**: `full_pass_at_k_glm-5p2.json` / `summary_table.json` (42 incidents, 5 conditions, glm-5p2).
  - **A2**: `ablation_pass_at_k_deepseek-v4-pro.json` (30 incidents, 5 conditions, deepseek-v4-pro).
  - **E3**: `result_three_way.json` (14 cascades, zero-shot vs OpenSRE-trained Qwen3-8B; Fireball arm blocked).
- Render a sortable/filterable table: rank, system, model, family, pass@1 (+95% CI bar), pass@2, pass@5, n, notes.
- Ship a `verify_leaderboard.py` that (a) schema-checks the JSON, (b) cross-checks 5 real
  numbers against the source tasks, and (c) serves the dir over HTTP and confirms the page +
  JSON return 200 and parse — i.e. proves "it loads the JSON."

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/H9/artifacts/leaderboard.json`
- `experiments/ralph_outputs/H9/artifacts/leaderboard.html`
- `experiments/ralph_outputs/H9/artifacts/verify_leaderboard.py`
- The 10 step docs + SUMMARY.md + result.json under `H9/`.

## Files to modify
- None. No shared core files touched (no `rex/*`, `sim/*`, `agent/*`, `experiments/*.py`, dashboard).

## Dependencies
- Python 3.13 stdlib only (`http.server`, `json`, `urllib`) for verification. No build step; the
  HTML is vanilla JS/CSS, no external CDN, so it works fully offline once served.

## Risks
- `file://` fetch is blocked by browser CORS → mitigate: instruct to serve over HTTP; verifier
  uses HTTP so the "loads JSON" claim is proven, and the page prints a helpful error on file://.
- Stale/wrong numbers → mitigate: verifier cross-checks against the actual A1/A2/E3 JSONs.
- pass@5 degeneracy at low seeds → label it as an optimistic upper bound (inherited A1 caveat).

## Success criteria
1. `leaderboard.html` renders a models-vs-pass@k table from `leaderboard.json` (separate file).
2. Numbers are real A1/A2/E3 values (verified, not placeholder).
3. The page provably loads the JSON over HTTP (verifier returns all-pass).
4. Clean, public-facing styling; no shared-core edits.
