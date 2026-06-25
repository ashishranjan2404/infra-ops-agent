# E8 — 08 Verification

## Against success criteria (from 01/03)
| criterion | met? | evidence |
|---|---|---|
| Harness reads real corpus + profiles it | YES | profile: 319 recs, 34 families, diff {3:100,4:201,5:18} |
| Sweep caps at corpus size (degrade honestly) | YES | every N∈{1k..50k} → actual_N=319, blocked:true |
| Power analysis returns monotone, known-value N | YES | δ-grid 76→1900; `test_power_analysis_known_value` passes |
| Fixture sweep exercises 100→2000 with strata kept | YES | 07 fixture table, .3/.6/.1 preserved |
| All pytest tests pass | YES | 13 passed |
| No score/curve fabricated | YES | scores None, curve None on real run; demo labelled illustrative |
| No shared core file touched | YES | only new files under E8/artifacts/ (git check below) |

## Real, not placeholder?
- `fireball_sweep.py` (~330 LoC) is executable and exercised end-to-end on BOTH the real
  corpus and a 2000-record fixture.
- The 13 tests run actual logic (determinism, strata deviation <0.05, nesting >0.8,
  closed-form power match), not stubs.
- Subset manifests are real JSON files with real id lists (`sweep_manifests/`).
- The headline scaling curve is genuinely **absent** because the data is absent — that is
  the honest result, not a placeholder.

## The two N questions, separated (per 05 Engineer A)
1. **Training N (the headline "1k/10k/50k?"): BLOCKED.** Requires Fireball data above 319 +
   a fit callback. Not computable; not fabricated.
2. **Eval N (measurement budget per sweep point): COMPUTED.** To detect a δ=0.05 mean-reward
   gap between two policies at α=.05/power=.80 needs ~304 eval rollouts/arm (sd≈0.22). This
   is what the power analysis delivers as a real, usable number today.

## No-shared-core verification
```
$ git status --porcelain | grep -v '^?? experiments/ralph_outputs/E8/'
```
Expected: empty (all E8 outputs are new untracked files; no tracked core file modified).
See 07 for the actual run; verified at write time that only `experiments/ralph_outputs/E8/`
paths were created.
