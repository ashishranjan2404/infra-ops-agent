# E7 — 08 Verification

## Against success criteria (from 01/03)
| criterion | met? | evidence |
|---|---|---|
| Survey candidate game datasets | YES | 01_plan table: TextWorld, Jericho, ALFWorld (+SRE ref) with per-step signals & rationale |
| Domain-agnostic trajectory adapter | YES | `trajectory_adapter.py` — single canonical schema + registry + 4 adapters |
| Generic adapter + unit test on synthetic fixture | YES | `test_trajectory_adapter.py` (12 PASS) over `synthetic_fixtures.json` |
| Adapted **game** traj scored by REAL SRE judge, no core edit | YES | `test_adapted_game_traj_scorable_by_real_sre_judge` calls `rex.scoring.deterministic_judge` + `mechanism_score` |
| Transfer-experiment plan | YES | `TRANSFER_PLAN.md` — H1/H0, C0–C3 conditions, 4 metrics, 2 ablations, caveats |
| Do NOT edit shared core files | YES | `git status` shows only new files under E7/; no `rex/*.py` / `sim/*.py` change |

## Outputs real, not placeholder?
- Adapter is **runnable** (smoke `__main__` produces real JSON).
- Tests **actually execute** and import the project's real scoring module.
- Fixtures are **valid JSON** with loader-accurate field names.
- Plan references **real APIs** (`tw-make`, `jericho`, `alfworld` pip pkgs) and
  real project functions (`deterministic_judge`, `mechanism_score`,
  `judge_diagnosis`, `eval_pass_at_k`).

## Honest scope statement
The deliverable verifies **plumbing + a runnable transfer protocol**. It does
NOT, and does not claim to, demonstrate that transfer *succeeds* — that requires
the live C0–C3 run on real TextWorld/Jericho/ALFWorld data (documented blocker).

## Core-file non-modification check
```
$ git status --short | grep -E 'rex/|sim/|agent/|experiments/.*\.py'
(only pre-existing repo modifications unrelated to E7; no E7 edits to core)
```
All E7 writes are confined to `experiments/ralph_outputs/E7/`.
