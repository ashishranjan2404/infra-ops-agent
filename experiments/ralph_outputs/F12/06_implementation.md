# F12 — 06 Implementation

## What I built
A self-contained, fact-checked 2-page fundraising memo plus its evidence ledger. No shared
core file was touched (this is a writing task).

### Artifacts created (all task-namespaced under F12/artifacts/)
1. **`SRE_Degrees_2pager.md`** — the deliverable. ~1,135 words / ~2 printed pages, 8 sections
   + a rigor footnote. Covers all 5 required topics:
   - **Problem** (§1): outage cost + the trap — loudest alert points at a victim, naive fix
     makes it worse.
   - **Why now** (§2): frontier models exist but are right only ~1/4 of the time first-try.
   - **Insight** (§3): *graduation / code-as-policy* in plain English — model stays frozen, the
     code scaffold gets smarter; grade root-cause+fix+trap, not "did it come back up."
   - **Evidence** (§4): 0.23 → 0.90 first-try success, reproduced on a 2nd model (0.24 → 0.89),
     graded by code; plus the honest negative (strip feedback → lift vanishes).
   - **Product/wedge** (§5): eval benchmark + graded data feed ("SAT + practice problems").
   - **Market** (§6), **Moat** (§7), **Ask** (§8).
2. **`evidence_check.md`** — claim→source table; every quantitative claim maps to an A1 or A2
   artifact (or ARCHITECTURE.md for the design facts). Estimates explicitly labeled; a
   forbidden-number audit (no fabricated revenue/customers/TAM) that PASSES.

## Design decisions implemented (from the grill + ouroboros)
- One headline stat in the body, all rigor (n, seeds, McNemar, deterministic grader) compressed
  into a single footnote.
- Trap = early credibility color; graduation = the moat paragraph, NOT the lead, phrased to not
  spook an operator.
- Wedge = eval + data engine; autonomous response explicitly the expansion, trust-gated.
- Honest negative framed as "we know where the lift comes from / the feedback content is the
  product."
- Jargon scrubbed: no "pass@k / Thompson / FIREBALL / MCTS / oracle" in the memo (verified in 07).

## Source inputs (read-only, not modified)
- `experiments/ralph_outputs/A1/{SUMMARY.md,result.json}`
- `experiments/ralph_outputs/A2/{SUMMARY.md,result.json}`
- `ARCHITECTURE.md`, memory note `rl-project-framing.md`.
