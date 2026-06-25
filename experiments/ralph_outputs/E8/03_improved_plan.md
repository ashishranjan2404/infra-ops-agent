# E8 — 03 Improved Plan

## What changed after the grill

**Accepted:**
- (PSRE/AAAI) The deliverable is **harness + power-analysis N + honest blocker**, not a
  scaling curve. Removed any path that emits a curve from real data we don't have.
- (AAAI) **Hard anti-fabrication gates**: `fit_learning_curve` returns `None` on <4 real
  points; `run_sweep` with no fit callback sets `blocked:true` and leaves every `score`
  None. Added explicit tests for both.
- (RLE) **Stratified + nested** subsetting preserving family×difficulty; nesting via stable
  per-record hash prefixes so subset(N1) ⊂ subset(N2). Added a nesting test (>0.8 overlap)
  and a strata-preservation test (<0.05 deviation).
- (RLE/DVO) **Degrade, don't abort**: cap N at corpus size; still write manifests + power
  analysis; expose `requested_N` AND `actual_N` everywhere so a capped run is unmistakable.
- (SMR/PSRE) **Report coverage with volume**: profile emits per-family and per-difficulty
  counts, answering the coverage question alongside the volume question.
- (SMR) Power analysis over a **δ grid** with observed reward sd ≈ 0.22, giving a
  quantitative "N needed" anchor independent of the (blocked) curve.

**Rejected (with reason):**
- SMR's "the curve is the answer / fit it now": rejected — fitting a 5-point log-spaced
  curve when only 319 real records exist would be fabrication (PSRE/AAAI). The fitter
  exists and is tested, but is only ever fed *real* points from a *real* fit callback.
- DVO's "fail loudly / abort if data missing": rejected in favor of RLE's degrade — a
  capped run with manifests is more useful and still honest, as long as the cap is visible.
- PSRE's "this is only coverage, drop the volume sweep": rejected — kept the volume sweep
  (data-efficiency per stratum is a real scaling question) but *added* the coverage report
  so both views ship.

## Final design (unchanged core, hardened edges)
Reader → stratified/nested subsetter → power analysis → sweep driver (BLOCKED unless a real
fit callback is injected) → curve fitter (gated ≥4 real points). Validated on a 2k synthetic
fixture (no score field) + run against the real 319-record corpus to demonstrate the cap.

## Updated success criteria
Adds: capped run shows actual_N<requested_N on real corpus; `blocked:true` with no scores;
fitter refuses <4 points; coverage in profile; all in tests.
