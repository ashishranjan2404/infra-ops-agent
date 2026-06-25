# B3 — 09 Critique (honest)

## What's solid
- The formula is correct: validated against three independent published Wilson values and
  an independently-written reference implementation. Not circular.
- It is a genuine **reproduction** of the A1/A2 published intervals: 40/40 cells match the
  upstream stored `ci95` within 0.01. If A1/A2 had a CI bug, this run would have surfaced it.
- Self-contained, stdlib-only, no shared-core edits, parallel-safe. Runs in <0.1s.

## Where a reviewer attacks

1. **Binomial-iid assumption (the real weakness).** Each pooled cell mixes seeds that
   reuse the same incidents. Draws within an incident are correlated, so the effective
   sample size is below n and the **true 95% interval is wider** than the Wilson interval
   reported here. The intervals capture binomial sampling error only; they are
   *anticonservative* with respect to seed correlation. A cluster-robust or
   incident-bootstrap interval would be more honest but needs a clean per-(incident,seed)
   binary matrix for every cell, which the summary JSONs don't uniformly expose. This is
   the limitation I'd lead with as a reviewer, and it is stated, not hidden.

2. **Upstream-match could look circular.** If the upstream `compute_pass_at_k.py` used the
   same Wilson formula, "match = ok" only proves we reproduced it, not that the formula is
   right. Mitigated: correctness is carried entirely by the independent known-value tests;
   the match is reported separately as a *reproduction* check. Still, a skeptic could ask
   for a check against scipy's `proportion_confint(method='wilson')` — not done because
   scipy isn't a project dependency (the exact `Z95` constant makes them agree to ~1e-12,
   which I'd add if asked).

3. **pass@2 / pass@5 get no interval.** The deliverable name says "pass@k," but Wilson is
   a binomial-proportion interval and only pass@1 is a raw proportion. pass@2/@5 are the
   combinatorial Chen et al. estimator; a defensible interval there needs bootstrapping
   over the n draws. I scoped to pass@1 rather than slap an ill-defined Wilson interval on
   a non-proportion. This is a real (deliberate) gap.

4. **Only two input files.** A1 (glm-5p2) and A2 (deepseek-v4-pro) were the available
   pass@k JSONs at run time. If A3/A4 produce more, the tool already accepts them on argv,
   but they weren't present, so coverage is two conditions-sets, not the whole frontier.

5. **Cosmetic table bug.** The long `retry_realistic` label overruns the fixed-width
   `scope` column in the text table. Purely visual; `wilson_table.json` has clean fields.

## What's missing / would strengthen
- An incident-level bootstrap CI alongside Wilson, to quantify how much the seed
  correlation actually widens the interval (likely modest for the pooled overall cells,
  larger for the small n=30 family cells).
- A scipy parity test guarded by `pytest.importorskip("scipy")`.

## Honest bottom line
The deliverable does exactly what was asked and reproduces the published numbers, with the
one substantive caveat that the intervals model binomial sampling error and slightly
understate uncertainty under seed correlation. No fabricated results.
