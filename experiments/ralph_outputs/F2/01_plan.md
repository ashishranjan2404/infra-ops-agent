# F2 — 01 Plan

## Objective
Write an honest, reviewer-defensible **Limitations** section (markdown) for the
SRE-Degrees paper. It must be *grounded in real findings already in `experiments/`*,
not generic boilerplate. The point is candor: name what is synthetic, what is
single-domain, what is preliminary, and what is actively broken (reward hacking).

## Approach
1. Mine the existing evidence base for concrete, citable limitations:
   - `experiments/FINAL_SUMMARY.md` (flat RFT, partial ablation, blocked Fireball)
   - `experiments/CLAIMS_EVIDENCE.md` ("what's missing" per claim, single-model, semi-synthetic SME)
   - `ralph_outputs/D13/SUMMARY.md` (reward-hacking the deterministic judge — 5 exploit classes)
   - `scenarios/cidg/generated/*.yaml` (synthetic incidents — count, provenance)
2. Group limitations into themes: (a) synthetic data, (b) single-domain, (c) preliminary
   RFT, (d) reward-function fragility / reward hacking, (e) evaluation-judge limits,
   (f) statistical power / single-model, (g) blocked replications.
3. Each limitation: state it plainly, cite the file/number that proves it, and say what
   it does (and does not) invalidate. Add a short "what would fix it" where honest.
4. Deliver as a standalone markdown artifact that can be pasted into the paper.

## Files to create (task-namespaced, no core edits)
- `artifacts/LIMITATIONS.md` — the deliverable section.
- `artifacts/evidence_index.md` — file:line citations backing each claim (auditability).
- `artifacts/check_limitations.py` — parse-check + verifies every cited file exists.
- The 10 step files + SUMMARY.md + result.json.

## Dependencies
- Read-only access to `experiments/` and `scenarios/`. No training, no API, no cluster.
- Python 3.13 for the parse-check script (stdlib only).

## Risks
- **Over-claiming honesty**: writing limitations that aren't actually true of this work.
  Mitigation: every limitation must cite a real artifact/number.
- **Hedging into uselessness**: a limitations section that undercuts every claim.
  Mitigation: scope each limitation to what it actually invalidates.
- **Citing files that moved/don't exist**: Mitigation: `check_limitations.py` asserts
  each cited path exists.

## Success criteria
- `LIMITATIONS.md` parses as valid markdown, ≥6 distinct grounded limitations.
- Every numeric/empirical claim traces to a real file in the repo (evidence_index).
- `check_limitations.py` runs green: all cited files exist.
- No shared core file edited.
