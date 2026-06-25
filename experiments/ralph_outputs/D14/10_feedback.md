# D14 — 10 Feedback for the next task

The biggest trap on the opensre RFT env is the **task-selection index space**: the stock
runner (`train_rft_v2.py`) selects tasks by integer index into `Taskset.from_module`, which
only enumerates the 34 *canonical* ids from `canonical_ids()` — so any task set that includes
`-sNNN` variants (or wants >34 tasks) is silently uninexpressible by index and must be built
from explicit `investigate_v2(scenario_id=...)` calls. Two cheap-but-real gotchas cost time:
(1) the corpus uses the field `difficulty`, NOT `scenario_difficulty` (that key lives only in
the spec JSONs), so any curriculum/sort that reads the wrong key is a silent no-op; and
(2) anything that imports `hud_env`/`hud_env_v2` drags in `from hud import ...`, which only
works in `.venv-hud` (3.12) — keep offline validation paths (dry-runs, id checks) reading
`out/trajectories.jsonl` directly so they run in system python3. Finally, the trainable head
is a *shared* resource: concurrent Ralph workers will 409 each other on forward-backward, so
treat that as transient (the `_aretry` wrapper handles it) and prove the pipeline with a
single-step smoke before committing to a long run under any compute cap. The corpus has 319
scenarios (34 canonical + 285 variants), so there's ample real material for larger task sets
without fabricating anything.
