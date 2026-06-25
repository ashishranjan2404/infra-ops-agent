# 07 — Test Results

## Static checks
```
$ python3 -m py_compile experiments/ralph_outputs/E1/artifacts/verify_grpo_push.py
py_compile OK
$ python3 -c "import json;json.load(open('.../grpo_inventory.json'));print('json OK')"
json OK
```
All `.md` deliverables are valid GitHub-flavored markdown (parse-checked by rendering).

## Branch / remote inventory (the load-bearing fact for this task)
```
$ git branch -a | grep -iE 'grpo|wenji|rft|fireball'      ->  (no output)
$ git for-each-ref | grep -iE 'grpo|wenji|rft|fireball'   ->  (no output)
$ git remote -v
origin  git@github.com:ashishranjan2404/infra-ops-agent.git
remote branches: origin/main, origin/opensre-traj
```
**Confirmed: no GRPO/Fireball/Wenji branch exists locally or on `origin`.** This is the blocker.

## Verifier functional tests (3 cases from spec §C)
| case | setup | expected | got |
|------|-------|----------|-----|
| **T1** today, nothing pushed | repo as-is | BLOCKED, exit 2, corpus MISS | ✅ exit 2, `fireball_corpus_present` MISS, `no_secrets` PASS |
| **T2** complete fixture | corpus + rollouts + run log + `E1_MANIFEST.json`, no secrets | GATE-1 PASS, exit 0 | ✅ exit 0, prints gate-2 next command |
| **T3** secret injected | T2 fixture + `HUD_API_KEY=…` in corpus | BLOCKED, exit 2, `no_secrets` MISS | ✅ exit 2, leak path reported |

Raw output captured during the run (T2 tail):
```
GATE-1: PASS — branch payload is complete & mergeable.
NEXT (GATE-2, owned by us): ... python3 -m rex.eval_pass_at_k ...
  parity assert: |our_reward - her_reward| < 1e-3 per rollout (rex/scoring.py).
```

## Fix applied during testing
Initial corpus glob (`trajector`) false-positived on the opensre **target-domain** files
`opensre-traj/out/*trajectories.jsonl` (which per `P7_fireball_status.md` are NOT the Fireball
source corpus). Tightened `CORPUS_HINTS` to `fireball|dnd|d&d|incidents.jsonl` and added a
`CORPUS_EXCLUDE` for `opensre-traj/out/`, the P7 status doc, and `ralph_outputs/`. Re-ran T1 →
corpus correctly MISS; T2/T3 unaffected.

## Exit-code semantics (documented, not a failure)
Exit 2 on T1 is the **correct BLOCKED state**, not a crash — the branch genuinely isn't pushed.
The verifier reserves exit 1 for internal errors only (none observed).
