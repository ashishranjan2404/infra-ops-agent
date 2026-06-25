# D14 — 03 Improved Plan

## What changed after the grill

### Accepted
1. **Build the Taskset from explicit scenario_ids, not integer indices** (RLE).
   This is the load-bearing fix: 8 of the 42 are `-sNNN` variants that
   `Taskset.from_module` / `canonical_ids()` never enumerate, so an index-based
   selector (like the stock `train_rft_v2.py --tasks`) silently caps at 34. The
   launcher `train_rft_42.py` now imports `hud_env_v2.investigate_v2` and instantiates
   one task per scenario_id directly.
2. **Provenance metadata in the task file** (AAAI). Each task row carries `kind`
   (canonical|variant), `origin` (real_postmortem|synthetic), `difficulty`, `category`
   so contamination / mix is auditable from the artifact alone.
3. **Keep all 34 canonical + 8 hard variants** (PSRE+SMR compromise). All 19 real
   postmortems retained; synthetic difficulty-3 incidents retained as the curriculum
   floor; variants add within-class spread.
4. **Graceful degradation** (DVO): `--dry-run` validates config + every scenario_id
   against the corpus **without importing the `hud` package** (reads trajectories.jsonl
   directly), so correctness is provable in system Python. `--smoke` runs the real
   pipeline in `.venv-hud`. The forked-slug + `.venv-hud` need is a documented prereq.
5. **Curriculum by REAL difficulty** (SMR). Read the corpus `difficulty` field (values
   3/4/5 here) — NOT a nonexistent `scenario_difficulty` — and order easy->hard.

### Rejected (with reasons)
- **AAAI's "build the train/eval split into D14"** — rejected as scope creep (RLE).
  D14's deliverable is the *training* task set; pass@k eval already lives in
  `rex/eval_pass_at_k.py`. The task file carries enough provenance to construct a split
  downstream; building the split here would over-engineer the task. (AAAI's narrower
  demand — provenance metadata — was accepted.)
- **PSRE's "drop synthetic variants, reals only"** — rejected (SMR). 19 hard tasks give
  almost no early positive reward; the synthetic floor is needed for GRPO to climb.
- **SMR's "42 must be 42 maximally-distinct signals"** — rejected (PSRE). Near-variants
  with different evidence framings are desirable within-class spread for GRPO groups.

## Final shape
- `assemble_tasks.py --n 42` -> `tasks_42.json` (34 canonical + 8 variants; 19 real / 23 synthetic).
- `train_rft_42.yaml` — runnable GRPO config, `tasks: all`, `curriculum: true`, `smoke:` block.
- `train_rft_42.py` — explicit-id Taskset builder; `--dry-run` (offline) + `--smoke` (live).
- Validation ladder: py_compile -> yaml parse -> dry-run (42 ids resolve) -> live smoke.
