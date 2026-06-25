# F10 — 04 Spec

## Artifacts and contracts

### A. `signoff_sheet.md`
Markdown. Three pipe tables, all sharing the trailing columns `Ashish | Wenji | Sylvie`.

- **Table A (primary):** columns
  `# | Claim | Evidence pointer | Key number | Known caveat | Ashish | Wenji | Sylvie`.
  Rows: C1, C2, C3.
- **Table B (supporting):** `# | Claim | Evidence pointer | Status | Ashish | Wenji | Sylvie`.
  Rows: S1–S4.
- **Table C (negative/blocked):** same shape as B. Rows: N1, N2.
- Sign-off cell grammar: one of
  `PENDING` | `APPROVED` | `APPROVED w/ comment: <text>` | `REJECTED: <text>`.
- All cells initialize to `PENDING`.
- Appendices: verbatim full claim text; primary-reviewer responsibility map;
  blocking conditions; usage instructions.

**Invariant:** no number or caveat may appear that is not present in
`experiments/CLAIMS_EVIDENCE.md`.

### B. `signoff_request.md`
Send-ready message. Subject line, body addressed to the three authors, numbered
asks, two hard blockers (C2 push, N2 RLVR clarification), `[deadline]` placeholder,
per-author TL;DR. Channel-agnostic (email or Slack).

### C. `check_signoff.py`
Signature & behavior:

```
main(argv) -> int   # 0 = parsed OK, 1 = malformed rows, 2 = file not found
```

Helper functions:
```
split_row(line: str) -> list[str]          # markdown row -> trimmed cells
cell_status(cell: str) -> str | None       # -> "PENDING"|"APPROVED"|"REJECTED"|None
parse_tables(text: str) -> Iterator[(header, rows)]  # only tables with author cols
```

Classification per claim row (over Ashish/Wenji/Sylvie cells):
- `rejected`  if any cell == REJECTED
- `cleared`   if all three == APPROVED
- `pending`   if all three == PENDING
- `partial`   otherwise (mixed APPROVED/PENDING, none rejected)
- `malformed` if any author cell is missing or unclassifiable

Evidence check: extract every backtick token containing `/` and a dotted filename;
resolve against repo root (`F10/artifacts/../../../..`). Report present / missing /
external (tokens matching `EXTERNAL_EVIDENCE = ("GRPO run",)` are known-absent, not
errors). Stdlib only.

### D. `BLOCKER.md`
Documents: why a coordination task can't be agent-completed; the three hard external
blockers (C2 unpushed, N2 ambiguity, Diagram 6 incomplete); what was delivered;
definition of done for the humans.

## Test cases (executed in 07)
1. Validator on the real sheet → `9 pending, 0 malformed`, 4 evidence files present.
2. Synthetic sheet with one APPROVED row → that claim reports `cleared`.
3. Synthetic sheet with a REJECTED cell → reports `rejected`.
4. Synthetic sheet with a missing author cell → reports `malformed`, exit 1.
5. `python3 -m py_compile check_signoff.py` → clean.
