# I3 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Numerical methods reviewer
**Problems found:**
1. The original `_dip_statistic_fallback` is mathematically wrong for non-uniform
   unimodal data (Gaussian D≈0.16). Shipping it as the engine would have produced
   a false "everything bimodal" result. → FIX: demote to a labelled fallback;
   make `diptest` the primary engine; the run uses the package (verified
   `_HAVE_PKG=True` in run.log).
2. `boot_pval=False` returns the analytic-table p, which is deterministic but is an
   *interpolation* and can read exactly `0.0` for very large D. → Reported as
   p<1e-4 in prose; the raw 0.0 is kept in JSON honestly, not rounded up.

## Engineer B — Statistics / experimental-design reviewer
**Problems found:**
1. Pooling conditions mixes populations with different means; a naive reader could
   over-claim "the reward signal is bimodal." → FIX: pooled rows are kept but
   explicitly labelled `ALL_CONDITIONS_pooled` and interpreted in 08/09 as a
   mixture, not within-policy structure.
2. rex/runs n=12 is too small for a confident dip conclusion. → FIX: kept but
   flagged small-n in 08/09; not used as a headline.
3. Multiple comparisons (13 tests). → Even Bonferroni at 0.05/13≈0.0038 leaves
   every weak-policy p (all <1e-4) significant, so the conclusion is robust; noted
   in 09.

## Engineer C — Software / reproducibility reviewer
**Problems found:**
1. `pip`/`python3` mismatch: a first `pip install diptest` landed in a different
   interpreter (`ModuleNotFoundError`). → FIX: installed via `python3 -m pip`;
   verified import under the exact interpreter that runs the analysis.
2. matplotlib may be absent in some envs. → `make_figure.py` is a separate optional
   artifact; the core analysis (dip_results.json) does not import it, so the
   numeric result never depends on plotting.
3. Hard-coded relative repo path. → resolved via `os.path.join(HERE, '..'*4)` and
   absolute paths; runner is location-independent.

## Final filtered spec deltas
- Primary engine = `diptest` package; numpy fallback labelled and untrusted.
- Gaussian sanity gate is a hard test (blocks trust if it fails).
- Pooled + rex/runs reported but flagged; per-condition is the headline.
- Figure decoupled from the numeric pipeline.
