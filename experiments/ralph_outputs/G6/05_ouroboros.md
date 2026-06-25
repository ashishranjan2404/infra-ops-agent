# G6 — 05 Ouroboros (self-critique, 3 engineers)

## Engineer 1 — finds: citation integrity is the whole value
**Problem:** If `claims_table.csv` references a `source_id` that doesn't exist in `sources.json`, the entire "be sourced" mandate is silently broken. A markdown doc *looks* cited but could be fabricated. **Fix:** `validate.py` must HARD-fail (nonzero exit) on any dangling `source_id`, and assert T5 (every claimed repo file path actually exists). A claims analysis whose citations don't resolve is worse than useless.

**Problem:** Quant claims drift between blog versions (90% faster vs 95% MTTR vs 2x/3–4min). Attributing the wrong number to the wrong post is a real accuracy bug. **Fix:** each quant row's `source_id` must point to the *specific* post that made that number; keep the "deeper-reasoning" post (S?) distinct from the launch post.

## Engineer 2 — finds: fairness drift / straw-man risk
**Problem:** The line between "not disclosed" and "cannot do" is exactly where this analysis becomes propaganda if sloppy. "Bits has no false-positive rate" must be typed `not_disclosed`, never `acknowledged_limit`. **Fix:** add a `type` taxonomy enforced by validate (must be in the allowed set), and a written rule in the analysis: *absence of evidence is labeled as absence of evidence.*

**Problem:** Over-claiming for us. If a differentiator cites `rex/scoring.py` but the reward weights I quote don't match the file, that's a credibility own-goal. **Fix:** quote the reward weights verbatim from the file (`W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60`) and the escalation behavior from `rex/loop.py:142-146` / `rex/escalate.py`. T5 checks the files exist; I additionally pin the exact constants.

## Engineer 3 — finds: scope & over-engineering
**Problem:** Building a JSON+CSV+validator is borderline over-engineered for a 1-doc analysis. Justify it or cut it. **Verdict:** keep — the brief demands "REAL, validated artifacts," and a passing validator is the cheapest proof the citations resolve. It directly buys the success criterion. Not over-engineered; it's the test.

**Problem (under-engineering):** The analysis risks being a generic "vendor vs us" piece that could apply to any competitor. **Fix:** force every differentiator to name the *specific incident class* (loudest-alert-points-at-victim cascade) and the *specific mechanism* (mechanism-level judge, trap penalty, escalation on `singleton_node_notready`). Generic = rejected.

**Problem:** No empirical head-to-head (we can't run Bits). A reviewer will note we compare *their claims* to *our mechanisms*. **Fix:** state this limitation explicitly in `09_critique.md` and in the analysis verdict — it's a claims/design analysis, scoped as such, not a measured benchmark.

## Final filtered spec (delta over 04)
- validate.py: HARD-fail on dangling source_id + enforce `type` enum + assert required repo files exist.
- analysis.md: quote reward constants verbatim; label not-disclosed vs acknowledged explicitly; name the incident class per differentiator; include the "we did not run Bits" caveat in the verdict.
- claims CSV: quant rows pinned to the specific source post.
