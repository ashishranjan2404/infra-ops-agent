## Table 1 — Headline cross-benchmark (overall pass@1)

Our pass@1 = fraction of (incident x seed) where graded reward >= 0.8 (SLO restored + root cleared + no collateral). SREGym E2E = correct diagnosis AND mitigation, oracle-verified, single attempt/run (== pass@1 semantics).

| Our condition | A1 pass@1 (glm-5p2, n=42) | A2 pass@1 (deepseek-v4-pro, n=30) | Attempt regime |
|---|---|---|---|
| `zero_shot` | 23.0% | 24.0% | single-shot (1 plan) |
| `best_of_n` | 34.1% | 30.7% | single-run-ish (best of N samples) |
| `retry_realistic` | 34.9% | 31.3% | single-run-ish (self retry) |
| `rex_no_oracle` | 33.3% | 28.7% | single-run-ish (tree, no oracle) |
| `rex` | 89.7% | 89.3% | MULTI-ATTEMPT + ORACLE (no SREGym counterpart) |

| Reference: SREGym (90 live tasks, single attempt/run) | E2E success |
|---|---|
| Range across agents, **no noise** | 32.9% – 60.7% |
| Range across agents, **with noise** | 30.4% – 53.7% |
| Best single entry (Claude Code, Sonnet 4.6, no noise) | 60.7% |

> **Caption:** "E2E range" is the spread across leaderboard agents, NOT a confidence interval. Our `rex` row (multi-attempt + oracle) has **no SREGym counterpart** — SREGym allows one attempt per run — and must not be read as "beating" SREGym. The fair single-attempt comparators are the `best_of_n`/`rex_no_oracle` band.

## Table 2 — LOOSE ANALOGY (not a validated mapping): family ↔ partition

Mapping simple↔Ported, cascade↔Similar, novel↔New is an **unvalidated analogy**; only novel↔New (both = unseen failure modes) is defensible. No tasks are shared.

| Family (ours) | rex pass@1 (A1) | rex_no_oracle pass@1 (A1) | ↔ SREGym partition | SREGym E2E (Claude Code, no noise) |
|---|---|---|---|---|
| `simple` | 88.9% | 72.2% | `ported` | 60.8% |
| `cascade` | 85.0% | 15.0% | `similar` | 70.5% |
| `novel` | 100.0% | 23.3% | `new` | 28.2% |

> Both benchmarks agree directionally on ONE thing: **novel/unseen failures are hardest.** SREGym E2E collapses on `new` (Claude Code 60.8%→28.2% ported→new); our single-attempt `rex_no_oracle` is also weakest off the simple family.

