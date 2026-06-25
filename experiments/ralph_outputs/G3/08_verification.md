# G3 — 08 Verification

## Success criteria (from 01) vs reality

| Criterion | Met? | Evidence |
|---|---|---|
| Research SREGym's published leaderboard numbers, cite sources | YES | `sregym_reported.json` with arXiv:2605.07161v1 + sregym.com/leaderboard, retrieved 2026-06-25; 8 E2E rows + partition breakdown. |
| Use OUR real pass@1 from A1/A2 | YES | `rank_leaderboard.py` reads A1/A2 (via B15 distilled, itself from A1/A2) live; numbers match A1/A2 SUMMARYs (rex 89.7%/89.3%, fair band ~31-35%). |
| Ranking table script (small) | YES | `rank_leaderboard.py`, stdlib-only, `--selftest` passes, emits `ranked_leaderboard.md`. |
| Analysis report | YES | `positioning_report.md` — cited numbers, merged ranking, honest bottom-of-board conclusion. |
| Explicit non-equivalence caveats | YES | 11 numbered caveats in the report; loud banner above the ranked table. |
| Answer "where would we rank" honestly | YES | Fair: rank 8/13 (~34.9%), above only Kimi-K2.5, below all frontier agents; REx nominal #1 but flagged out-of-regime/category-error. |
| No shared core files edited | YES | All outputs under `G3/`; git shows G3 untracked; pre-existing M/D files are from the session-start snapshot, not G3. |

## Outputs real, not placeholder?
- Numbers are read from real A1/A2 result artifacts and real cited SREGym data — no
  invented figures.
- The ranked table is script-generated (`rc=0`), not hand-written.
- Selftest enforces the invariants that make the conclusion defensible.

## Honesty check
The deliverable does NOT claim a SREGym win. It explicitly concludes we are a
bottom-of-board entry on fair terms and tags REx as out-of-regime. This is the honest,
non-flattering reading the task asked for.

**Verdict: meets all success criteria.**
