# B3 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — Numerical / stats engineer

**Problems found:**
- A1. Hardcoding `z = 1.96` would make 50/100 come out [0.4038...] but diff from scipy's
  exact quantile in later decimals. → FIX: use `Z95 = 1.959963984540054`.
- A2. `wilson_ci(0, 0)` divides by zero in `p = passes/n`. → FIX: early-return (0.0, 1.0)
  before computing p.
- A3. Clamping `max(0, lo)` is correct, but then `half_width = (hi-lo)/2` is no longer
  the true score half-width after clamping (at the boundary). → ACCEPT as reported: it's
  the *displayed* interval half-width, which is what a reader wants; documented as such.
- A4. The unit test must validate against values NOT produced by the same code, or it's
  circular. → FIX: `_ref_wilson` is written independently + literal textbook constants
  (0.4038, 0.2775, 0.7225) hardcoded.

## Engineer B — Data-plumbing engineer

**Problems found:**
- B1. If a future input lacks `by_condition`, `iter_cells` would yield nothing silently.
  → ACCEPT (defensive `.get` returns {}), and `build_rows` prints a WARN on a file that
  fails to parse at all. Empty-but-valid files just contribute 0 rows — acceptable.
- B2. `stored_ci95` may be absent on some cell → the `match?` column must handle None.
  → FIX: `format_table` only computes match when `stored_ci95` is truthy.
- B3. Auto-discovery hardcodes two paths; if A1/A2 dirs are renamed the tool prints "No
  inputs." → ACCEPT: argv override exists; discovery is a convenience, exit code 2 is
  explicit, not a silent empty table.
- B4. Float formatting: pass@1 like 0.0667 should not display as 0.07 then claim "match
  ok" off a rounding artifact. → checked: comparison uses the rounded values to 4 dp and
  a 0.01 tolerance; rounding to 3dp for *display* only. Fine.

## Engineer C — Reviewer / scientific-integrity engineer

**Problems found:**
- C1. Biggest risk: presenting binomial Wilson as if it captures ALL uncertainty. Seeds
  reuse incidents → correlated draws → real interval is wider. → FIX: stated explicitly
  in spec + critique; not hidden. This is the honest framing REV demanded.
- C2. Cross-checking against upstream `ci95` is circular IF upstream used the same
  formula — a "match" then only proves we copied it, not that it's correct. → RESOLVED:
  correctness is established by the INDEPENDENT known-value tests (50/100 etc.); the
  upstream match is a *reproduction* check (did we read the right n/passes and apply the
  right family), reported separately. Both claims are made distinctly.
- C3. pass@2 / pass@5 in the source JSON get NO interval here. → ACCEPT + document: the
  task says "Wilson CIs for pass@k numbers"; Wilson is a *binomial-proportion* interval
  and applies cleanly to pass@1 (a proportion of independent-ish episodes). pass@2/@5 are
  the Chen et al. *combinatorial estimator*, not a raw proportion — a Wilson interval on
  them is not well-defined without bootstrapping. Scoped to pass@1; noted in critique.

## Final filtered spec (deltas applied)
- exact Z95 constant; n==0 guard; independent reference + literal known values in tests;
  None-safe `match?`; WARN on unparseable file; explicit exit 2 when no inputs.
- Honesty notes carried into 09: (i) binomial model is anticonservative under seed
  correlation; (ii) upstream-match is a reproduction check, not the correctness proof;
  (iii) interval scoped to pass@1, not the combinatorial pass@2/@5.
