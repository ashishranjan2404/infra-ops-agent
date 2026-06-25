# B14 — SUMMARY: Cost-Normalized Metric (pass@1 per dollar)

## Deliverable
A cost-efficiency harness computing **pass@1 per dollar of (estimated) API spend** from the
existing REx evaluation artifacts, plus a token/cost model with per-model $/token pricing.

## Artifacts (all under experiments/ralph_outputs/B14/artifacts/, no shared core edits)
- cost_model.py — per-model price table (real Claude: Opus 4.8 $5/$25, Sonnet 4.6 $3/$15,
  Haiku 4.5 $1/$5; gateway/Fireworks slugs as flagged assumptions) + per-condition call-shape
  (proposer calls/job from rex/eval_pass_at_k.py: zero_shot=1, best_of_n=rex=rex_no_oracle=4,
  retry_realistic~2.3; deterministic P0 judge = $0) + estimate_job_cost().
- cost_per_dollar.py — ingests real A1 (glm-5p2, 42 incidents) and A2 (deepseek-v4-pro, 30
  incidents) pass@1 JSONs, emits the cost-efficiency table.
- test_cost_model.py — 9 unit tests (all pass).
- cost_efficiency.json / cost_efficiency_table.md — generated outputs (10 rows).

## How it ran
python3 cost_per_dollar.py ingested both real result JSONs, produced 10 rows (5 conditions x 2
models). Unit tests 9/9. Arithmetic spot-check confirmed (glm-5p2 rex = $0.010272/incident ->
0.8968/0.010272 = 87.31 pass@1/$).

## Key finding
At EQUAL cost (4 proposer calls), rex buys 0.90 pass@1 vs best_of_n's 0.34 — 2.6x the pass rate
for the same dollars. rex's pass@1-per-$ (87.3) essentially matches the cheapest baseline
zero_shot (89.6) while delivering ~4x the absolute pass rate => rex is the efficient frontier
point at high pass@1; best_of_n and rex_no_oracle are strictly dominated. The naive "zero_shot is
most cost-efficient" line is a floor-cost artifact (cheapest, but leaves ~77% unresolved); the
load-bearing comparison is iso-cost.

## Honest caveat / blocker
Cost is ESTIMATED, not measured: no token counts are logged in any result JSON (agent/llm.py:call
discards the provider usage block; the eval harness never records tokens). All $ come from the
call-shape + price model with named overridable assumptions. The measurement upgrade (thread usage
into the result JSON) edits a shared core file, so it was documented as a follow-up, not applied.
The iso-cost finding is robust to pricing assumptions; absolute dollars are not.

## Status: completed
