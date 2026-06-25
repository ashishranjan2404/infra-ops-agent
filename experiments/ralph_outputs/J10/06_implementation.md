# J10 — Implementation

## What I built (real, task-namespaced artifacts under `experiments/ralph_outputs/J10/artifacts/`)

1. **`lessons_from_production.md`** — the deliverable section itself. An honest
   "Lessons from (Pre-)Production: A Deployment-Readiness Analysis." Section 0 states
   plainly that the agent has never run in a live production environment and no production
   metrics are reported. Section 1 gives four transferable lessons (L1 action-layer safety,
   L2 gameable reward → action-safety [D13], L3 substrate fidelity bounds/biases [A16],
   L4 no clean outcome ground truth [A9]). Section 2 gives the three required deployment
   gaps (G1 trap-action safety under distribution shift, G2 shadow-mode, G3 MTTR), each
   with a concrete validation protocol and an acceptance gate labeled
   `TARGET — NOT YET MEASURED`. Section 3 is a go/no-go checklist with an explicit critical
   path (shadow-mode first). Section 4 is an honest bottom line separating what we can and
   cannot stand behind.

2. **`readiness_gaps.json`** — machine-checkable registry of the lessons + gaps + checklist.
   Every lesson and gap carries `grounding` paths to real repo artifacts.

3. **`check_readiness.py`** — validator/renderer. `verify()` enforces: exactly {G1,G2,G3}
   with the required name tokens; every grounding path exists and is non-empty; every
   lesson/gap has ≥1 grounding; every acceptance gate carries the `TARGET — NOT YET MEASURED:`
   label; and no fabricated-prod phrasing (literal list + regex for sneaky MTTR-percentage
   claims). `verify_md()` additionally scans the markdown for banned phrasing and cross-checks
   that every G1–G3 and L1–L4 heading is present (JSON↔MD agreement).

4. **`test_readiness.py`** — 7 pytest cases covering schema, the three required gaps,
   grounding existence+non-emptiness, gate labeling, no fabricated phrasing in the MD,
   required sections present, and a clean `verify()`.

## Grounding sources (verified present in the repo before writing)
- `rex/scoring.py` — trap-action mechanism (closed author-defined vocab), safety-harness
  BLOCK, hedge→0.55 scoring weights (W_ROOT 0.30 + W_FIX 0.25).
- `experiments/ralph_outputs/D13/SUMMARY.md`,`result.json` — 5 reward-hacks, hedge 92.9%.
- `experiments/ralph_outputs/A16/SUMMARY.md`,`validation_report.json` — 54/61 fixes resolve,
  7 broken, unmodeled metrics + hysteresis.
- `experiments/ralph_outputs/A9/SUMMARY.md` — 18 sourced / 12 unknown MTTR.

## The integrity guard caught a real bug in my own draft
On first run, `check_readiness.py` and `test_readiness.py` FAILED: my section-0 sentence
"has not been deployed to production" tripped the banned-phrase guard (substring
"deployed to production"). I reworded it to "has not run in a live production environment."
This is the guard working as designed — it prevents fabricated-prod phrasing even when the
surrounding sentence is a legitimate negation, forcing unambiguous wording. After the fix:
validator exits 0, all 7 tests pass (see `07_test_results.md`).

## Shared-core safety
No shared core file was edited. All four artifacts are new files under the J10 task dir.
Grounding paths are read-only references; nothing in `rex/`, `sim/`, `agent/`,
`experiments/*.py`, or any dashboard was modified.
