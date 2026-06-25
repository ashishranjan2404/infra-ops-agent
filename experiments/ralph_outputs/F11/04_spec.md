# F11 — 04 Spec

## Artifact 1: `artifacts/APPENDIX.md` (the deliverable)
AAAI/ACM Artifact Appendix. Required sections (order fixed):
1. **Abstract** — what the artifact is (SRE-Degrees benchmark + REx eval harness), what it lets
   you reproduce (pass@k of REx vs baselines across simple/cascade/novel families).
2. **Artifact check-list (meta-information)** — ACM-style key/value block (Algorithm, Program,
   Run-time env, Hardware, Metrics, Output, Experiments, Disk, Setup time, Run time, Public link,
   License, Badges claimed).
3. **Description**
   3.1 *How to access* — git URL + pinned commit/tag; GitHub-release→Zenodo DOI path.
   3.2 *Hardware dependencies* — CPU-only; ~2 cores, 2 GB RAM; no GPU.
   3.3 *Software dependencies* — Python 3.13; `requirements-rex.txt`; optional HUD_API_KEY.
   3.4 *Benchmarks (data)* — `scenarios/cidg/generated/*.yaml`; families simple/cascade/novel.
4. **Installation** — clone, venv, `pip install -r requirements-rex.txt`.
5. **Experiment workflow** — Tier A (offline Functional) and Tier B (online Reproduced), each a
   copy-pasteable command grounded in the repo.
6. **Evaluation and expected results** — what each tier prints/writes; reproduction tolerance.
7. **Experiment customization** — flags (`--model --conditions --per-family --seeds --frontier`,
   `REX_JUDGE_MODE`).
8. **Notes / threats to reproduction** — sim substrate, model drift, cost, sampling noise.
9. **Badge → claim mapping** — table mirroring badge_claim_map.json.

Format: GitHub-flavored Markdown, must parse (verified in 07 by a Markdown link/section check).

## Artifact 2: `artifacts/badge_claim_map.json`
Machine-readable mapping. Schema:
```json
{
  "artifact": "string",
  "commit_pin": "string (tag or 'PIN_BEFORE_SUBMISSION')",
  "badges": [
    {
      "badge": "Artifacts Available | Artifacts Evaluated - Functional | Results Reproduced",
      "claim": "string (the paper claim or property this badge attests)",
      "tier": "availability | offline | online",
      "command": "string (exact shell command, '' for availability)",
      "evidence_file": "string (repo-relative file the command/claim depends on)",
      "expected": "string (what success looks like)",
      "needs_credentials": true|false
    }
  ]
}
```
Invariants (asserted by `test_badge_map.py`):
- Exactly the 3 ACM badge names present, each once.
- Every non-empty `evidence_file` resolves to a real path under repo root.
- The offline Functional badge has `needs_credentials == false`.
- The online Reproduced badge has `needs_credentials == true` and `command` contains
  `rex.eval_pass_at_k`.

## Artifact 3: `artifacts/smoke_ae.sh`
Offline Functional smoke. Steps, fail-fast (`set -euo pipefail`):
1. Print Python version.
2. `python3 -c` load `scenarios_by_family()`, assert family counts > 0.
3. `python3 -c` run `floor_check` on a small incident set, assert `floor_ok` True.
4. `python3 -m pytest tests/test_rex_deterministic_judge.py -q`.
Exit 0 on all-pass. Uses repo root = the script's `../../../..`.

## Artifact 4: `artifacts/test_badge_map.py`
Pytest validating Artifact 2 against its schema invariants above. Self-contained; resolves repo
root relative to the test file; no network.

## Test cases
- `test_three_badges` — exactly the 3 ACM badge names.
- `test_evidence_files_exist` — every evidence_file resolves under repo root.
- `test_offline_badge_no_creds` — Functional badge credential-free.
- `test_online_badge_uses_eval` — Reproduced badge command references `rex.eval_pass_at_k`.
- `test_json_parses` — file is valid JSON with required top-level keys.
