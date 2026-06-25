# Human blocker — F10 (co-author sign-off)

## Why this task cannot be completed by the agent

F10 is a **coordination task**. The deliverable — three humans (Ashish, Wenji,
Sylvie) reading the evidence and signing off — requires human judgment and human
authority. A Ralph worker can build the *instrument* (the sign-off sheet, the
evidence pointers, the request message) but **cannot itself approve a claim** on
behalf of an author. Doing so would be fabrication.

Therefore every sign-off cell ships as `PENDING`. This is the correct, honest state.

## Hard external blockers (not just "humans haven't replied yet")

1. **C2 (Fireball) is structurally unreviewable today.**
   The evidence is "Wenji's GRPO run (NOT YET PUSHED to repo)"
   (`experiments/CLAIMS_EVIDENCE.md` L38). The artifact does not exist in the
   codebase. No author — human or agent — can verify a claim whose evidence is
   absent. **Action owner: Wenji. Action: push GRPO branch.**

2. **N2 (RLVR harness-in-loop ambiguity) is an open question.**
   `CLAIMS_EVIDENCE.md` L131: "must clarify whether RLVR was run with or without
   the harness." Until resolved, C2 and N1 sign-offs are premature.
   **Action owner: Wenji.**

3. **Diagram 6 fine-tuning is incomplete** (reward FLAT 0.522→0.491; 8B/30B
   crashed — L94, L127-131). It must be disclosed as negative, not claimed.
   Wenji's ask: rerun with Qwen-14B to step 25+. **Action owner: Wenji.**

## What the agent CAN and DID deliver

- `signoff_sheet.md` — per-claim sheet, every major claim + evidence pointer +
  per-author sign-off column, grounded in CLAIMS_EVIDENCE.md.
- `signoff_request.md` — send-ready draft request message.
- `check_signoff.py` — validator that parses the sheet and reports cleared vs
  blocked claims, so progress is mechanically trackable.

## Definition of done (for the humans, post-handoff)

- All rows in sections A–C have all three columns = `APPROVED`
  (or a recorded `REJECTED`/comment that the team has resolved).
- `check_signoff.py` reports `0 blocked, 0 pending`.
- C2's evidence is actually in the repo.
