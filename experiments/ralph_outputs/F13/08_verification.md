# 08 — Verification against success criteria

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| poster.md AND poster.html both exist | ✅ | both in `artifacts/` (6.4 KB, 12 KB) |
| Both parse / are well-formed | ✅ | validator T1+T2 PASS; HTMLParser tag-stack balances |
| All 5 required sections present (motivation, method, benchmark, results, takeaways) | ✅ | T1 PASS in md; T3 confirms heading text in html |
| Print/poster CSS present (`@page`, `@media print`, A0 sizing) | ✅ | T3 PASS |
| Every quantitative claim cites a real repo source | ✅ | T5 PASS — all 9 cited file-paths exist |
| No placeholder / lorem | ✅ | T4 PASS |
| Did NOT edit shared core files | ✅ | all writes under `experiments/ralph_outputs/F13/` |
| Self-contained (opens offline) | ✅ | CSS fully inlined, system fonts, no external refs |

## Are the outputs real, not placeholder?
Yes. The poster carries the actual reward formula (`0.30·diagnosis + 0.25·correct_fix +
0.45·resolved − 0.60·trap`), the real frontier sweep table (5 named models, real baselines and
0.86 ceiling), the real honest band (haiku 0.27 / opus 0.50), the real verifier-generalization
numbers (0.90 vs 0.95, 14→3 rules), and the real ablation (REx 0.25 ≈ zero-shot 0.24) — each
sourced from `ARCHITECTURE.md` or `docs/headline_insights.md`, both of which exist in-repo.

## Honesty verification (the part a reviewer checks)
The poster does **not** present the +0.23 frontier lift as the unqualified headline. The
ablation showing the lift is largely oracle-feedback leakage appears as a co-equal `.rigor`
panel, same card/heading weight, explicitly flagged. The 0.86 figure is labeled the *designed*
safe ceiling, not a measured per-incident decomposition. The two-tier contract is stated
(sim = reproducible numbers; GKE = mechanism-validated only). These were the specific
integrity points raised by the AAAI-reviewer persona and Engineer B, and they are honored.
