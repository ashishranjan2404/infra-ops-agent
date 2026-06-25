# G3 — SREGym pass@1 (E2E) leaderboard: where would we rank?

> **NON-EQUIVALENCE BANNER.** This table inserts OUR numbers into SREGym's E2E leaderboard *for positioning only*. SREGym rows are **live Kubernetes** single-attempt E2E (diagnosis AND mitigation, n=90). OUR rows are a **deterministic simulator** with a reward@0.8 grader, different incidents, cheaper models. The 'rank' column is NOT a fair-fight ranking — it is a number line. See caveats.

- SREGym source: Numbers transcribed from SREGym paper (arXiv:2605.07161v1) and the public leaderboard (sregym.com/leaderboard), retrieved 2026-06-25. Frozen here for reproducibility; not scraped at run time.
- Our source: B15/artifacts/our_pass_at_1.json (distilled from A1/A2)

| rank | system | pass@1 (E2E) | 95% CI | n | regime |
|---:|---|---:|---|---:|---|
| 1 | OURS REx (sim, glm-5p2) [OUT-OF-REGIME] **<- OURS** | 89.7% | [0.83,0.94] | 126 | multi-attempt + ORACLE (no SREGym analogue) |
| 2 | Claude Code (Claude Sonnet 4.6) | 60.7% |  | 90 | live single-attempt E2E |
| 3 | Stratus (Claude Sonnet 4.6) | 54.8% |  | 90 | live single-attempt E2E |
| 4 | Claude Code (Claude Sonnet 4.6, noise) | 53.7% |  | 90 | live single-attempt E2E |
| 5 | Codex (GPT-5.4) | 53.3% |  | 90 | live single-attempt E2E |
| 6 | Codex (GPT-5.4, noise) | 45.9% |  | 90 | live single-attempt E2E |
| 7 | Stratus (Claude Sonnet 4.6, noise) | 40.2% |  | 90 | live single-attempt E2E |
| 8 | OURS retry_realistic (sim, glm-5p2) **<- OURS** | 34.9% | [0.27,0.44] | 126 | sim single-attempt |
| 9 | OURS best_of_n (sim, glm-5p2) **<- OURS** | 34.1% | [0.26,0.43] | 126 | sim single-attempt |
| 10 | OURS rex_no_oracle (sim, glm-5p2) **<- OURS** | 33.3% | [0.26,0.42] | 126 | sim single-attempt |
| 11 | Stratus (Kimi K2.5) | 32.9% |  | 90 | live single-attempt E2E |
| 12 | Stratus (Kimi K2.5, noise) | 30.4% |  | 90 | live single-attempt E2E |
| 13 | OURS zero_shot (sim, glm-5p2) **<- OURS** | 23.0% | [0.17,0.31] | 126 | sim single-attempt |

## Honest positioning

- **Fair single-attempt comparison:** our best in-regime condition is 34.9% (retry / best_of_n), landing at rank 8. It sits in the LOWER part of SREGym's E2E band (30.4%–60.7%): above only the 2 weakest SREGym entries (Kimi-K2.5 Stratus), and below every frontier-model agent. On a like-for-like single-attempt basis we are a bottom-of-board entry, not a leader.
- **REx (89.7%) would 'top' the table**, but it is out-of-regime: it consumes multiple attempts AND a P0 oracle hint that SREGym agents never get. Treat its placement as a CATEGORY ERROR, not a win. (A1 also shows rex_no_oracle collapses to ~33%, i.e. the tree alone buys little — the oracle is doing the work.)
- **Both benchmarks agree** novel/unseen failures are hardest: SREGym E2E collapses ported->new (60.8->28.2 Claude Code; 63.7->17.9 Stratus), and our zero_shot cascade pass@1 is 6.7%.
