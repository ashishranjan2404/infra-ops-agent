# H9 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/H9/artifacts/`)

### 1. `leaderboard.json` — the data
9 ranked `entries` + 1 `blocked` arm, every number mined from real completed tasks:

| source | system | model | family | n | pass@1 |
|---|---|---|---|---|---|
| A1 | REx (tree + oracle) | glm-5p2 | all-42 | 126 | **0.897** [0.83,0.94] |
| A2 | REx (tree + oracle) | deepseek-v4-pro | all-30 | 150 | **0.893** [0.834,0.933] |
| A1 | retry_realistic | glm-5p2 | all-42 | 126 | 0.349 |
| A1 | best_of_n | glm-5p2 | all-42 | 126 | 0.341 |
| A1 | rex_no_oracle | glm-5p2 | all-42 | 126 | 0.333 |
| A1 | zero_shot | glm-5p2 | all-42 | 126 | 0.230 |
| A2 | zero_shot | deepseek-v4-pro | all-30 | 150 | 0.240 |
| E3 | OpenSRE-trained (GRPO) | opensre-qwen3-8b | cascade-14 | 28 | 0.107 |
| E3 | zero_shot (base 8B) | qwen3-8b-base | cascade-14 | 28 | 0.071 |
| E3 | Fireball-trained | — | — | — | **BLOCKED** (no model/data; not fabricated) |

Sources of truth:
- A1 → `experiments/ralph_outputs/A1/artifacts/summary_table.json`
- A2 → `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` (`by_condition`)
- E3 → `experiments/ralph_outputs/E3/artifacts/result_three_way.json` (`by_arm`)

### 2. `leaderboard.html` — the page
Single self-contained file, zero external deps (no CDN/framework). Vanilla JS:
- `fetch("leaderboard.json")` → builds the `<table>` at runtime (data/render split).
- Sortable columns (click any header), family filter dropdown, text search.
- pass@1 cell shows percentage + a CI bar; REx rows highlighted gold.
- Separate "Blocked / not evaluated" panel for the Fireball arm.
- On fetch failure (e.g. `file://`) it renders an actionable "serve over HTTP" message
  rather than a blank page.
- Public-facing dark theme, responsive, tabular-aligned numbers.

### 3. `verify_leaderboard.py` — proof it works
Stdlib-only. Schema-checks the JSON, cross-checks 5 real anchor numbers against A1/A2/E3,
confirms the HTML fetches the JSON, then **serves the directory over HTTP and GETs both files**
to prove the page actually loads the JSON (the task's explicit "verify it loads" requirement).

## Shared-core files touched
None. Everything is task-namespaced under `H9/artifacts/`. No `rex/*`, `sim/*`, `agent/*`,
`experiments/*.py`, dashboard, or `ralph_status.json` edits.

## How to view
```
cd experiments/ralph_outputs/H9/artifacts
python3 -m http.server 8080      # then open http://localhost:8080/leaderboard.html
python3 verify_leaderboard.py    # all checks should pass
```
