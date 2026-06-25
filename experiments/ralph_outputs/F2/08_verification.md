# F2 — 08 Verification

## Success criteria (from 01/03) vs outcome

| Criterion | Target | Result |
|---|---|---|
| ≥6 distinct grounded limitations | 6 | **6** (L1–L6), each cited | ✅ |
| Every empirical claim traces to a real file | 100% | evidence_index: 14/14 rows verified | ✅ |
| `check_limitations.py` green | exit 0 | exit 0, all cited files exist | ✅ |
| LIMITATIONS.md parses / well-formed | yes | single `## Limitations` H2, L1–L6 + Scope | ✅ |
| No shared core file edited | required | only wrote under `F2/artifacts/` | ✅ |
| Closing scope names surviving results | required | Scope names harness 89.7% + REx-SME 2.8× | ✅ |

## Are outputs real (not placeholder)?
Yes. All numbers were lifted from and re-verified against repo artifacts:
- 51 generated YAMLs — counted live via glob.
- 92.9% hedge fool-rate — grep-confirmed in D13 SUMMARY.
- Reward weights 0.30/0.25/0.45 — grep-confirmed in `rex/scoring.py:22`.
- RFT v1 0.522→0.491 / v2 0.504→0.541 — from FINAL_SUMMARY P4.
- Ablation 0.242/0.235/0.230/0.250/0.687 — from CLAIMS_EVIDENCE / ablation.json.
- Harness 66.7%→89.7%→94.9%, false-allow 100%→30.8% — from table3 / FINAL_SUMMARY P5.

## Parallel-safety
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`,
`ralph_status.json`, the dashboard, or any other task's directory. All writes are
under `experiments/ralph_outputs/F2/`.

## Verdict
Deliverable meets all success criteria. The Limitations section is honest,
grounded, reviewer-defensible, and paste-ready.
