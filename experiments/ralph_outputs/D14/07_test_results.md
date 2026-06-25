# D14 — 07 Test Results

All commands run from `experiments/ralph_outputs/D14/artifacts/`.

## T1 — assemble the 42-incident task file — PASS
```
$ python3 assemble_tasks.py
wrote tasks_42.json : 42 tasks (34 canonical + 8 variants; 19 real / 23 synthetic)
```
`tasks_42.json`: count=42, n_canonical=34, n_variants=8, n_real_postmortem=19,
n_synthetic=23. Internal asserts (unique ids, all ∈ corpus) passed.
Difficulty spread (Counter): `{5: 18, 4: 15, 3: 9}` — a real curriculum gradient.

## T2 — full dry-run (offline config + id resolution) — PASS
```
$ python3 train_rft_42.py --config train_rft_42.yaml --dry-run
[dry-run] resolved 42 tasks (group=6, steps=30, lr=1e-05)
[dry-run] corpus has 319 scenarios; missing=[]
[dry-run] curriculum order (first 6): [('001-oom_kill', 3), ('002-cpu_saturation', 3),
          ('003-disk_pressure', 3), ('004-crashloop', 3), ('011-bad_deploy_errors', 3),
          ('001-oom_kill-s019', 3)]
[dry-run] OK: config valid, all 42 scenario_ids resolve in corpus
```
All 42 ids (incl. 8 variants) resolve. Runs in **system python3** — no `hud` backend needed.

## T3 — smoke dry-run (override block applied) — PASS
```
$ python3 train_rft_42.py --config train_rft_42.yaml --smoke --dry-run
[dry-run] resolved 2 tasks (group=4, steps=1, lr=1e-05)
```
`smoke:` overrides correctly narrow to 2 tasks / group 4 / 1 step.

## T4 — static checks — PASS
```
$ python3 -m py_compile assemble_tasks.py train_rft_42.py   -> py_compile OK
$ python3 -c "import yaml; yaml.safe_load(open('train_rft_42.yaml'))"  -> yaml OK
```

## T5 — LIVE smoke through `.venv-hud` (HUD Tinker provider) — PASS (run A), then backend-contended (run B)

**Run A (first attempt) — full pipeline executed end-to-end:**
```
opensre-rft-42  model=opensre-qwen3-8b  n_tasks=2  group=4  steps=1  lr=1e-05  curriculum=True
job: https://hud.ai/jobs/342a1c2f5ebb4d98906d18a8ab204952
step   0  mean_reward=0.6586  spread=0.056  n=8
SMOKE OK
```
Archived: `artifacts/smoke_run.jsonl`
`{"step": 0, "mean_reward": 0.6586, "reward_std": 0.0562, "n": 8, "loss": null}`
=> rollouts ran on the assembled tasks (incl. via explicit scenario_id), the deterministic
v2 reward returned a non-degenerate within-group spread (0.056), and a forward/backward
step completed and logged. **The 42-task config + launcher are runnable.**

**Run B (re-run for evidence) — transient backend contention:**
```
... Status: 409 ... model <id> is being trained by another worker; retry later
```
This is a **transient 409** from the shared trainable head being held by another concurrent
Ralph worker — exactly the class the launcher's `_aretry` wrapper is built for; it is not a
defect in the D14 artifacts (Run A proved the same code path succeeds when the head is free).

## Notes / fixes applied during testing
- Fixed `_difficulty` to read the corpus `difficulty` key (was `scenario_difficulty`,
  which is absent from trajectories.jsonl) — without this the curriculum was a no-op.
- Made `--dry-run` read `trajectories.jsonl` directly instead of importing `hud_env`
  (whose `from hud import ...` fails in system py3.13), so offline validation truly is offline.
