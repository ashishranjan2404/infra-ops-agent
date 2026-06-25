# E10 — Test results

## Test 1 — automated validation gate
Command:
```
python3 experiments/ralph_outputs/E10/artifacts/validate_section.py
```
Output:
```
PASS
  subsections: 6/6 in order
  experiments E3..E9: present
  PENDING cells: 34
  result-table fabricated numbers: 0
  citations: rex/scoring.py, eval_pass_at_k, SCHEMA.md present
  falsification criterion: present
exit=0
```
**Result: PASS.** All six spec gates hold:
- 6/6 required H2 subsections present and in order.
- E3–E9 all present in the design.
- 34 `PENDING` cells (spec required ≥12).
- **0 fabricated numeric values** in any result-table (T1/T2/T3) data cell — the
  anti-fabrication gate is the load-bearing check and it passes.
- Real-object citations (`rex/scoring.py`, `eval_pass_at_k`, `SCHEMA.md`) present.
- Falsification / null criterion present.

## Test 2 — markdown table well-formedness
Parsed every pipe-table and checked uniform column count per table.
Output:
```
tables found: 5; ragged tables: none
```
**Result: PASS.** All 5 tables (H1–H4 hypotheses, E3–E9 design, T1, T2, T3) are
rectangular / well-formed.

## Test 3 — anti-fabrication spot check (manual)
Confirmed the decimals that DO appear in the document are legitimate and confined to:
- the reward weights in prose (`0.30·diagnosis + 0.25·correct_fix + 0.45·resolved − 0.60·trap`)
  — cited from `rex/scoring.py`, not a result;
- benchmark sizes (14 cascades, 8 simple, 10 novel) — integers, dataset sizes, not results.
No decimal appears inside a T1/T2/T3 result cell (confirmed by Test 1's scoped grep).

## Fixes applied
None required — the validator passed on first run. The grep gate was deliberately *scoped*
to result-table cells (per ouroboros fix A2) so legitimate prose numbers (reward weights,
benchmark counts) do not trip it; that scoping was designed in before running, and the run
confirmed it behaves correctly (PASS with 0 result-cell numbers while prose decimals remain).
