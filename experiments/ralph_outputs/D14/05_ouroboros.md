# D14 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "the corpus-field skeptic"
**Problem found:** The spec's `_difficulty` originally read `scenario_difficulty`, but the
*corpus* records (trajectories.jsonl) use the key `difficulty`; `scenario_difficulty` only
exists in the separate spec JSONs. With the wrong key every task defaults to 3 → the
curriculum is a no-op (all equal) and the headline "curriculum: true" is a lie.
**Fix:** read `rec.get("difficulty", rec.get("scenario_difficulty"))`. Verified the corpus
yields difficulty 3/4/5 (counts 9/15/18 in the 42-set) and the curriculum reorders reals last.

## Engineer B — "the import-graph skeptic"
**Problem found:** `--dry-run` is sold as "offline, runs in system Python," but the first
draft imported `hud_env` to read `SCENARIOS`, and `hud_env` does `from hud import ...`.
The `hud` package only installs in `.venv-hud` (3.12); in system Python 3.13 it explodes
on an unrelated `mcp.shared.auth_utils` ImportError. So the dry-run — the one thing meant
to prove correctness without the heavy backend — itself required the backend. Self-defeating.
**Fix:** dry-run now reads `out/trajectories.jsonl` directly to build the corpus-id set; no
`hud_env`/`hud` import. Confirmed it runs clean in system python3 (`missing=[]`, 42 ids).

## Engineer C — "the index-trap skeptic"
**Problem found:** It's tempting to "reuse train_rft_v2.py with `--tasks 0,1,...,41`".
But that runner indexes into `Taskset.from_module(ENV)`, which enumerates only the 34
`canonical_ids()` — index 34..41 would IndexError, and even the valid indices can never
select a variant. So the easy path *cannot* express the 42-set; the 8 variants are
index-invisible. Reusing it would quietly ship a 34-task run mislabeled as 42.
**Fix:** the launcher builds tasks from explicit scenario_ids via `investigate_v2(scenario_id=…)`,
sidestepping the index space entirely. The live smoke confirmed variant ids
(e.g. `001-oom_kill-s019`) instantiate and roll out.

## Final filtered spec (deltas applied)
- `_difficulty` reads the correct `difficulty` corpus key → curriculum is real.
- `--dry-run` reads the corpus file directly → truly offline / backend-free.
- Taskset built from explicit scenario_ids → all 42 (incl. 8 variants) are reachable.
- Remaining known limitation (not a defect, documented in 09): `out:` writes to
  `opensre-traj/runs/` (a shared dir) — acceptable since it's an append-only run log, but
  noted; a copy of the smoke log is archived under this task's `artifacts/`.
