# F3 — Critique (honest)

## What's weak
1. **The deliverable is prose.** A Conclusion is rhetoric over machinery; it adds no new
   capability. Its worth is entirely (a) whether the framing is *correct* (it maps to real
   mechanisms) and (b) whether the cited numbers are *honest* (they are, and pinned). A
   skeptic can fairly say "this is writing, not engineering" — true, but the task asked for
   exactly this, and the validator+provenance discipline is the engineering rigor applied to
   writing.
2. **The metaphor still does some load-bearing work the code only partly supports.** The
   honest soft spot is *revocation*: graduation implies a credential that can be pulled, but
   the demotion `autonomous → approval` is **designed and partially exercised, not yet an
   automated closed loop.** I state this aloud in the Conclusion, but a hostile reviewer will
   still say the metaphor's most distinctive feature (revocability) is the least implemented.
   That's a fair hit; mitigated only by honesty, not by code.
3. **The provenance check is shallow.** It confirms a value string *exists* in a file, not that
   it sits on the semantically-correct line in the right context. A number that legitimately
   recurs (e.g. `0.86`) would pass even if mis-attributed. Documented as a drift detector, not
   a linker — but it is weaker than a reader might assume from the word "provenance."
4. **n is small and the judge is an LLM.** The evidence the Conclusion leans on is 5 incidents
   × 5 models plus a 15+5 curriculum, with diagnosis graded by an LLM-judge. I scope the claims
   to *shape/direction/within-group signal*, not population effect size — but the numbers are
   not from a large, independently-replicated study.

## What a reviewer attacks first
- *"0.86 across all five models is suspiciously clean — is the ceiling an artifact of the
   reward construction rather than a finding?"* The Conclusion pre-empts this by arguing
   0.86 = `(4×1.0 + 0.30)/5` is *exactly* solve-4 + escalate-1, i.e. the result is the reward
   doing its job, not saturation. But a determined reviewer can still press on whether the
   five-incident suite is too small for "converge" to mean much.
- *"You renamed 'it passed an eval' to 'it graduated' — what's actually new?"* The defense is
   the four mechanisms; the attack lands only if a reader treats the framing as the
   contribution rather than as an interpretation of existing machinery.

## What's missing
- A worked example of an *actual demotion* (a tool losing `autonomous` after a regression)
  would convert the weakest part of the metaphor into a demonstration. Out of scope here;
  flagged as future work in the Conclusion.
- No tie to the live cluster (Tier-B / `mreal/`) in the evidence — the cited numbers are
  sim/curriculum tier. The Conclusion is honest that "the simulation is not the cluster."

## Net assessment
A strong, well-grounded, honestly-bounded Conclusion that earns its central metaphor on three
of four mechanisms and is candid about the fourth (revocation). The rigor is in the
grounding/provenance discipline, not in new capability — appropriate for an authoring task,
but worth naming plainly.
