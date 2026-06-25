# F12 — SUMMARY

## Task
Write a crisp 2-page non-academic summary for a YC / fundraising audience: the problem (SRE
autonomy), the insight (graduation / code-as-policy), the evidence (real A1/A2 numbers), market,
and ask. Punchy, honest, no jargon. Do not edit shared core files.

## Outcome: COMPLETED
Delivered a ~1,135-word (about 2 printed pages) fundraising memo plus an evidence ledger, with
every quantitative claim traced to a real A1/A2 artifact. No shared core file touched.

### The memo (artifacts/SRE_Degrees_2pager.md), 8 sections + footnote
- Problem: outages cost millions/hour; senior SREs are the bottleneck; the trap — the loudest
  alert points at a victim, not the cause, and the naive fix makes it worse.
- Insight (graduation / code-as-policy): keep the AI model FROZEN, make the code around it
  smarter via a watch -> check -> feedback -> retry loop; grade root-cause + correct-fix +
  trap-avoidance, not "did it come back up."
- Evidence (real): first-try success 0.23 -> 0.90 (~4x) on 42 incidents, graded by code;
  reproduced on a 2nd model 0.24 -> 0.89 (750 episodes, McNemar p<0.0001); honest negative —
  strip the feedback and the lift mostly vanishes, so "we know exactly where the lift comes from."
- Wedge: eval benchmark + graded data feed ("the SAT + practice problems for incident AI");
  autonomous response is the trust-gated expansion, not the ask.
- Market / Moat / Ask: picks-and-shovels under the AIOps category; moats = cascade catalog +
  root-cause-aware grader + model-agnostic graduation loop; raising [seed round] to make the
  benchmark the default third-party yardstick.

## Numbers — all real, all sourced (see artifacts/evidence_check.md)
| Claim | Value | Source |
|---|---|---|
| zero-shot first-try | 0.230 | A1 |
| REx first-try | 0.897 (~0.90) | A1 |
| 2nd-model corroboration | 0.240 -> 0.893 | A2 |
| significance | McNemar p<0.0001 | A2 |
| honest negative | rex_no_oracle 0.287 ~= best_of_n | A2 |

## Validation (07)
8/8 tests pass: word count 1,135 in [1100,1400]; all 5 topics; headline pair; 2nd-model pair;
honest negative; footnote rigor; zero undefined jargon; clean structure.

## Honest limits (09)
Evidence is benchmark/live-cluster stage, not production; only two models; lift is feedback-driven
(not search); no traction yet. A credible pre-seed research pitch, not a traction pitch — and it
doesn't pretend otherwise.

## Parallel-safety
All writes under experiments/ralph_outputs/F12/. No edit to rex/*, sim/*, agent/*,
experiments/*.py, status/dashboard, or other task dirs. Sources read-only.
