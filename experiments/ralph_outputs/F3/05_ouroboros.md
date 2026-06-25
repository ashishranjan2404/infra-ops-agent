# F3 — Ouroboros (self-critique as 3 engineers in sequence)

## Engineer 1 — "the provenance is a lie detector that doesn't detect"
**Problem found.** The validator's provenance check greps the *value string* in the source
file. But ARCHITECTURE.md renders numbers like `0.86` and `+0.23` in a markdown table — a
value like `0.23` will trivially appear *somewhere*, even on the wrong row. So the check
verifies "this number exists in this file," not "this claim is sourced." That's weak. **Also**:
the ceiling identity `(4×1.0 + 0.30)/5` — the `×` is a Unicode multiplication sign; if I write
`(4*1.0...` in the TSV it won't match the doc's `(4×1.0`. Token mismatch will false-fail.

**Fix accepted.** (a) Accept that the check is a *presence/consistency* check, not a semantic
linker, and say so honestly in the validator docstring + step 08 — it catches drift (a number
changed in the doc but not the Conclusion), which is its real job. (b) For provenance `value`
strings, copy the EXACT substring from the source doc (verify with grep before finalizing),
including Unicode `×`/`−`, so matches are exact.

## Engineer 2 — "the structure regex is too brittle / too loose"
**Problem found.** Spec requires headings "in order." If I phrase the mechanisms heading as
`## What makes graduation real` the regex `^##\s+What .*graduation .*real` matches — fine. But
the certifies heading `^##\s+What .*certif` and the mechanisms heading both start with
`## What ` — if order matching is naive (find each regex's first index, assert increasing),
two `## What...` headings could cross-match and pass even if misordered, OR the certifies regex
could match the mechanisms heading first. Ambiguity = false pass.

**Fix accepted.** Make the regexes disjoint: mechanisms heading must contain `real`, certifies
heading must contain `certif` and NOT `real`. Implement order check by finding the match
position of each regex *after* the previous match's end offset (sequential scan), not global
first-index. This removes the cross-match ambiguity.

## Engineer 3 — "is the deliverable over-engineered for an authoring task?"
**Problem found.** The task is "write a Conclusion." Three artifacts + a validator is a lot of
scaffolding around one prose document. Risk: the validator becomes the deliverable and the
prose gets thin. Also: a 700-word floor could push toward padding — a Conclusion that's too
long is a Conclusion nobody reads. And the "does NOT certify" honesty could be reduced to a
single token (`not automated`) to satisfy the checker while the actual paragraph stays vague.

**Fix accepted.** (a) Treat `CONCLUSION.md` as THE deliverable; validator + TSV are
lightweight guards (≤ ~120 lines total), explicitly secondary. (b) Target ~750–950 words —
enough to be substantive, short enough to be a real Conclusion, not a second paper. (c) Write
the limitations subsection as a genuine, specific paragraph (n=5×5, LLM judge, demotion not
automated, sim-vs-prod gap) — the token check is a floor, the prose must exceed it. (d) Keep
the word floor at 700 but aim higher; quality over the bar.

## Final filtered spec (deltas applied)
- Provenance `value` strings = EXACT substrings copied from source docs (Unicode-faithful);
  validator documented as a *drift/consistency* check, not a semantic linker.
- Structure regexes made disjoint (`real` vs `certif`, latter excludes `real`); order checked
  by sequential post-offset scan.
- `CONCLUSION.md` is primary; validator/TSV are thin guards. Target ~750–950 words.
- Limitations subsection must be a real specific paragraph, not a token-satisfying stub.
