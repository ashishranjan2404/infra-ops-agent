# G3 — 01 Plan

## Objective
Answer "where would we rank on SREGym's pass@1 (E2E) leaderboard?" with an HONEST
positioning analysis. Insert our real pass@1 (from A1/A2) into SREGym's published
E2E leaderboard, produce a single ranked table, and surface explicit non-equivalence
caveats so the "rank" is never mistaken for an apples-to-apples claim.

## Approach
1. Research SREGym's published leaderboard numbers and cite sources (paper +
   leaderboard). B15 already transcribed these into `sregym_reported.json` with
   citations; reuse and re-cite so G3 is self-contained.
2. Pull OUR real pass@1 from the A1 (42-incident, glm-5p2) and A2 (deepseek-v4-pro,
   750-episode) result artifacts — no fabricated numbers.
3. Build a `rank_leaderboard.py` that merges both into ONE descending-sorted table
   with a rank column, tagging each of our conditions as "fair single-attempt" or
   "out-of-regime (multi-attempt + oracle)".
4. Render a report with a loud non-equivalence banner + honest positioning bullets.

## Files to create (all task-namespaced — NO shared core edits)
- `artifacts/rank_leaderboard.py` — stdlib ranking script (+ `--selftest`).
- `artifacts/sregym_reported.json` — cited frozen SREGym data (copied from B15).
- `artifacts/ranked_leaderboard.md` — generated ranked table + positioning.

## Dependencies
- Read-only: A1/A2 result JSON; B15's `our_pass_at_1.json` (distilled) + `sregym_reported.json`.
- Python 3.13 stdlib only. No network, no API, no cluster.

## Risks
- **Overlap with B15.** B15 built a *comparison table*; G3 must add the distinct
  *ranked-leaderboard placement* angle ("where would we rank") and not just duplicate.
- **Misleading rank.** A naive merge implies a fair fight. Mitigation: loud banner +
  regime tags + honest "we are bottom-of-board on fair terms" conclusion.
- **A1/A2 absent.** Then status would degrade; but both exist and are read live.

## Success criteria
- Ranking script runs, `--selftest` passes, emits a real ranked table from real data.
- Report states our fair rank (rank 8 of 13, lower band) and flags REx as out-of-regime.
- Sources cited; >=8 non-equivalence caveats; no shared core file edited.
