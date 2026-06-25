# 10 — Feedback for the next task

Fetching an "external/academic" dataset is often less blocked than assumed —
check the Hub first (`HfApi().dataset_info` + `list_repo_files`) before writing a
blocker; FIREBALL was public, non-gated, CC-BY-4.0, and one 1.7 MB shard was
enough to capture the REAL schema and validate the converter end-to-end without
pulling 100K–1M rows. The high-leverage move is: download ONE small shard, copy
its real schema into a `*_schema.py` with a loud `validate_row`, then build a
tiny clearly-synthetic fixture (`SYNTH_*` ids) so tests stay hermetic while the
converter is also proven on real data. Keep the full action (here Avrae commands)
as the trajectory action and treat any derived "tools_used"/verb list as a lossy
convenience view — and always skip empty action/target rows so you don't train on
blanks. Distinguish "converter validated on real data" from "full dataset
acquired" so the deliverable's scope is honest.
