# G3 — 06 Implementation

## What I built (all in `experiments/ralph_outputs/G3/artifacts/`, no shared core edits)

1. **`rank_leaderboard.py`** — stdlib-only ranking script. Loads cited SREGym data +
   our real A1/A2 pass@1, merges into one descending-sorted leaderboard with a `rank`
   column, tags each of our conditions fair vs out-of-regime, and renders a markdown
   table with a non-equivalence banner directly above it plus honest-positioning bullets.
   - `load_ours()`: prefers B15's distilled `our_pass_at_1.json`; falls back to
     recomputing pass@1 from A1/A2 raw result JSON via `_pass_at_1_from_result()` +
     `_wilson_ci()` so G3 is not hard-coupled to B15.
   - `build_ranked_rows()`: produces the ordinal merge; `render()`: the report block.
   - `--selftest`: 6+ assertions on data integrity, sort order, rank permutation, and
     the fair-band-below-SREGym-top invariant.

2. **`sregym_reported.json`** — cited, frozen SREGym leaderboard (8 E2E rows + partition
   breakdown), copied from B15 and re-cited (arXiv:2605.07161v1 + sregym.com/leaderboard,
   retrieved 2026-06-25) so G3 stands alone.

3. **`ranked_leaderboard.md`** — script-generated ranked table (13 rows) + positioning.

4. **`positioning_report.md`** — the primary analysis: cited SREGym numbers, our A1/A2
   pass@1, the merged ranking, honest "bottom-of-board on fair terms" conclusion, and 11
   numbered non-equivalence caveats.

## How it differs from B15 (no duplication)
B15 produced a side-by-side *comparison* table. G3 answers the specific "**where would we
RANK**" question by inserting our rows into SREGym's actual ordinal leaderboard and
emitting a single ranked list with explicit rank numbers (fair band = rank 8/13; REx =
nominal rank 1 but flagged out-of-regime). The ranking script and ranked output are new.

## Real-data provenance
- Our pass@1 is read at run time from A1/A2 artifacts (via B15's distilled file, which
  itself derives from A1/A2). Nothing hand-typed for our numbers.
- SREGym numbers are transcribed from the cited paper/leaderboard and frozen (not scraped).

## Parallel safety
Reads A1/A2/B15 read-only; writes only under `G3/artifacts/`. No `rex/*`, `sim/*`,
`agent/*`, `experiments/*.py`, status, or dashboard files touched.
