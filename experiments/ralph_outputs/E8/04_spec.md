# E8 — 04 Spec

## Module: `fireball_sweep.py`

### Data structures
```python
@dataclass
class Record:
    rid: str          # trajectory id (de-dup key)
    family: str       # incident family (stratum dim 1)
    difficulty: int   # 0 if absent (stratum dim 2)
    n_steps: int      # len(trajectory[])
    raw: dict         # original record
    @property
    def stratum -> str   # f"{family}::d{difficulty}"
```

### Record-shape detection (Fireball-format tolerance)
- id      ← first present of `trajectory_id | id | uid`
- family  ← first present of `incident | failure_mode | family | scenario_id`
- traj    ← first present of `trajectory | steps | messages`  (must be a list)
- A record missing id, family, or list-trajectory is **skipped** (not Fireball-shaped).

### Function signatures + contracts
```python
read_corpus(path) -> list[Record]
  # skips blank + non-fireball lines; de-dups on rid; RAISES ValueError on bad JSON.

corpus_profile(recs) -> dict
  # {n_records, n_families, per_family, per_difficulty, mean_steps}

stratified_subset(recs, n, seed="E8") -> list[Record]
  # |out| == min(n, len(recs)); deterministic for fixed (n, seed);
  # preserves family::difficulty proportions (largest-remainder apportionment);
  # NESTED: subset(N1,seed) ⊂ subset(N2,seed) for N1<N2 (stable hash prefix).

required_n_for_effect(delta, sd, alpha=0.05, power=0.80) -> int
  # per-arm N = ceil( 2 * ((z_{1-α/2}+z_power)*sd/delta)^2 ); RAISES if delta<=0 or sd<=0.

fit_learning_curve(points: list[(int,float)]) -> dict | None
  # None unless >=4 distinct points. Else grid-fit score(N)=a-b*N^(-c);
  # returns {a,b,c,sse,asymptote,knee_N_95pct,n_points}.

run_sweep(recs, n_grid, seeds, fit=None, out_dir=None) -> dict
  # fit: (subset, seed)->score in [0,1], the REAL trainer/eval. Optional.
  # returns {n_grid, seeds, points:[{requested_N,actual_N,seed,score,n_families,
  #          per_difficulty[,manifest]}], blocked: fit is None, learning_curve}
  # with fit=None: every score is None, blocked=True, learning_curve=None.
```

### File formats
- **Input corpus**: JSONL, one Fireball record per line (real:
  `opensre-traj/out/trajectories.jsonl`).
- **Subset manifest** (`subset_N{n}_{seed}.manifest.json`):
  `{requested_N, actual_N, seed, ids:[rid...], profile:{...}}`.
- **CLI stdout**: JSON `{corpus, profile, power_analysis, sweep}`
  (or `{corpus, profile, power_analysis}` with `--profile-only`).

### Test cases (pytest) — see `test_fireball_sweep.py`
1. reader parses all fixture records
2. reader skips non-fireball + blank + dup id
3. reader raises on bad JSON
4. subset size + cap at corpus size + empty on n=0
5. subset deterministic per seed, differs across seeds
6. subset preserves per-difficulty strata (<0.05 deviation)
7. nested subsets (>0.8 overlap)
8. power N monotone in δ and sd
9. power N matches closed-form known value
10. power rejects δ<=0 / sd<=0
11. **no fit ⇒ blocked + all scores None + no curve** (anti-fabrication)
12. **fitter returns None on <4 points; dict on >=4** (anti-fabrication)
13. fit callback wiring records scores

## Module: `make_fixture.py`
`make(n, seed) -> list[dict]` — n Fireball-shaped records over 8 families × diffs
{3,4,5} (weights .3/.6/.1), alternating assistant/tool trajectory, **no score field**.
CLI writes `fixture_corpus.jsonl`.
