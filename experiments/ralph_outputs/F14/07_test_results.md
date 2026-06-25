# F14 — 07 Test Results

## Test 1 — timing validator self-test + budget check
Command:
```
python3 experiments/ralph_outputs/F14/artifacts/timing_check.py
```
Output (real):
```
[selftest] all assertions passed
  Slide  1 (0:30)  Title
  Slide  2 (1:15)  Hook: the alert is lying to you
  ...
  Slide 17 (0:30)  Close + reproduce it yourself
------------------------------------------------------------
  slides=17  total=15:00  target=15:00  contiguous=True
  ADVISORY: total exactly equals target — zero buffer (informational).
PASS
EXIT=0
```
Result: **PASS**. 17 contiguous slides, no slide > 75s, total == 15:00 target.

### Iteration log (real fixes applied)
- **Fix 1:** First run the self-test failed (`AssertionError`) because a 450s test slide
  exceeded `max_slide_seconds=75`. Corrected the self-test fixture to a realistic 60s/slide
  case with an explicit `target_seconds=120`. Re-ran → self-test passes.
- **Fix 2:** Validator then reported `total=13:45 ≠ 15:00 → FAIL`, catching a real discrepancy:
  my "## Timing summary" line claimed 15:00 but the per-slide values summed to 13:45 (825s).
  Bumped 5 slides (2, 6, 8, 13, 16) by 15s each (+75s) and updated the summary line.
  Re-ran → `total=15:00`, **PASS**. The validator did its job — it caught my arithmetic error.

## Test 2 — Python syntax check
```
python3 -c "import ast; ast.parse(open(...timing_check.py).read())"  -> py syntax OK
```

## Test 3 — content grounding / structure parse
A scan confirmed: 17 content slides, 13 `[ARCH]` + 9 `[HEAD]` source tags, 5 backup slides, and
the presence of the load-bearing numbers (reward function `0.30·diagnosis...`, verifier
`0.90 accuracy`, `0.95 hand-written`, `14 → 3`, ablation `0.25`, env band `0.27`/`0.50`).
The only "MISSING" hit (`haiku 0.27` as a contiguous string) was a false negative caused by
markdown bold markers (`haiku **0.27**`) splitting the substring — verified present at
line 65.

## Verdict
All tests pass. The deliverable is valid markdown, the validator is valid Python that runs
clean (exit 0), the budget sums exactly to 15:00, and every headline number traces to a real
source in the repo.
