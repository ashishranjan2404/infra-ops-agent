# A18 — 07 Test Results

## T1 — Offline validator (`validate_package.py`) — PASS
```
== 1. JSONL schema ==
  ok  197 records (got 197)
  ok  all records have required keys (bad: [])
  ok  all subscores complete (bad: [])
  ok  all rewards in [0,1] (bad: [])
  ok  83 synthetic (got 83)
  ok  114 real (got 114)
  ok  every real record has source_url (missing: [])
== 2. README YAML front-matter ==
  ok  front-matter block present
  ok  front-matter is valid YAML mapping
  ok  license == apache-2.0
  ok  configs == all/synthetic/real (got {'synthetic', 'real', 'all'})
  ok  dataset_info all==197
  ok  dataset_info synthetic==83
  ok  dataset_info real==114
== 3. Loader script ==
  ok  loader exposes 3 configs (got {'synthetic', 'real', 'all'})
VALIDATION PASSED
```

## T2 — Local `datasets.load_dataset` on staged package — PASS
```
staged: ['README.md', 'hud_trajectories.jsonl', 'opensre_trajectories.py', 'real/real.jsonl', 'synthetic/synthetic.jsonl']
load_dataset config=all: 197 rows (expect 197) OK
load_dataset config=synthetic: 83 rows (expect 83) OK
load_dataset config=real: 114 rows (expect 114) OK
sample row keys: ['answer','difficulty','incident','model','n_agent_steps','n_tool_calls','reward',
 'scenario_id','source','source_company','source_url','subscores','tools_used','trace_id','trap_actions','true_category']
```
Confirms the card's multi-config resolution, the shard split, and the typed schema all parse cleanly
(default-fill on synthetic worked — no null errors on real-only fields).

## T3 — `push_to_hub.py --dry-run` (credential-free path) — PASS
```
[build] staged package at /var/folders/.../opensre_hf_zvsy30zq
[build] total=197 synthetic=83 real=114
  - README.md
  - hud_trajectories.jsonl
  - opensre_trajectories.py
  - real/real.jsonl
  - synthetic/synthetic.jsonl
[dry-run] package is upload-ready; skipping network upload.
```

## T4 — Real push + live load-back — PASS (credentials present)
Auth: `HfApi().whoami()` -> user `quantranger` (token scope includes `repo.write`).
```
[ok] pushed to https://huggingface.co/datasets/quantranger/opensre-incident-trajectories
repo: quantranger/opensre-incident-trajectories | private: False
files: [..., 'README.md', 'hud_trajectories.jsonl', 'opensre_trajectories.py', 'real/real.jsonl', 'synthetic/synthetic.jsonl', ...]
hub load real: 114 rows
sample company: Slack | url: https://slack.engineering/slacks-outage-...
```

## Fixes applied during testing
None required — validator and both load paths passed on first run; the default-fill design (from the
ouroboros pass) pre-empted the synthetic null-field failure (A1).

## Note on blocker handling
The brief framed the actual push as a likely blocker pending HF auth. Auth was in fact present, so the
push was executed for real. Had it been absent, the deliverable would have stopped at T3 (dry-run) with
the documented blocker "no HF_TOKEN / `huggingface-cli login` required".
