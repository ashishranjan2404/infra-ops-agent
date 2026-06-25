# F10 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/F10/artifacts/`)

1. **`signoff_sheet.md`** — the deliverable. Three sign-off tables:
   - **A. Primary claims** (C1 harness, C2 Fireball, C3 REx+SME): each row carries a
     paraphrase, evidence pointer, key number, the verbatim caveat from
     CLAIMS_EVIDENCE.md, and three PENDING sign-off cells.
   - **B. Supporting/figure claims** (S1 Diagram1, S2 Diagram2, S3 Diagram3,
     S4 false-allows) with status from the evidence-to-diagram mapping table.
   - **C. Negative/blocked** (N1 Diagram6 flat reward, N2 RLVR-harness ambiguity) —
     disclosures that still require sign-off.
   - Appendices: verbatim full claim text, primary-reviewer responsibility map,
     explicit blocking conditions, usage instructions.

2. **`signoff_request.md`** — send-ready, channel-agnostic request message with a
   "do NOT auto-send" banner, numbered asks, the two hard blockers (Wenji pushes
   GRPO branch; resolve N2), a `[deadline]` placeholder, and per-author TL;DRs.

3. **`check_signoff.py`** — stdlib validator. Parses every author-column table,
   classifies each claim row as cleared/partial/rejected/pending/malformed, and
   checks that cited in-repo evidence files exist (flagging the GRPO run as a known
   external blocker). Status report, not a CI gate (PENDING is normal; only malformed
   → exit 1).

4. **`BLOCKER.md`** — documents why a coordination task cannot be agent-completed,
   the three hard external blockers, what was delivered, and the human definition of done.

## Grounding
Every claim, number, and caveat is copied from `experiments/CLAIMS_EVIDENCE.md`
(C1/C2/C3 statements, the 89.7%/94.9% harness numbers, the 0.687 vs 0.242 ablation
numbers, the "baselines too close" flag, the unpushed-GRPO note, the flat Diagram-6
reward). No new numbers were invented.

## Core-file safety
No shared core file was edited. Only new files under the F10 artifacts directory were
created. The validator reads `rex/runs/*.json` and `experiments/CLAIMS_EVIDENCE.md`
read-only to confirm existence; it does not modify them.

## Deviations from spec
None material. The json *contents* are intentionally not validated (out of scope per
Ouroboros Engineer 2 — avoids coupling to a schema we don't own); only existence is checked.
