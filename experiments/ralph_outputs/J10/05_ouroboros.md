# J10 — Ouroboros (self-critique as 3 engineers, sequential)

## Engineer A — "the integrity auditor"
**Problems found:**
- A1. The banned-phrase list is too easy to evade — e.g. "MTTR dropped 40%" uses neither
  "mttr reduction of" nor "% mttr" literally. The guard gives false confidence.
- A2. `test_grounding_paths_exist` checks paths exist but not that they're *non-empty* — a
  zero-byte placeholder would pass and look grounded.
- A3. The spec lets `grounding` be empty `[]` for a lesson, which silently permits an
  ungrounded claim. The whole point is grounding.

**Fixes:** broaden BANNED_PHRASES to also catch the digit-pattern `r'\bmttr\b[^.]{0,20}\d'`
and `r'\d{1,3}\s*%[^.]{0,15}\bmttr'` via regex (not just literal substrings). Assert each
grounding file is non-empty. Require every lesson/gap to have ≥1 grounding path.

## Engineer B — "the SRE who has to sign the deploy ticket"
**Problems found:**
- B1. A go/no-go checklist with everything "blocked" is honest but operationally useless —
  it gives no *order*. Which gap must close FIRST? I need a critical path.
- B2. G1 (distribution shift) protocol says "measure trap recall off-distribution" but never
  says *where the off-distribution incidents come from*. With no real incident stream, the
  protocol is unrunnable as written — that's the real blocker and it must be named.
- B3. Rollback was added to the checklist but the doc never states the agent's current
  rollback capability. If it's "none," say "none."

**Fixes:** add an explicit ordering / critical path to section 3 (G2 shadow-mode is the gate
that unblocks G1 and G3, because it's the only one runnable without giving the agent write
access). For G1, name the data dependency honestly: requires a real or held-out incident
stream we do not yet have; the held-out CIDG scenarios are the *closest available proxy* and
that limitation is stated. State current rollback capability as "not implemented in the loop."

## Engineer C — "the skeptical reviewer"
**Problems found:**
- C1. Risk of the doc reading as *all caveats, zero contribution* — exactly the "vacuous
  honesty" failure the grill warned about. Need to make the transferable lessons land as
  real, defensible claims, not apologies.
- C2. L4 ("no clean ground truth") could be read as "so nothing here is validated," which
  overshoots — A16 DID validate 54/61 fixes against the engine. That's a real positive
  result and should not be drowned.
- C3. The JSON and the MD can drift: a lesson reworded in MD but stale in JSON. The tests
  check the MD has anchors and the JSON has gaps, but never that they *agree*.

**Fixes:** open section 1 with a one-line positive thesis ("Here is what we can actually
defend:") and keep L3 explicit that 54/61 fixes are engine-validated. Add a light cross-check
in the test: every gap id in JSON (G1/G2/G3) must also appear as a heading anchor in the MD.

## Final filtered spec (deltas applied)
- BANNED guard upgraded to regex + literal list (A1).
- Grounding files asserted **non-empty** and **≥1 per lesson/gap** (A2, A3).
- Section 3 gains an explicit **critical path**: G2 shadow-mode first (read-only, runnable),
  which then unblocks G1 and G3 (B1, B2).
- G1 names its data dependency + uses held-out CIDG as the stated best-available proxy (B2).
- Rollback capability stated as "not implemented in the loop" (B3).
- Section 1 opens with a positive thesis; L3 keeps the 54/61 engine-validated result (C1,C2).
- New test: JSON gap ids must appear as MD anchors (C3).
Rejected: none — all three engineers' fixes are cheap and increase rigor.
