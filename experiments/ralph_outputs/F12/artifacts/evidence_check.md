# F12 — Evidence Check (every memo claim → real source)

All numbers in `SRE_Degrees_2pager.md` trace to A1/A2 outputs or ARCHITECTURE.md. No invented
quantitative claims.

| Memo claim | Number | Source |
|---|---|---|
| First-try success ~a quarter off the shelf | 0.23 | A1 SUMMARY.md / result.json: zero_shot pass@1 = 0.230 [0.17,0.31] |
| Graduation lifts first-try success to 0.90 | 0.90 | A1: rex pass@1 = 0.897 [0.83,0.94] |
| ~4x improvement | 0.23→0.90 | A1 (derived: 0.897/0.230 ≈ 3.9) |
| 42 incidents, simple/cascade/novel | 42 (12/20/10) | A1 SUMMARY.md |
| 5 conditions, 630 episodes, 0 errors | 5 / 630 / 0 | A1 SUMMARY.md |
| Graded by code, not a model judging itself | deterministic P0 judge | A1 SUMMARY ("deterministic P0 judge"); A2 ("Deterministic P0 judge (no LLM judge)") |
| Non-overlapping baselines | disjoint 95% CIs | A1: rex [0.83,0.94] vs zero_shot [0.17,0.31] |
| Reproduces on a second model (0.24 → 0.89) | 0.240 → 0.893 | A2 SUMMARY.md / result.json (deepseek-v4-pro) |
| Second model: 750 episodes, 0 errors | 750 / 0 | A2 SUMMARY.md |
| Paired significance p<0.0001 | McNemar p<0.0001 | A2 SUMMARY.md |
| Honest negative: strip feedback → lift vanishes | rex_no_oracle 0.287 ≈ best_of_n 0.307 | A2 SUMMARY.md ("rex_no_oracle ~= best_of_n ... lift is the oracle feedback content, not the tree") |
| n=126 per condition (3 seeds) | 126 / 3 | A1 SUMMARY ("n=126 per condition", seeds=3) |
| Reward formula | 0.30/0.25/0.45/−0.60 | ARCHITECTURE.md reward line |
| Frozen, model-agnostic policy | — | ARCHITECTURE.md / memory note (code-as-policy, no fine-tuning) |
| Two-tier sim + live cloud cluster | — | ARCHITECTURE.md (Tier-A sim + Tier-B M-real on GKE) |

## Labeled estimates (NOT measured — flagged as such in the memo)
- "AIOps is one of the fastest-growing slices" — labeled "(directional estimate, not a measured figure)".
- Outage cost "millions per hour" — industry-common framing, stated qualitatively, no precise figure claimed.
- Raise size / 12-month milestone — placeholder `[seed round]`, no fabricated traction, customers, or pipeline.

## Forbidden-number audit
No revenue, customer count, LOIs, or precise TAM dollar figure appears in the memo. PASS.
