# F10 — 01 Plan

## Objective
Produce a per-claim **co-author sign-off sheet** so Ashish, Wenji, and Sylvie can
formally approve every major paper claim before submission. The agent cannot
execute the coordination (humans must sign), so the real deliverable is the
*instrument*: a sheet pairing each claim with its evidence pointer and a per-author
sign-off column, a draft request message, a validator, and an honest blocker doc.

## Approach
1. Treat `experiments/CLAIMS_EVIDENCE.md` as the single source of truth. Enumerate
   every claim: 3 primary (C1 harness, C2 Fireball, C3 REx+SME), figure-level
   supporting claims (S1–S4), and negative/blocked results (N1 fine-tuning flat,
   N2 RLVR-harness ambiguity).
2. For each claim: paraphrase, attach the exact evidence file/diagram, record the
   key number, copy the known caveat verbatim, add three sign-off cells = PENDING.
3. Add a primary-reviewer responsibility map and explicit blocking conditions.
4. Write a send-ready sign-off request message (channel-agnostic).
5. Write a validator that parses the sheet, tallies cleared/pending/rejected, and
   checks that cited in-repo evidence exists.
6. Document the human blocker honestly (C2 unreviewable until GRPO branch pushed).

## Files to create (task-namespaced, no core edits)
- `artifacts/signoff_sheet.md` — the deliverable sheet.
- `artifacts/signoff_request.md` — draft request message.
- `artifacts/check_signoff.py` — validator (stdlib only).
- `artifacts/BLOCKER.md` — human blocker documentation.
- 10 step files + SUMMARY.md + result.json.

## Dependencies
- Read-only access to `experiments/CLAIMS_EVIDENCE.md` and `rex/runs/*.json`.
- Python 3.13 stdlib for the validator. No API, no cluster, no training.

## Risks
- **Fabrication risk:** the temptation to mark cells APPROVED. Mitigation: all cells
  ship PENDING; only humans may approve.
- **Drift from source:** inventing numbers. Mitigation: copy numbers/caveats verbatim
  from CLAIMS_EVIDENCE.md; validator checks evidence files exist.
- **C2 evidence absent:** the Fireball GRPO run is not in the repo — must be surfaced
  as a hard blocker, not silently signed.

## Success criteria
- Sheet covers all 3 primary claims + supporting + negative results.
- Every claim has an evidence pointer that resolves to a real file (or is flagged
  external).
- Validator parses cleanly and reports the correct PENDING tally.
- Draft message + blocker doc are concrete and send/handoff-ready.
