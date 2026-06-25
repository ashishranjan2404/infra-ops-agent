# H9 — Public-facing leaderboard page — SUMMARY

## TL;DR
Built a real, clean, **JSON-driven static leaderboard** (SREGym-style) that renders a
**models-vs-pass@k** table, populated with **real numbers from tasks A1, A2, and E3** (no
placeholders, no fabrication). The page provably loads its JSON over HTTP (29/29 verification
checks pass).

## Deliverables (all under `experiments/ralph_outputs/H9/artifacts/`)
- `leaderboard.json` — 9 ranked entries + 1 blocked arm; every cell traced to a source task.
- `leaderboard.html` — single zero-dependency page; `fetch()`es the JSON, builds a sortable /
  filterable table with pass@1 CI bars, highlighted REx rows, family filter, and a separate
  "blocked / not evaluated" panel. Renders offline; graceful `file://` error handling.
- `verify_leaderboard.py` — schema check + 5 real-number cross-checks against A1/A2/E3 +
  live HTTP load test. **29/29 pass.**

## Headline rows (real numbers)
| system | model | family | n | pass@1 (95% CI) | source |
|---|---|---|---|---|---|
| REx (tree + oracle) | glm-5p2 | all-42 | 126 | **0.897** [0.83,0.94] | A1 |
| REx (tree + oracle) | deepseek-v4-pro | all-30 | 150 | **0.893** [0.83,0.93] | A2 |
| zero_shot | glm-5p2 | all-42 | 126 | 0.230 [0.17,0.31] | A1 |
| OpenSRE-trained (GRPO) | opensre-qwen3-8b | cascade-14 | 28 | 0.107 | E3 |
| zero_shot (base 8B) | qwen3-8b-base | cascade-14 | 28 | 0.071 | E3 |
| Fireball-trained | - | - | - | BLOCKED (no model/data) | E3 |

## How to view
```
cd experiments/ralph_outputs/H9/artifacts
python3 -m http.server 8080   # open http://localhost:8080/leaderboard.html
python3 verify_leaderboard.py # 29/29 checks
```

## Honesty / limitations
- Cross-family/cross-model ranking is mitigated (family tag + filter) not eliminated.
- pass@5 flagged as a low-seed optimistic upper bound (inherited A1 caveat).
- Blocked Fireball arm shown explicitly; no fabricated numbers.
- No shared core files edited; fully task-namespaced and parallel-safe.
