# J4 — 08 Verification

## Against success criteria (01)
| Criterion | Status | Evidence |
|---|---|---|
| Protocol covers both designs, randomization, confounds, power | ✅ | `04_spec.md` protocol section + `required_n_paired` |
| Metrics + statistics defined | ✅ | speedup (GM ratio), median, %-within-SLO, Cliff's delta; t-test/Wilcoxon/Mann-Whitney/bootstrap |
| Runnable analysis harness | ✅ | `mttr_analysis.py` self-test exits 0; CLI runs on CSV/JSON |
| Simulation on synthetic timing data | ✅ | `simulate_trials.py` → `trials_*.csv`; grounded in A9 |
| Recovers planted speedup within tolerance | ✅ | within 1.50x (planted 1.8, attenuated), between 1.87x |
| Null correctly non-significant | ✅ | T5: speedup 0.96, p=0.34, CI brackets 1.0 |
| Both designs run | ✅ | within + between reports produced |
| Reuse A9 mttr_labels as baseline | ✅ | `used_a9: True`; baselines drawn from real labels |
| No shared core files edited | ✅ | only J4/artifacts/ + read-only A9 |
| scipy-optional / hermetic | ✅ | T2 no-scipy fallback ALL PASS |

## Are outputs real (not placeholder)?
- `report_within.json` / `report_between.json` are produced by actually running
  the harness on actually-generated CSVs — copied verbatim into `07`.
- Numbers are internally consistent: gm_control 277.5 / gm_agent 184.4 = 1.505 =
  reported speedup; pct_reduction 33.55 = (1 - 1/1.5049)*100. Checks out.
- Self-test asserts CI brackets the estimate AND a null case — a constant/broken
  estimator cannot pass both, so PASS is meaningful, not vacuous.

## What is NOT verified (honest)
- **No real human timing data** — the speedup numbers are from SIMULATION with a
  KNOWN planted effect; they validate the *analysis*, they do not measure a real
  agent's real MTTR improvement. That requires the staged-replay lab (the blocker).
- `resolved=False` exclusion not yet wired (field captured, documented in `09`).

## Conclusion
Deliverable (protocol + metrics/stats + harness + grounded simulation) is REAL,
runnable, and self-validating. The real-world measurement is correctly scoped as
a blocker, not faked.
