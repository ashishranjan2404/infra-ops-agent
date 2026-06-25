# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Statistician (finds real problems)
- **P1**: Krippendorff alpha with 12 units and 5 raters has a huge confidence interval; a point
  estimate is borderline meaningless. → *Fix*: ship the metric but force `interpretation`
  labels and document N as underpowered; recommend bootstrap CI as a future add (noted, not
  blocking — would need numpy).
- **P2**: My ordinal-delta coincidence-matrix implementation is the part most likely to be
  subtly wrong. → *Fix*: add a degenerate sanity test (all-identical → alpha=1.0) and a
  monotonicity check (synthetic data with known structure yields alpha in a plausible band).
  Both run in 07. (T5 = 1.0 ✓; self-test alpha 0.63–0.74, plausible for noisy ordinal ✓.)
- **P3**: Validity correlation on 12 points with stratified (non-random) sampling can be
  inflated. → *Fix*: report Spearman AND Pearson, label as exploratory, N=12.

## Engineer B — Practitioner SRE (finds real problems)
- **P4**: "Safety 5 = safe remediation" is unfair to diagnoses that *intentionally* don't
  propose a fix (RCA-only). A rater might score them 1. → *Fix*: rubric explicitly states "or
  correctly defers/recommends investigation" counts as safe; add to anchor text.
- **P5**: Raters will anchor on diagnosis *length*; verbose wrong answers look authoritative.
  → *Fix*: protocol instruction "rate the claim, not the prose; length is not quality."
- **P6**: `ground_truth_category` is in the item shown to raters — that leaks the answer and
  destroys correctness ratings. → *Fix (CRITICAL)*: move ground-truth reveal to AFTER rating;
  protocol says raters first rate blind, then may view ground truth for the free-text rationale.
  (Item JSON keeps the field for the analyst, but the rendered rater view must hide it —
  documented in protocol; the CSV workflow never displays it.)

## Engineer C — Reproducibility/tooling (finds real problems)
- **P7**: Script defaults `--key` to a path relative to the script file; if run from elsewhere
  it could miss. → *Fix*: `_default_key()` resolves via `os.path.dirname(__file__)` (absolute).
  ✓ implemented.
- **P8**: No schema validation on rating CSV — a typo header silently yields empty results.
  → *Partial fix*: `_to_int` tolerates blanks; empty match prints a clear stderr message.
  Full JSON-schema validation deferred (stdlib-only constraint), documented in 09.
- **P9**: Example CSVs are synthetic but live next to real artifacts — risk of someone treating
  them as real human data. → *Fix*: they live in `ratings_example/` and the output `_mode`
  marks synthetic provenance; SUMMARY flags they are illustrative only.

## Final filtered spec changes (applied)
1. Ground-truth category is **hidden from the rater view**; revealed only post-rating
   (protocol step). The field stays in JSON for the analyst. *(addresses P6 — critical)*
2. Safety anchor amended: "safe, reversible, correctly scoped — *or correctly defers*". *(P4)*
3. Protocol instruction: "rate the claim, not the prose." *(P5)*
4. `ratings_example/` clearly labeled synthetic; `_mode` provenance in output. *(P9)*
5. N=12 underpowered + bootstrap-CI-as-future documented; alpha sanity tests in 07. *(P1,P2)*
6. Deferred (documented, not silently dropped): bootstrap CIs, JSON-schema CSV validation. *(P3,P8)*
