# A18 — 04 Spec

## Source of truth
`/Users/mei/rl/opensre-traj/out/hud_trajectories.jsonl` — 197 newline-delimited JSON objects.
Distribution: models {opus-4-8:68, kimi-k2p5:61, haiku-4-5:68}; sources {real:114, synthetic:83};
19 real incidents, 15 synthetic incident types.

## Record schema (Features)
| field | dtype | notes |
|---|---|---|
| model | string | one of the spanning-set models |
| trace_id | string | HUD trace id |
| scenario_id | string | e.g. `104-slack_tgw_fd_exhaustion` |
| incident | string | short incident key |
| source | string | `"real"` \| `"synthetic"` |
| reward | float32 | weighted total, validated `0<=r<=1` |
| subscores | struct{root_cause_category, evidence_keywords, ruled_out_red_herrings, remediation_tool: float32} | grader components |
| n_tool_calls | int32 | |
| tools_used | sequence[string] | |
| n_agent_steps | int32 | |
| true_category | string | correct category (not the loud one) |
| difficulty | int32 | real-only; default `0` for synthetic |
| source_company | string | real-only; default `""` |
| source_url | string | real-only; default `""`; first-party postmortem |
| trap_actions | sequence[string] | real-only; default `[]` |
| answer | string | full model answer incl. ROOT_CAUSE/CATEGORY/FIX |

## Loading script — `opensre_trajectories.py`
- `OpenSRETrajectoriesConfig(BuilderConfig)` with `source_filter: Optional[str]`.
- `OpenSRETrajectories(GeneratorBasedBuilder)`, `VERSION=1.0.0`.
- 3 `BUILDER_CONFIGS`: `all`(None), `synthetic`("synthetic"), `real`("real"); default `all`.
- `_info()` returns the typed `Features` above. `_generate_examples` default-fills real-only fields.

## Dataset card — `README.md`
YAML front-matter keys: `license: apache-2.0`, `language: [en]`, `pretty_name`, `size_categories: [n<1K]`,
`task_categories: [text-generation]`, `tags: [...]`, `configs:` (all/synthetic/real ->
data_files), `dataset_info:` (per-config splits.num_examples = 197/83/114, full feature list on `all`).
Body: description, loading snippet, leaderboard table, record-schema jsonc, grading, intended uses,
**Limitations & ethics**, citation.

## Push script — `push_to_hub.py`
- `build_package(stage) -> stats`: writes root jsonl + `synthetic/`/`real/` shards, copies README +
  loader; returns counts + file list.
- CLI: `--repo-id`, `--private`, `--dry-run`, `--token` (default `HF_TOKEN`).
- `--dry-run`: build + print, **no hub import, no network**.
- else: `HfApi(token).create_repo(repo_type="dataset", exist_ok=True)` + `upload_folder(...)`.
- Exit 2 if no token or placeholder repo-id (and not dry-run).

## Validator — `validate_package.py` (offline)
Checks: (1) 197 records, required keys, subscore keys, reward in [0,1], 83/114 split, every real has
`source_url`; (2) README front-matter parses, license, 3 configs, dataset_info counts; (3) loader
imports + exposes 3 configs. Exit 0/1.

## Test cases
- T1 validator exits 0.
- T2 `load_dataset(stage, "all"|"synthetic"|"real")` -> 197|83|114 rows.
- T3 `push_to_hub.py --dry-run` -> 5-file staged package.
- T4 (if auth) real push -> `dataset_info` lists the 5 package files; hub `load_dataset("real")` -> 114.
