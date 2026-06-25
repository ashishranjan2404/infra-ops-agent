# 08 — Verification

## Success criteria (from 01) vs outcome
| Criterion | Met? | Evidence |
|-----------|------|----------|
| Script runs for real | ✅ | T4 smoke + T5 full run, both exit 0 (07) |
| Reports mean/p50/p99 for is_safe | ✅ | `is_safe`: 0.2704 / 0.2500 / 0.4160 µs (bench_results.json) |
| Reports mean/p50/p99 for no-op baseline | ✅ | `noop`: 0.0528 / 0.0420 / 0.0840 µs |
| Overhead vs no-op quantified (delta + ratio) | ✅ | +0.2176 µs mean, **5.12×** |
| Grounded in rex/harness.py is_safe | ✅ | imports the real `is_safe`; workload covers its Layer-1/2 branches |
| Defensible "meaningful overhead?" verdict | ✅ | see below |
| No shared-core edits | ✅ | only read rex/harness.py; all writes under C10/ (+ /tmp smoke) |

## Are outputs real (not placeholder)?
Yes. `bench_results.json` and `run.log` are captured from an actual 200k-iteration execution
on Python 3.13.7. The verdict-sanity gate (exit 2 on mismatch) proves the timed calls hit the
real `is_safe` branches, not a stub.

## Verdict: does is_safe add MEANINGFUL overhead?
**No — not meaningfully.** Per call, `is_safe` costs ~**0.27 µs**, of which ~**0.22 µs** is its
own logic over the no-op floor (5.1×). Projected over a full 10-action plan that is ~**2.7 µs**
total. The function it sits beside in `run_plan` — a sim tick (`world.run`) and, upstream, an
LLM plan generation — costs on the order of **milliseconds to seconds**, i.e. **10^4–10^7×**
larger. `is_safe` is therefore in the noise of harness inference latency.

Caveat (honest): the 5.1× *ratio over a no-op* is real but only matters relative to a vanishingly
small base; the absolute cost is what governs "meaningful," and it is sub-µs. The benchmark also
fixes `forbidden_categories` at a small list — if that list ever grew large the `in` test could
go linear; this benchmark does not cover that scaling regime (named in 05/09).

## Independent re-derivation
`overhead_ratio_mean = 0.270420 / 0.052813 = 5.120` ✓ matches reported 5.12×.
`projected_cost_per_10action_plan_us = 0.270420 * 10 = 2.704` ✓.
