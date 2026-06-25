# 06 — Implementation

## What I built (real artifacts)
1. **`artifacts/why_were_different.md`** — the one-pager. Structure: thesis + incumbent contrast →
   the wedge (open graduation benchmark + trap-action safety, with the concrete control-plane
   trap example and the reward formula) → the moat (verifiable env, learned/generalizing verifier,
   two-tier fidelity, model-frozen) → proof points (4 cited real-run numbers) → an explicit
   "what we do NOT claim" honesty block (the fair-control ablation + contamination defense) →
   the ask (partners + investors). Every number carries an inline source.
2. **`artifacts/proof_points.json`** — 12 machine-checkable claims (C1–C12), each with a value
   and a repo source path, so the one-pager is auditable rather than vibes.

## Source synthesis (no fabrication)
All claims trace to real repo files read this session:
- `ARCHITECTURE.md` — thesis, reward formula, REx frontier table, two-tier fidelity, reproducibility.
- `docs/headline_insights.md` — verifier generalization (C5), one-shot separation (C6), the
  honest ablation (C9).
- `opensre-traj/specs/real/*.json` (C1=19, counted) and `scenarios/cidg/generated/*.yaml`
  (C2=51, counted).

## Design decisions carried from the grill/ouroboros
- Moat = environment + verifier, NOT the refinement loop (grill consensus).
- REx framed by its **escalation/safety** behavior and **hard-tier** value, never the easy-tier
  raw lift, to avoid self-contradiction with the ablation (ouroboros critic 3).
- "Open graduation benchmark" qualified in-phrase; explicit "we do not claim uncontaminated."
- Honest ablation kept ON the page as a credibility signal.

## Shared-core safety
No shared core files edited. All writes are under `experiments/ralph_outputs/G8/`. No
`rex/*.py`, `sim/*.py`, `agent/*.py`, `ralph_status.json`, or other task dirs touched.

## Note on G5/G6/G7
Those directories existed but were empty at run time (parallel workers in flight), so I
synthesized the competitive frame directly from the verified repo assets and made every claim
auditable via `proof_points.json`. Documented as a dependency note in `07`/`09`.
