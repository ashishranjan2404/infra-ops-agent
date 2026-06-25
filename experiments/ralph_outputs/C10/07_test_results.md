# 07 — Test Results

## T1 — Syntax / AST parse
```
$ python3 -c "import ast; ast.parse(open('experiments/ralph_outputs/C10/artifacts/bench_is_safe.py').read()); print('syntax OK')"
syntax OK
```
**PASS.**

## T2 — Import sanity (is_safe imports from rex.harness)
```
$ python3 -c "from rex.harness import is_safe; print('import ok')"
import ok
```
**PASS.**

## T3 — Verdict sanity (workload exercises real branches)
The script asserts each of the 6 cases returns its expected allowed/blocked verdict before
timing; a mismatch exits 2 with `WORKLOAD MISMATCH`. The full run exited 0 and produced timings
→ all 6 verdicts matched (allow ×2, Layer-1 block ×2, Layer-2 block ×2). **PASS.**

## T4 — Smoke run (small iters, isolated JSON to /tmp)
```
$ python3 experiments/ralph_outputs/C10/artifacts/bench_is_safe.py --iters 5000 --warmup 500 --json /tmp/c10_smoke.json
...
projected per 10-action plan: 2.85us
wrote /tmp/c10_smoke.json
RC=0
```
**PASS** (exit 0; isolated so it does not overwrite the committed full-run JSON).

## T5 — Full run (default 200k iters) — the committed artifact
```
$ python3 experiments/ralph_outputs/C10/artifacts/bench_is_safe.py | tee experiments/ralph_outputs/C10/artifacts/run.log
python 3.13.7  iters=200000  cases=6
is_safe : mean=0.2704us  p50=0.2500us  p99=0.4160us
no-op   : mean=0.0528us  p50=0.0420us  p99=0.0840us
overhead: mean=0.2176us  p99=0.3320us  ratio=5.12x
projected per 10-action plan: 2.70us
wrote .../bench_results.json
```
**PASS.** `bench_results.json` written with full distribution (see 06).

## Notes / observations
- `is_safe` mean ≈ **0.27 µs**; no-op ≈ **0.05 µs**; overhead ≈ **0.22 µs** (5.1×).
- `is_safe` `max_us` = 80.25 µs (single sample) and no-op `max` = 6.1 µs — these are scheduler
  preemption outliers, not function behavior; they do not affect p50/p99 (sub-0.5 µs). This is the
  apparatus-bound tail flagged in 05.
- Numbers are host-specific; the **5× ratio** and **sub-µs absolute** are the stable conclusions.

## Fixes applied during testing
None — script ran correctly on first execution (syntax-checked before running).
