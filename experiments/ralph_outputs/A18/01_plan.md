# A18 — Upload dataset to HuggingFace with proper metadata — 01 Plan

## Objective
Produce an upload-ready HuggingFace **dataset package** for the OpenSRE Incident-Diagnosis
Trajectories (the 197 graded SRE rollouts in `opensre-traj/out/hud_trajectories.jsonl`): a
`datasets` loading script, a dataset card (README) with valid YAML metadata front-matter, and a
`huggingface_hub` push script. Validate offline (and push if credentials exist).

## Approach
1. Inspect the canonical data (`hud_trajectories.jsonl`, 197 records) + existing `HF_README.md`.
2. Author a typed `datasets` loading script with 3 configs: `all` / `synthetic` / `real`.
3. Author a dataset card with rich YAML front-matter (license, tags, task_categories, `configs:`,
   `dataset_info:` with the full feature schema + split counts).
4. Author a `push_to_hub.py` (build package -> split shards -> `HfApi.upload_folder`) with a
   `--dry-run` that needs no network.
5. Author `validate_package.py` — offline schema + YAML + loader checks.
6. Validate; load locally via `datasets.load_dataset`; push if HF auth present.

## Files to create (all under experiments/ralph_outputs/A18/artifacts/)
- `opensre_trajectories.py` — loading script (3 configs, typed Features).
- `README.md` — dataset card + YAML metadata.
- `push_to_hub.py` — upload script (huggingface_hub) + dry-run.
- `validate_package.py` — offline validator.
- `hud_trajectories.jsonl` — bundled copy of the data for self-containment.

## Dependencies
`huggingface_hub` (1.11.0, present), `datasets` (5.0.0, present), `pyyaml`. No core-file edits.

## Risks
- HF auth may be absent -> treat real push as documented blocker (dry-run is the deliverable).
- Heterogeneous schema (real-only fields `difficulty`/`source_company`/`source_url`/`trap_actions`)
  -> loader must default-fill for synthetic to keep one uniform `Features` schema.
- YAML `dataset_info` counts must match actual data or the Hub card validator complains.

## Success criteria
- `validate_package.py` exits 0 (schema + YAML + loader all green).
- `datasets.load_dataset(<stage>, cfg)` returns 197/83/114 for all/synthetic/real.
- `push_to_hub.py --dry-run` stages a clean 5-file package.
- Real push succeeds OR is documented as a blocker with the exact missing credential.
