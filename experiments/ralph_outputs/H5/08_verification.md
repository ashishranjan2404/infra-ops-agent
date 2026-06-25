# H5 — 08 Verification

## Against the task's success criteria
| Criterion | Met? | Evidence |
|---|---|---|
| Real self-contained HTML dashboard in artifacts dir | YES | `artifacts/dashboard.html`, no external deps (pure HTML/CSS/vanilla JS). |
| Reads a results JSON manifest | YES | `fetch("sample_manifest.json")` + file-picker; `validate()` enforces schema. |
| Shows model/condition pass@k | YES | Per-model table: pass@1 (bar+CI), pass@2, pass@5, per-family pass@1. |
| Promotion-gate view | YES | Counters + per-row PROMOTE/HOLD/REJECT tag with reasons; threshold tick on bar. |
| Sample manifest from REAL A1/A2 numbers | YES | `gen_manifest.py` reads A1 `summary_table.json` and A2 `ablation_pass_at_k_deepseek-v4-pro.json`; no hand-typed numbers. |
| Verify the HTML loads it | YES | HTTP 200 on both resources (T4) + Node DOM-shim render yielding correct counts (T5). |
| Do NOT edit shared core files / existing dashboard | YES | Only new files under `H5/`; `experiments/dashboard.html` untouched (verified by git status — not in modified set). |

## Are outputs real, not placeholder?
- The manifest's every number traces to a real upstream run (A1 = 630 episodes glm-5p2;
  A2 = 750 episodes deepseek-v4-pro). The generator fails loudly if those files are missing
  — it cannot emit fabricated data.
- The gate is genuinely discriminative: it rejects 8/10 candidates including the
  `rex_no_oracle` ablation, and promotes only the two true REx rows. A placeholder gate
  would promote everything or be hardcoded.

## Spot-check (numbers match source)
- A1 `rex.overall.p1 = 0.8968`, `ci = [0.8315, 0.9387]` → manifest `glm-5p2/rex`
  `pass_at_1 0.8968`, `ci_lo 0.8315`. Match.
- A2 `by_condition.rex.overall.pass@1 = 0.8933`, `ci95 = [0.8338, 0.9333]` → manifest
  `deepseek-v4-pro/rex` `pass_at_1 0.8933`, `ci_lo 0.8338`. Match.

## Verdict: meets all stated success criteria with real, verifiable artifacts.
