# E7 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/E7/artifacts/`)
1. **`trajectory_adapter.py`** — the deliverable. Pure-stdlib module:
   - `CanonicalStep`, `CanonicalTrajectory` dataclasses (shape-only, domain-agnostic).
   - A registry (`@register("domain")`) + `adapt()` / `adapt_many()` / `_validate()`.
   - Four adapters: `textworld`, `jericho`, `alfworld`, and a reference `sre`
     adapter that proves the canonical schema is a strict superset of the
     project's own incident-trajectory shape.
   - `to_sre_scoring_inputs()` projects a trajectory into the EXACT kwargs of
     `rex/scoring.deterministic_judge` so adapted **game** episodes are scorable
     by the existing SRE eval stack with **zero core-file edits**.
   - `__main__` smoke demo.
2. **`synthetic_fixtures.json`** — one realistic raw episode per domain, with
   field names matching the actual loaders (TextWorld `admissible_commands`,
   Jericho `valid_actions`, ALFWorld `admissible_actions`).
3. **`test_trajectory_adapter.py`** — 12 pytest cases incl. a real call into
   `rex/scoring.py` on an adapted TextWorld trajectory.
4. **`test_run.log`** — captured verbose run.
5. **`TRANSFER_PLAN.md`** — the transfer-experiment plan (baselines, metrics,
   ablations, blocker).

## Core-file safety
NO shared core file was modified. The adapter only *imports* `rex.scoring`
read-only. Conceptual core change (registering game domains in the eval CLI) is
described in `TRANSFER_PLAN.md` as a future patch, not applied.

## Known caveats baked in
- **Weak-gold fallback:** if a log lacks a walkthrough, `gold_target` falls back
  to the goal text. Fixtures all supply real gold so the demo never relies on it.
- **Oracle-handicap:** `available_actions` (TextWorld admissible / Jericho valid)
  is an inference-time oracle absent in deployment; kept in-schema and the
  experiment plan ablates it. `_validate` records an `action ∉ available_actions`
  warning into `meta["warnings"]`.
- **Synthetic ≠ transfer evidence:** fixtures validate plumbing only.
