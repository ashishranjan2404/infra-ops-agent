# 07 — Test Results

## Commands run

### 1. pytest on the reference implementation
```
$ cd experiments/ralph_outputs/I1/artifacts && python3 -m pytest test_graduation.py -v
collected 25 items
... (all 25 PASSED) ...
============================== 25 passed in 0.01s ==============================
```
**Result: 25/25 PASS.** No fixes were needed; the impl matched the spec on first run.

Coverage of the formalization:
- Wilson LB: zero-n, below-point-estimate, monotone-in-k, tightens-with-n — all pass.
- `clean_win` / `correct_escalation` truth tables (incl. the tricky "solvable+escalated is
  NOT a correct escalation" and "unsolvable+resolved is NOT correct escalation") — pass.
- Tier map grounded in real tools (`restart_service`→T1, `scale_deployment`→T2,
  `escalate_to_human`→T0, unknown→T3) — pass.
- Graduation conjunction: passes a clean batch; blocked below n_min; blocked by ONE unblocked
  trap (hard-zero gate); blocked when escalation untested (|UNSOLV|=0) — pass.
- `earned_autonomy` monotonicity + `grant` highest-contiguous-tier — pass.
- Revocation: instant on unblocked trap; fast on cw-floor breach; no-op on healthy window;
  no-op at T0 — pass.
- `outcome_from_loop_result` adapter on a real `refine_loop`-shaped dict (clean win +
  escalated-unsolvable) — pass.
- **Worked-example regression** (the load-bearing honesty check): live n=5 perfect vector →
  `grant == T0` (provisional); same quality scaled to n_min → `grant == T1` — pass.

### 2. Import smoke test
```
$ python3 -c "import graduation; print('tiers', list(graduation.TIERS))"
import OK; tiers [0, 1, 2, 3]
```

### 3. Markdown parse / size check (all step files + the formalization)
```
graduation_framework.md ok 11235 chars
01_plan.md ok 4929 ; 02_grill.md ok 5947 ; 03_improved_plan.md ok 2929
04_spec.md ok 6047 ; 05_ouroboros.md ok 4424
```
All files non-empty and readable.

## Fixes applied
None required — the reference implementation passed all 25 assertions on the first run, and
all documents parse. (The one design subtlety I pre-empted in the spec — that a perfect n=5
vector must NOT graduate — is exactly what `test_worked_example_live_sweep_is_provisional_only`
asserts, and it passed, confirming the framework refuses to over-claim from the headline 0.86.)

## Honest note on what was NOT run
I did not run the live REx sweep / `rex.frontier` (that needs `HUD_API_KEY` + model providers
+ minutes of API calls and is a *core* run, not part of this formal deliverable). Instead the
worked examples reuse the *already-published* ARCHITECTURE.md numbers and the framework's own
unit tests prove the per-incident accounting is internally consistent. This is a formalization
task; the deliverable is the predicates + a runnable reference impl, which are fully validated.
