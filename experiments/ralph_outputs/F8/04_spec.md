# F8 · 04 Spec

## Artifact 1 — `REPRODUCIBILITY_CHECKLIST.md`
AAAI/NeurIPS-style. Sections:
1. **Header**: project, git SHA, Python version, date, "frozen-LLM / code-as-policy"
   framing, two-tier definition.
2. **Code** (5 items): public availability, entrypoints, deps pinned, env setup,
   determinism of control flow.
3. **Data** (5 items): committed datasets, provenance/generator, splits, scenario
   corpus, doc/data drift note.
4. **Model weights** (4 items): closed-model versioning, open-model recipe, committed
   checkpoints, judge model.
5. **Randomness & seeds** (4 items): seed plumbing, deterministic judge, number of
   seeds/error bars, sources of nondeterminism.
6. **Compute & licensing** (3 items): hardware, budget, license.
7. **Summary table** + **Reviewer-facing limitations**.

Each item tagged with one of: `AVAILABLE` ✅ · `SEEDED` 🎲 (control-flow only) ·
`PARTIAL` ⚠️ · `BLOCKED` ⛔ — plus an **Evidence** pointer (`path:line` or command)
and a one-line **Honest note**.

## Artifact 2 — `repro_manifest.json` (schema)
```json
{
  "project": "SRE-Degrees / REx",
  "git_sha": "<sha>",
  "python": "3.13.7",
  "generated_utc": "<iso>",
  "tiers": {
    "replay":     {"deterministic": true,  "anchor": "opensre-traj/out/hud_trajectories.jsonl + deterministic_judge"},
    "generation": {"deterministic": false, "note": "means ± CI over seeds; LLM sampling not bitwise"}
  },
  "items": [
    {"id":"code.deps","axis":"code","status":"AVAILABLE",
     "evidence":"requirements-rex.txt","note":"runtime deps pinned (>=)."}
  ],
  "counts": {"AVAILABLE":0,"SEEDED":0,"PARTIAL":0,"BLOCKED":0}
}
```
- `status` ∈ {AVAILABLE, SEEDED, PARTIAL, BLOCKED}. `counts` is the tally.

## Artifact 3 — `verify_repro.py` (contract)
Pure-stdlib (`os`, `sys`, `json`, `subprocess`, `importlib.util`). No network.
Functions:
- `check_path(rel) -> bool` — file/dir exists under repo root.
- `check_import(mod) -> bool` — module importable (e.g. `yaml`, `requests`).
- `check_committed(rel) -> bool` — `git ls-files --error-unmatch` returns 0.
- `check_grep(rel, needle) -> bool` — substring present (e.g. `random.Random` in tree.py).
- `git_sha() -> str`.
- `main()` — runs a fixed list of checks mirroring the manifest, prints
  `PASS/FAIL  <id>  <detail>`, writes nothing, exits 0 if all *AVAILABLE/SEEDED*
  claims hold (PARTIAL/BLOCKED are informational, never fail the run).

Test cases (run in step 07):
- `python3 verify_repro.py` exits 0 on this repo.
- `json.load(open('repro_manifest.json'))` succeeds; `counts` sum == len(items).
- Checklist markdown parses (non-empty, has all 6 section headers).
- Manifest `git_sha` matches `git rev-parse HEAD`.

## Determinism contract (the load-bearing claim)
- **Replay tier**: given committed `hud_trajectories.jsonl` + `deterministic_judge`,
  re-grading yields identical scores byte-for-byte. Verifiable offline, no keys.
- **Generation tier**: `rex_tree(..., seed=s)` fixes tree traversal (`tree.py:30,67`)
  and `eval_pass_at_k`/`ablation` sweep `seeds`; the LLM call itself is stochastic, so
  the reproducible object is the **distribution** (mean ± std over seeds), not a run.
