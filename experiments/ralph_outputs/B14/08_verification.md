# B14 — Verification against success criteria

| Success criterion (from 01_plan) | Met? | Evidence |
|---|---|---|
| Runnable script ingesting real result JSONs | ✅ | `cost_per_dollar.py` ingests A1 + A2 pass@1 artifacts; run output shows `[ok]` for both. |
| Emits cost-efficiency table with pass@1-per-$ per (model, condition) | ✅ | `cost_efficiency_table.md` + `cost_efficiency.json`, 10 rows (5 conditions × 2 models), each with `pass@1_per_dollar`. |
| Token/cost model with per-model $/token | ✅ | `cost_model.py` `PRICES` table; real Claude prices + assumed gateway slugs, each flagged. |
| Uses token counts if logged, else documented assumptions | ✅ | Tokens not logged (verified) → call-shape model from real code, every assumption a named constant. |
| Cost model unit-tested | ✅ | 9/9 tests pass (`test_cost_model.py`). |
| Real numbers, not placeholders | ✅ | pass@1 values read verbatim from the result JSONs (glm-5p2 rex=0.8968, deepseek rex=0.8933); $ computed, not hardcoded. |
| No shared core file edited | ✅ | All artifacts under `B14/artifacts/`; `git status` shows no modification to `rex/*.py`/`sim/*.py`/etc. by this task. |

## Are outputs real?
Yes. The pass@1 figures are lifted directly from the existing A1/A2 artifacts (independently
produced eval runs). The cost figures are *estimates* — clearly labelled ESTIMATED in the table
header and via per-row `price_assumed` — derived from the actual proposer `max_tokens=1400`,
`N=4` budget, and the real Anthropic price sheet. Nothing is a placeholder; the one genuinely
un-pinnable input (`retry_realistic` retry count) is flagged as an assumed expected value.

## Interpretation (the honest read, per ouroboros Engineer-3)
The bare "most cost-efficient = zero_shot" line is a floor-cost artifact: zero_shot is cheapest
(1 call) so it tops $/pass, but it leaves ~77% of incidents unresolved (pass@1≈0.23). The
load-bearing finding is on the **iso-cost comparison**: at the *same* 4-call budget, **rex buys
0.90 pass@1 vs best_of_n's 0.34** — 2.6× the pass rate for the same dollars — and rex's
pass@1-per-$ (87.3) essentially matches zero_shot's (89.6) while delivering ~4× the absolute pass
rate. So rex is the efficient operating point at high pass@1, and best_of_n / rex_no_oracle are
strictly dominated (same cost, lower pass@1).

## Independent recomputation spot-check
glm-5p2 rex: cost/incident = 4 calls × (1200·0.6/1e6 + 1400·0.6·2.2/1e6)
= 4 × (0.00072 + 0.0018480·... ) → script reports $0.010272; pass@1 0.8968 / 0.010272 = 87.31. ✔
matches the emitted `pass@1_per_dollar`.
