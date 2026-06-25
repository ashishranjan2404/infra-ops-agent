# F11 — 06 Implementation

## What I built (all under experiments/ralph_outputs/F11/artifacts/, no shared-core edits)

1. **`APPENDIX.md`** — the AAAI/ACM artifact appendix. Sections A.1–A.9: Abstract, check-list
   meta-info, Description (access / hardware / software / data), Installation, two-tier experiment
   workflow, expected results + reproduction tolerance, customization, threats, and a Badge→claim
   table. Every command is grounded in the real repo:
   - `rex/eval_pass_at_k.py` flags (`--model --conditions --per-family --seeds --frontier
     --max-workers`) taken verbatim from the module's argparse.
   - `scenarios_by_family()` family counts (`simple=12, cascade=20, novel=10`) from a live call.
   - Deterministic judge / `REX_JUDGE_MODE` from `rex/scoring.py`.
   - `floor_check`, Wilson CI, pass@k from `rex/eval_pass_at_k.py` + `experiments/compute_pass_at_k.py`.
   - JSON output keys (`by_condition.<cond>.by_family.<fam>['pass@1']`, `ci95`) from the emitter.
   - No invented pass@1 numbers — the paper's figures are referenced as read-from-camera-ready.

2. **`badge_claim_map.json`** — machine-readable badge→claim→command→evidence→expected mapping
   for the three ACM badges. Online (Reproduced) command references `rex.eval_pass_at_k` and
   `--conditions`; offline (Functional) references `smoke_ae.sh`; availability references `LICENSE`.

3. **`smoke_ae.sh`** — offline, credential-free Functional smoke. Resolves repo root from its own
   location (with `REX_REPO` override per ouroboros P1.2), loads the registry, runs `floor_check`
   over the **full** registry (ouroboros P1.3 — not a subset), and runs the deterministic-judge
   unit tests. Fail-fast (`set -euo pipefail`).

4. **`test_badge_map.py`** — pytest validating the badge map: 3-badge set, evidence files exist,
   offline badge is credential-free, online badge command contains `rex.eval_pass_at_k` +
   `--conditions`, and the offline command names a real script (ouroboros P3.1).

## Ouroboros deltas applied
- floor_check runs over the full registry in the smoke (P1.3). ✔
- `REX_REPO` override + script-relative root resolution (P1.2). ✔
- No invented numbers; paper figures marked as read-from-camera-ready (P1.1). ✔
- Disk/setup/run-time/cost filled in the check-list (P2.1). ✔
- License pointed to repo `LICENSE` — verified present (P2.2 / P3.3). ✔
- Access leads with pinned tag + Zenodo DOI; `main` only as dev pointer (P2.3). ✔
- Command-grounding string checks in the test (P3.1). ✔
- Explicit "credential-free evaluators stop at Functional, by design" note (P3.2). ✔

## Verified facts used (not assumed)
- HEAD commit `8a12b41`; repo `LICENSE` exists; remote = github.com/ashishranjan2404/infra-ops-agent.
- `scenarios_by_family()` → `{'simple':12,'cascade':20,'novel':10}`.
- `floor_check(full registry-subset)` → `floor_ok: True`.
- Sim grading deterministic: identical plan → identical reward (0.0 == 0.0).
- `tests/test_rex_deterministic_judge.py` → 12 passed.

## No shared-core edits
Only files under `experiments/ralph_outputs/F11/` were created. No `rex/*.py`, `sim/*.py`,
`agent/*.py`, `experiments/*.py`, or status/dashboard files were modified.
