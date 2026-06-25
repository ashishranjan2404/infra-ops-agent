# G3 — 04 Spec

## Inputs
- `sregym_reported.json` (cited, frozen). Schema (subset used):
  - `n_problems: int` (90), `version_note: str` (citation), `leaderboard: [ {agent,
    model, noise:bool, diagnosis, mitigation, e2e:float, source} ]`,
    `partition_breakdown`, `key_finding`.
- Our pass@1: prefer `B15/artifacts/our_pass_at_1.json` (distilled, schema
  `by_run[run][cond].overall.{p1,ci,n}`); fallback recompute from A1/A2 raw via
  `_pass_at_1_from_result()`.

## Data structures
- Ranked row: `{rank:int, system:str, p1:float, kind:"SREGYM"|"OURS",
  regime:str, ci:[lo,hi]|None, n:int, fair:bool(OURS only)}`.

## Function signatures
- `_wilson_ci(k:int, n:int, z=1.96) -> (lo,hi)` — score-interval, for raw fallback.
- `_pass_at_1_from_result(result:dict) -> {cond: {p1,ci,n}}` — schema-tolerant reducer.
- `load_ours() -> ({run:{cond:{p1,ci,n}}}, src:str)` — distilled-first, raw fallback.
- `load_sregym() -> dict`.
- `build_ranked_rows(sregym, ours) -> [row]` — merges, sorts desc by p1, assigns rank.
- `render(rows, ours_src, sregym) -> str` — banner + table + positioning markdown.
- `selftest()` / `main()`.

## Constants
- `FAIR_CONDITIONS = {zero_shot, best_of_n, retry_realistic, rex_no_oracle}`
- `OUT_OF_REGIME = {rex}`

## Output format (`ranked_leaderboard.md`)
1. H1 title.
2. Blockquote NON-EQUIVALENCE BANNER (directly above table).
3. Two source-citation bullets.
4. Markdown table: `rank | system | pass@1 (E2E) | 95% CI | n | regime`, OURS rows
   marked `**<- OURS**`, descending by pass@1.
5. `## Honest positioning` — fair-band bullet (rank + band placement), REx out-of-regime
   bullet, shared "novel is hardest" bullet.

## Test cases (`--selftest`, all asserts)
- `n_problems == 90`; `len(leaderboard) >= 8`.
- A1 numbers present and non-empty.
- ranks form a permutation `1..N`.
- rows sorted descending by p1.
- REx row present, p1 > 0.8, tagged not-fair.
- at least one fair OURS row; `max(fair p1) < max(SREGym e2e)`.

## API / invariants
- Stdlib only; no network at run time (SREGym numbers frozen + cited).
- Reads A1/A2/B15 read-only. Writes only inside `G3/artifacts/`.
