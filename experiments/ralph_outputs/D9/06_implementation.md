# D9 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/D9/artifacts/`)

### `curriculum_schedule.py`
Consumes A12's `curriculum_order.json` and produces a deterministic banded
training schedule + a GRPO-style training config.
- `load_order()` hard-requires the A12 artifact (no recompute of difficulty).
- `_bands(ids, n_stages)` splits the ordered list into contiguous near-equal bands.
- `build_schedule(order, n_stages, rehearsal, seed, samples_per_incident)`:
  - `curriculum`: progressive unlock (stage k trains bands 0..k), newest band
    weight 1.0, earlier bands weight `rehearsal` (0.3) — anti-forgetting.
  - `random`: seeded deterministic shuffle, band-per-stage, flat weights (control).
  - `anti`: hard→easy reversal (control).
- `training_config(...)`: full RFT/GRPO config (group_size 8, lr 1e-6, kl 0.02,
  per-stage advance criterion mean_reward≥0.55 w/ patience) embedding the
  curriculum schedule, plus an explicit `blocker` field.
- CLI: `--order --stages --rehearsal --seed --out --print`.

### `curriculum_vs_random.py`
Curriculum-vs-random-vs-anti comparison harness.
- `simulate_run(...)`: deterministic competence-vs-difficulty proxy. competence
  rises via a Gaussian learnable band `LR*w*exp(-((d-c)/SIGMA)^2)`; per-stage eval
  is mean `sigmoid(K*(c-d))` over ALL 51 incidents (shared held-out yardstick).
- `compare(n_stages, seeds, rehearsal)`: runs all three orderings (random
  averaged over `seeds`), reports per-stage curves, AUC (area under learning
  curve), and a verdict. Output is loudly labeled SIMULATED.
- CLI: `--stages --seeds --rehearsal --out`.

### `test_curriculum_schedule.py`
10 pytest cases: A12 load, monotone curriculum, band coverage/no-overlap,
progressive unlock + rehearsal weights, seed determinism, shared incident set,
config embeds schedule+blocker, rewards ∈ [0,1], curriculum AUC > random AUC,
anti AUC ≤ curriculum AUC.

## Emitted artifacts (real, regenerable)
- `training_config.json` — 51 incidents, 5 stages, 616-sample budget. Stage 0
  unlocks the easiest leaf faults (cert-expire-leaf-sidecar, fd-exhaust-leaf-
  shipper, mem-leak-leaf-transcoder, ...); later stages add cascades/novel real
  outages.
- `comparison.json` — per-stage curves + verdict (see 07).

## Shared-core safety
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, or any other task dir. A12 is
read-only. `curriculum_vs_random.py` imports `curriculum_schedule` (both local to
D9). The real-eval seam references `rex.scoring.score_plan` by name only — not
imported, not modified.

## Blocker (carried into 07/09)
Real gradient training requires a GPU/training backend (HUD Tinker SDK + a
forked Qwen slug) that is not available in this environment (frozen-LLM project,
~15 min cap). The schedule + config are runnable *inputs* to that loop; the
comparison harness runs a transparent simulation as an eval-side proxy with a
one-function seam to plug in real model rollouts.
