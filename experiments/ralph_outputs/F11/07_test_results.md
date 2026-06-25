# F11 — 07 Test Results

All checks run on this machine (Python 3.13.7, repo HEAD `8a12b41`). Real output below.

## T1 — Tier-A smoke script (`smoke_ae.sh`), offline, no credentials
```
[smoke] repo root: /Users/mei/rl
[smoke] 1/4 python version
Python 3.13.7
[smoke] 2/4 benchmark registry loads
  families: {'simple': 12, 'cascade': 20, 'novel': 10}
[smoke] 3/4 reward floor does not leak (full registry)
  floor_check: {'empty_plan_max_reward': 0.0, 'trap_max_reward': 0.1, 'threshold': 0.8, 'floor_ok': True}
[smoke] 4/4 deterministic judge unit tests
............                                                             [100%]
12 passed in 0.03s
[smoke] PASS — Functional badge checks satisfied (offline, no credentials).
RC=0
```
**PASS.** Note: over the *full* registry `trap_max_reward` is `0.1` (a trap earns a small partial
credit) but still well below the `0.8` threshold, so `floor_ok` holds. This is a stronger check
than the 2-per-family subset used during drafting (which reported 0.0) — caught by ouroboros P1.3.

## T2 — Badge-map schema/grounding tests (`test_badge_map.py`)
```
......                                                                   [100%]
6 passed in 0.02s
```
**PASS** — `test_json_parses`, `test_three_badges`, `test_evidence_files_exist`,
`test_offline_badge_no_creds`, `test_online_badge_uses_eval`, `test_commands_reference_real_flags`.

## T3 — JSON parse + badge set
```
badges: ['Artifacts Available', 'Artifacts Evaluated - Functional', 'Results Reproduced']
```
**PASS** — exactly the three ACM badges.

## T4 — APPENDIX.md structural sanity
```
all 9 sections present; 14 code fences (even: True)
```
**PASS** — sections A.1–A.9 present; all fenced code blocks balanced (14 = 7 pairs).

## T5 — Simulator determinism (REV's challenge from the grill)
```
determinism (same plan twice): 0.0 0.0 EQUAL
```
**PASS** — identical plan → identical reward, substantiating the appendix's "deterministic given a
fixed plan" claim.

## Blocker (expected, documented)
**Tier B (the full pass@k sweep) was NOT run** — it requires a live LLM gateway key and real API
spend (hours). Per the brief, fabricating those numbers is forbidden. The appendix instead ships
the exact, verified reproduction command and the JSON keys to compare; the deliverable (the
appendix + self-checking artifacts) is complete and the offline Functional tier is fully green.

## Fixes applied during testing
- `smoke_ae.sh` floor_check switched from a subset to the **full** registry after T1 surfaced the
  subset would have hidden the `trap_max=0.1` reality (still passing, but now an honest check).
- No other fixes needed; tests passed first run.
