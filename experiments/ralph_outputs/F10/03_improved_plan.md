# F10 — 03 Improved Plan

## What changed after the grill

| Change | Source critique | Accepted? |
|---|---|---|
| Add advisory primary-reviewer map (unblocking ownership) on top of 3 equal sign-offs | PSRE vs RLE synthesis | ACCEPTED |
| Put N1/N2 negative/blocked results on the sheet as sign-off rows | REV | ACCEPTED |
| Caveat column sits beside the key-number column in every row | REV | ACCEPTED |
| Validator is a status report (PENDING ≠ error); only malformed errors | DOL vs RLE | ACCEPTED |
| C2 marked explicitly "blocked — evidence not in repo" in BLOCKER.md | SMR | ACCEPTED |
| Send-ready request message with owner + deadline placeholder | DOL | ACCEPTED |

## Rejected critiques (and why)

- **RLE: drop the primary-reviewer map entirely** (fear of rubber-stamping).
  REJECTED. PSRE's counter is stronger: with no owner, the missing C2 evidence never
  gets pushed. Mitigation for RLE's concern: the map assigns *unblocking* ownership,
  and all three sign-offs remain mandatory and equal, so it does not reduce the
  three-way check.
- **DOL: hard CI gate "all-APPROVED-or-nothing-ships."** REJECTED as a literal gate.
  C2 is legitimately unreviewable today; a blanket gate just yields a permanent red.
  Kept the *intent* (a claim ships only when its row is all-APPROVED) as documentation
  in the sheet, but the validator reports rather than blocks.
- **SMR: "process, not science."** PARTIALLY REJECTED. Treated sign-off as an
  integrity step (REV's framing), which is why negative results and caveats are
  first-class on the sheet.

## Final plan
Build `signoff_sheet.md` with three tables (A primary, B supporting, C negative),
caveat beside number, three equal PENDING sign-off columns, a primary-reviewer
responsibility map, and explicit blocking conditions. Add `signoff_request.md`
(owner + deadline placeholder), `check_signoff.py` (status-report validator), and
`BLOCKER.md`. Validate the parser against the real sheet.

## Success criteria (unchanged, sharpened)
- All 3 primary + 4 supporting + 2 negative claims present, each with a resolving
  evidence pointer.
- Validator reports `9 pending, 0 malformed` and confirms 4 in-repo evidence files
  exist; flags C2's GRPO evidence as external.
