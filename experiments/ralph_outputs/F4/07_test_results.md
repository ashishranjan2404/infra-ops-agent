# F4 — 07_test_results

All four spec tests run; results below are real captured output.

## T1 — generator runs clean
```
$ python3 experiments/ralph_outputs/F4/artifacts/make_figures.py
REPO=/Users/mei/rl
OUT =/Users/mei/rl/experiments/ralph_outputs/F4/artifacts/figures
  fig -> .../fig1_passk_ci.png
  fig -> .../fig2_passk_by_family.png
  fig -> .../fig3_passk_curve.png
  fig -> .../fig4_mcnemar.png
  fig -> .../fig5_frontier.png
  fig -> .../fig6_harness.png
done.
exit 0 OK
```
**PASS** — exit 0, six `fig ->` lines. (Full log: `artifacts/run.log`.)

## T2 — PNG validity + size (PIL verify)
```
fig1_passk_ci.png                78806B PNG  OK
fig2_passk_by_family.png         59861B PNG  OK
fig3_passk_curve.png             99310B PNG  OK
fig4_mcnemar.png                 67702B PNG  OK
fig5_frontier.png                92271B PNG  OK
fig6_harness.png                 94021B PNG  OK
```
**PASS** — all 6 valid PNGs (PIL `verify()` clean), all > 10 KB, all 200 DPI (1343–1863 px wide).

## T3 — numbers trace to real JSON
```
all spot-checks PASS
```
Asserted: A1 `rex.overall.p1`==0.8968 (fig1 "0.90"), A1 `rex.novel.p1`==1.0;
A2 McNemar vs-zero-shot a_pass=99 / a_fail=1 (fig4); every frontier `rex_mean`==0.86 (fig5);
harness synthesized accuracy=0.897, false_allow=0.308 (fig6). **PASS.**

## T4 — no shared-file leak
`git status` lists pre-existing dirty files (`rex/*.py`, `sim/*.py`, `agent/*.py`,
`rex/eval_pass_at_k.py`, …) — these were **already** modified/untracked in the session-start
git snapshot, not by me. Confirmed with:
```
$ find rex sim agent experiments -name '*.py' -newermt '30 minutes ago' | grep -v ralph_outputs/F4
(no output)
```
No shared `.py` file was modified during this session. All new files live under
`experiments/ralph_outputs/F4/`. **PASS.**

## Fixes applied during dev
- Reworked `fig6_harness_generalization` after inspecting `heldout_table` — it is a
  `{policy: metrics}` dict, not a per-incident list. Without the fix fig6 would have been blank.
- Switched fig1 error bars from any normal-approx to the stored asymmetric Wilson interval.
