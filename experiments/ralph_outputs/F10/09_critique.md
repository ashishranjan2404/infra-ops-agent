# F10 — 09 Critique (honest)

## What's weak

1. **The deliverable is an instrument, not an outcome.** F10's real goal — three
   humans signing off — is unachieved and unachievable by the agent. I produced the
   sheet, the message, and the validator, but every cell is PENDING. A skeptic can
   fairly say "zero claims are actually signed off." That's true and unavoidable; the
   honest move is to ship the instrument and name the blocker, which I did.

2. **Claim selection is my interpretation.** I lifted 3 primary + 4 supporting + 2
   negative claims from CLAIMS_EVIDENCE.md. A reviewer might argue the supporting
   claims (S1–S3) are really facets of C3 and shouldn't be separate rows, or that I
   missed a claim that lives in the paper draft but not in CLAIMS_EVIDENCE.md. I
   deliberately scoped to CLAIMS_EVIDENCE.md (the named grounding) — but if the paper
   has claims outside that file, this sheet is incomplete.

3. **C2 is unverifiable today.** Its evidence (Wenji's GRPO run) is not in the repo.
   The validator can't check it; I keyword-flag it as external. Until pushed, C2's row
   is decorative — no one can responsibly sign it.

4. **Validator is shallow.** It checks file *existence*, not that the numbers in the
   sheet match the json contents. So a future edit that mis-states 89.7% would pass.
   I judged content-validation out of scope (don't own the json schema), but a harder
   version would parse the json and diff the numbers.

## What a reviewer attacks first
- "You can't sign off on a claim whose evidence isn't in the repo" → C2. Mitigated by
  BLOCKER.md naming Wenji as owner of the push.
- "The 4 baselines are statistically indistinguishable" → that's a C3 *content*
  problem inherited from CLAIMS_EVIDENCE.md; the sheet surfaces it as a caveat but
  doesn't fix it (out of scope for F10).

## What's missing
- An automated link between this sheet and the actual paper text (so a signed claim
  can't drift from what's written). Out of scope but would be the natural next task.
- Number-level validation against the json evidence (see weakness 4).

## Honest status
COMPLETED at the deliverable level, BLOCKED at the coordination outcome (by design).
Not over-claimed: no cell is marked approved, the negative results are disclosed, and
the C2 evidence gap is loud.
