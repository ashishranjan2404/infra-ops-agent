# F10 — SUMMARY

**Task:** Get all co-authors (Ashish, Wenji, Sylvie) to sign off on the paper's
claims. This is a coordination task the agent cannot directly execute, so the
deliverable is the *instrument* to drive sign-off + an honest blocker.

## Delivered (all in `experiments/ralph_outputs/F10/artifacts/`)
- **`signoff_sheet.md`** — per-claim sign-off sheet. 9 claims across 3 tables
  (3 primary: C1 harness, C2 Fireball, C3 REx+SME; 4 supporting: S1–S4; 2 negative:
  N1 flat fine-tune, N2 RLVR-harness ambiguity). Each row: evidence pointer, key
  number, verbatim caveat, and a PENDING sign-off cell per author. Plus a
  primary-reviewer responsibility map and explicit blocking conditions.
- **`signoff_request.md`** — send-ready draft request message (owner + `[deadline]`
  placeholder, two hard blockers called out, per-author TL;DRs, do-not-auto-send banner).
- **`check_signoff.py`** — stdlib validator; tallies cleared/partial/rejected/pending/
  malformed and checks cited in-repo evidence exists. 5/5 tests pass.
- **`BLOCKER.md`** — documents the human/coordination blocker and the C2 evidence gap.

## Grounding
Entirely from `experiments/CLAIMS_EVIDENCE.md`. No invented numbers. The 4 in-repo
evidence files (CLAIMS_EVIDENCE.md, rex/runs/ablation.json, frontier.json,
harness_synth_v2.json) all resolve on disk; C2's GRPO evidence is flagged external
(not yet pushed).

## Status
**COMPLETED** at the deliverable level. The downstream *outcome* (actual approvals) is
an inherent **human blocker** — every cell ships PENDING because only humans may
approve. C2 has an additional hard blocker: its evidence is not in the repo until
Wenji pushes the GRPO branch.

## Core-file safety
No shared core files edited. Only new files under F10/artifacts/. Evidence files read
read-only for existence checks.
