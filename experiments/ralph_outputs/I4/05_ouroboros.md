# I4 — Ouroboros (3 engineers critique my own spec)

## Engineer α — "the in-scope split smuggles the result"
**Problem found.** The spec defines `in_scope = Φ-expressible positives ∪ ALL negatives`.
By dumping every negative into the in-scope set, I dilute the residual and inflate the
"fraction of `H(y)` removed". The 35 topology-trap *positives* are excluded, but their many
*neutral negative* siblings stay in — biasing `H(y)` and the coverage denominator.
**Severity:** real. **Fix:** keep the split, but report `n`, `positives`, AND
`out-of-scope positives` explicitly so the reader sees the denominator. The witness already
prints `in-scope (Φ region) n=545 positives=218` and `out-of-scope positives=35`. The claim
is scoped to "the Φ region", and the excluded mass is named — not hidden. Accept with the
honesty caveat made loud in the doc's scope section.

## Engineer β — "the full-vector MI bound is loose, not the true sup over R4"
**Problem found.** `I(y;R4|R123) ≤ H(y|R123) − H(y|full_Φ)` is an *upper* bound. The doc could
be read as "a 4th rule gains exactly 0.034 bits". It does not — 0.034 is the *most* any
Φ-rule could gain, achieved only by the full-vector partition (which is not a single human
rule). A single realizable R4 likely gains less.
**Severity:** medium (overclaim risk). **Fix:** the doc states it as "≤ 0.0344 bits — the
*ceiling* on what any 4th Φ-rule can recover", and notes the achiever is the degenerate
full-vector partition. The argument only needs the ceiling to be small. Accept.

## Engineer γ — "entropy treats both error directions equally; an SRE cares about false-allows"
**Problem found.** Two rule-sets with identical `H(y|R123)` can differ catastrophically:
one leaks dangerous false-allows, the other only over-blocks. Shannon entropy can't see it.
The spec's coverage metric helps but coverage(positives) alone ignores false-blocks.
**Severity:** real but *out of scope for the IT claim*. **Fix:** the doc explicitly says the
IT decomposition answers "do the 3 rules carry the label's information" and the *coverage of
should-block mass* answers "do they catch the dangerous events (false-allow side)". The
false-block side is C12's accuracy witness territory (99.6%); I cite it rather than recompute.
Accept the scoping; do not pretend entropy is a safety metric.

## Filtered final spec (deltas applied)
1. Witness prints the full denominator breakdown (n, positives, oos positives) — DONE.
2. `I(y;R4|R123)` framed as a **ceiling** on any Φ-rule's gain, achiever named — reflect in doc.
3. IT claim explicitly scoped: entropy = "information carried"; coverage = "dangerous events
   caught"; false-blocks deferred to C12's accuracy witness. — reflect in doc §scope.
4. No change to the rule-schemas or the computation (they passed T1–T6). The fixes are
   *framing/honesty*, which is exactly where an IT argument is most often abused.
