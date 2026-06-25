# E5 — Test Results

## 1. Harness self-test (no network)
```
$ python3 experiments/ralph_outputs/E5/artifacts/test_transfer_eval.py
  ok: select_novel_set -> 10 loadable keys ['azure_leapyear_cert', 'conntrack_exhaustion',
      'facebook_bgp_backbone', 'firefox_addon_cert', 'gke_ip_exhaustion', 'kafka_poison_pill',
      'knight_capital_conflict', 'auth_cert_expiry', 'billing_disk_fill', 'checkout_bad_rollout']
  ok: empty plan scores 0.0 on all 10 (floor)
  ok: oracle plan scores >= 0.8 on all 10 (ceiling / data-validity)
  ok: unknown model handled (lazy)
ALL E5 TESTS PASSED
```
PASS — selection, floor, ceiling, and blocked-model handling all validated offline.

## 2. Syntax / parse checks
```
$ python3 -m py_compile transfer_eval_novel.py test_transfer_eval.py   -> PY_COMPILE_OK
$ python3 -c "import json; json.load(open('.../transfer_results.json'))" -> JSON_OK
```
PASS.

## 3. Live transfer run (real LLM)
```
$ set -a; source ~/.zshrc; set +a
$ python3 experiments/ralph_outputs/E5/artifacts/transfer_eval_novel.py \
      --baselines glm-5p2 --fireball-model fireball --seeds 2 --n 10
novel set (10): [...]
  glm-5p2 (baseline): pass@1=0.25 mean=0.4075
  fireball (fireball): BLOCKED  [KeyError: 'fireball']
floor/ceiling: {'empty_mean': 0.0, 'oracle_mean': 1.0, 'floor_ok': True, 'ceiling_ok': True}
-> experiments/ralph_outputs/E5/transfer_results.json
```
PASS for the deliverable: real baseline numbers produced; Fireball recorded blocked.

## 4. LLM reachability probe (explains the blocker class)
```
glm-5p2          -> reachable (Fireworks)          [used as baseline]
gpt-5.5          -> reachable but returns ''        [gateway; would score low, not blocked]
claude-haiku-4-5 -> HTTP 400 Bad Request           [Anthropic credits exhausted, per project memory]
fireball         -> KeyError: 'fireball'           [not in ROSTER / no provider — THE BLOCKER]
```

## Errors encountered + fixes
- `timeout` not on macOS zsh → dropped it; ran the eval as a background task instead.
- Initial eager client resolution would have crashed the run on the bad fireball name →
  spec already guards it in `main()` try/except, so the valid glm-5p2 numbers survived
  and fireball was cleanly recorded `blocked` (verified in the run above).

## Bottom line
Harness is real and runnable; controls hold (floor 0 / ceiling 1); one real baseline
(glm-5p2, pass@1 0.25, std 0.38) captured on the 10 novel incidents; Fireball blocker
documented, not fabricated.
