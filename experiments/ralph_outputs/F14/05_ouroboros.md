# F14 — 05 Ouroboros (3 self-critiques in sequence)

## Engineer A — "the parser is brittle"
**Problem found:** The spec's regex contract `### Slide N — T (M:SS)` uses an em-dash (—). If
the outline ever uses a hyphen-minus or en-dash, the parser silently returns nothing and the
validator reports a *passing* empty run (0 slides, total 0 ≠ 900 → actually fails, good — but
the failure mode is confusing). Also `M:SS` with `SS >= 60` (e.g. `0:90`) would be accepted as
90s but is malformed.
**Fix:** Parser tolerates em-dash, en-dash, and hyphen as the title separator; reject `SS>=60`
with an explicit error. Add a self-test for the malformed `0:90` case and the empty-doc case
(must report `n_slides==0, ok False`).

## Engineer B — "the content over-trusts two sources that disagree"
**Problem found:** `ARCHITECTURE.md` says "REx lifts every frontier model … all converge to
0.86" while `headline_insights.md` says REx's lift is mostly oracle leakage (0.25 ≈ 0.24). A
naive outline that cites both as positive results is internally contradictory and a reviewer
will catch it instantly.
**Fix (already in the outline, verify):** Slide 9 introduces REx neutrally; Slide 12 is the
ablation that *reconciles* the two — the 0.86 table is explicitly demoted to backup B2 "with
the ablation caveat." Confirm the outline never presents 0.86 as a standalone headline. ✔
present (REx framed as loop on slide 9, lift adjudicated on slide 12, 0.86 only in B2).

## Engineer C — "timing is too tight / under-tested"
**Problem found:** 17 slides in exactly 15:00 leaves zero buffer; real talks overrun on the
result slides. Three slides at 1:15 back-to-back (7, 10, 12) is a fatigue risk. Also the
validator only checks the *sum*; it doesn't warn that exactly-15:00 with no buffer is
operationally risky.
**Fix:** Keep the budget at 15:00 (the ask is a 15-min talk; a 13:30 "real" target with 1:30
Q&A buffer is documented in 01_plan and noted on slide 17). Add to `timing_check.py` a soft
advisory when total == target exactly with no slack (informational, does not fail). Spread the
three 1:15 slides so they're not adjacent — current order is 7, 10, 12 (separated by ≥2 slides
each), acceptable. No reorder needed; add the advisory only.

## Final filtered spec (deltas applied)
1. Parser accepts em-dash / en-dash / hyphen separators.
2. Parser rejects `SS >= 60` as malformed (explicit error, ok False).
3. Empty-doc → `n_slides==0, ok False`, with a self-test.
4. Validator emits a non-failing advisory when total exactly equals target (no slack).
5. Outline confirmed self-consistent: REx lift adjudicated by the ablation slide; 0.86 lives
   only in backup B2. No content change required beyond verification.
