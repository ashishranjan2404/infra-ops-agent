# F10 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — Parser-correctness reviewer
**Problems found:**
- The `cell_status` prefix match would mis-classify a cell literally containing the
  word "APPROVED" inside a comment of a REJECTED ("REJECTED: was APPROVED earlier").
  Since I match on the *start* of the cell, "REJECTED: ..." classifies correctly as
  REJECTED — good — but a cell like "APPROVED w/ comment: ... reject ..." correctly
  stays APPROVED. Edge is handled by anchoring on prefix. Confirmed OK after re-check.
- Table detection regex for the separator row (`|---|---|`) must tolerate `:` for
  alignment and optional leading/trailing pipes. Current regex `^\s*\|?[\s:|-]+\|?\s*$`
  covers it. OK.
- **Real gap:** if two tables have author columns at *different* positions, indices
  are recomputed per-table via `header.index(a)`. Good — not hard-coded. OK.

## Engineer 2 — Evidence-integrity reviewer
**Problems found:**
- The evidence-existence check only looks at backtick tokens with `/` and a dotted
  filename. C2's evidence is phrased "Wenji's GRPO run (NOT YET PUSHED)" with no
  backtick path, so it is silently *not checked*. That's a real gap: the most
  important blocker is invisible to the validator.
  **Fix:** add `EXTERNAL_EVIDENCE` keyword matching ("GRPO run") and document C2 as a
  hard blocker in BLOCKER.md so the absence is loud in prose even if not in the parser.
- Diagram references ("Diagram 5") are not files and shouldn't be checked — correctly
  skipped because they lack `/`. OK.
- **Over-engineering risk:** I do not need to validate the *contents* of the json
  files, only that they exist. Verifying numbers against json would couple this task
  to schema we don't own. Deliberately out of scope. OK.

## Engineer 3 — Coordination-realism reviewer
**Problems found:**
- The sheet must not let the agent imply approval. Every cell PENDING — confirmed.
  But the *request message* originally lacked an explicit "do not auto-send" note for
  the human dispatching it. **Fix:** add a "Send-ready draft… do NOT send automatically"
  banner to signoff_request.md.
- Missing: a definition of done the humans can check against. **Fix:** add it to
  BLOCKER.md.
- Under-specified: who owns pushing the C2 branch. **Fix:** name Wenji explicitly in
  both the request and the blocker.

## Final filtered spec (deltas applied)
1. Added `EXTERNAL_EVIDENCE` keyword check so C2's absent evidence is acknowledged.
2. Added "do NOT send automatically" banner to the request message.
3. Added definition-of-done + named owners (Wenji for C2/N2) to BLOCKER.md.
4. Confirmed out-of-scope: validating json contents (avoid over-engineering).
All three reviewers' real problems are resolved or consciously deferred with reason.
