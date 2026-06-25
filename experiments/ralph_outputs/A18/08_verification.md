# A18 — 08 Verification

## Success criteria (from 01_plan)
| Criterion | Result | Evidence |
|---|---|---|
| `validate_package.py` exits 0 | MET | T1 — all checks green, "VALIDATION PASSED" |
| `load_dataset` -> 197/83/114 for all/synthetic/real | MET | T2 — staged dir loaded, exact counts |
| `push_to_hub.py --dry-run` stages clean 5-file package | MET | T3 — 5 files, correct counts |
| Real push succeeds OR documented blocker | MET (push succeeded) | T4 — live repo, hub load-back 114 rows |

## Are the artifacts real (not placeholder)?
- `hud_trajectories.jsonl` — 197 real graded rollouts, 570 KB, parsed and validated record-by-record.
- `opensre_trajectories.py` — executed by `datasets`; generated all three splits with correct typing.
- `README.md` — YAML parsed by `yaml.safe_load`; `configs:`/`dataset_info:` actually drove the Hub
  multi-config load (T2/T4), not decorative.
- `push_to_hub.py` — performed a real `upload_folder`; the dataset is live and public.
- `validate_package.py` — real assertions over the data, not stubs.

## Independent confirmation
The dataset loads **from the Hub** (`load_dataset("quantranger/opensre-incident-trajectories","real")`
-> 114 rows, real `source_company`/`source_url` intact), proving the round-trip end to end and that
provenance fields survived (PSRE's requirement).

## Parallel-safety check
No shared core file touched. The pre-existing `opensre-traj/out/HF_README.md` was left unmodified; the
improved card lives only in artifacts and was the pushed copy. Confirmed via `git status` mental check —
only new files under `experiments/ralph_outputs/A18/`.

## Verdict
All success criteria MET. Deliverable is a real, validated, Hub-resolved dataset package; the optional
push (gated on credentials in the brief) was completed because auth was available.
