# A12 — 01 Plan

## Objective
Produce a **curriculum ordering (easy → hard)** of the CIDG incident set so that
curriculum-learning experiments (and the existing `rex/curriculum.py` SIMPLE→HARD
tiers) can train/eval on a principled difficulty gradient instead of an arbitrary
file order.

## Approach
Derive a **static, composite difficulty signal** from fields already present in
each scenario spec — no model rollouts required, so the ordering is cheap and
deterministic. Signals available in `scenarios/cidg/generated/*.yaml` +
`registry.json`:
- topology size (nodes + edges)
- `root_cause.hidden`
- `assertions.cascades`, `loudest_alert_not_cause`, `buried_gun_exists`,
  `hysteresis`, `monitoring_degrades`
- `observation.smoking_guns[].buried_under` (depth evidence is buried)
- `len(slo)`, multi-step `canonical_fix`
- `registry.red_herrings` count

These map directly to the difficulty axes already named in `rex/curriculum.py`:
SIMPLE = "loud alert IS the cause, one refinement clinches it"; HARD = "loud alert
is a downstream victim, naive fix worsens it." A weighted sum reproduces and
extends that simple/hard split into a fine-grained order.

## Files to create (all task-namespaced — no shared-core edits)
- `artifacts/build_curriculum.py` — generator script.
- `artifacts/curriculum_order.json` — the ordered output (the deliverable).
- 10 step docs + SUMMARY.md + result.json.

## Dependencies
- `python3`, `PyYAML` (already in repo requirements; `import yaml`).
- Read-only access to `scenarios/cidg/generated/`.

## Risks
- **Static signal ≠ empirical difficulty.** A graph-size/assertion proxy may not
  match measured model pass-rate. Mitigation: emit per-incident feature vector so
  weights can be re-tuned or replaced with empirical pass@k later.
- **Files written by parallel workers** — re-run the generator at the end so the
  count is current.
- Some yamls aren't in `registry.json` (family unknown) — handle gracefully.

## Success criteria
- A valid `curriculum_order.json` with `order_easy_to_hard` listing every incident
  id, the difficulty score + feature breakdown, and the weights used.
- Generator runs clean and is deterministic (stable tiebreak).
- Simple/leaf incidents land at the easy end; real-outage cascades at the hard end.
- No shared core file modified.
