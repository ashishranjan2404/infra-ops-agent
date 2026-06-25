# A2 — 07 Test Results

All commands run from `/Users/mei/rl` with `set -a; source ~/.zshrc; set +a` (keys loaded:
ANTHROPIC len=108, FIREWORKS len=24, HUD len=42).

## T1 — compile / import
```
$ python3 -m py_compile experiments/ralph_outputs/A2/artifacts/run_ablation_fast.py
COMPILE OK
```
Initial `ModuleNotFoundError: No module named 'rex'` — REPO was 4 dirnames up; the file lives
at `artifacts/A2/ralph_outputs/experiments/rl`, i.e. **5** up. Fixed; imports resolve.

## T2 — model selection probes (one real call each, cascade prompt)
```
claude-haiku-4-5   ERR HTTPError: 400 Bad Request        # model id retired on this account
minimax-m3         OK 0.6s 0 chars                        # empty completion -> unusable proposer
gemini-3.1-pro     OK 14.4s 363 chars                     # too slow
deepseek-v4-pro    OK 2.3s  -> parsed_actions=1 score=0.00 (deterministic)   # CHOSEN
glm-5p2 (orig)     OK 2.3s  -> parsed_actions=1 score=0.00
```
Under 8-way concurrency, deepseek calls take 8-14s (gateway queueing) — the per-call speedup
over glm is modest; the real win is a **working** proposer + **completable** (resumable,
time-boxed) sweep.

## T3 — smoke (exposed a real bug, then fixed)
`--per-family 1 --seeds 1 --conditions zero_shot,best_of_n --max-seconds 120` timed out before
the engine's first 25-episode checkpoint flush -> `_summarize_partial` returned None ->
`[error] nothing produced`. **Fixed:** empty-checkpoint now yields a valid empty report and
`print_report` is guarded. Re-compiled OK.

## T4 — partial-report + floor + spread + schema compat (on the live checkpoint at 150 eps)
```
partial report built. conditions present: ['zero_shot','best_of_n','retry_realistic','rex','rex_no_oracle']
zero_shot overall: {'n': 150, 'passes': 36, 'pass@1': 0.24, 'reward_std': 0.3744}
floor_check: {'empty_plan_max_reward': 0.0, 'trap_max_reward': 0.1, 'threshold': 0.8, 'floor_ok': True}
aligned_rewards(zero_shot) len: 150 -> schema compatible with run_ablation_v2 OK
```
Key findings:
- **Real spread**: `reward_std=0.37` on zero_shot — deepseek is a good substrate (not floored,
  not ceilinged), so there is genuine headroom for REx to lift (answers the grill's RLE/SMR
  concern empirically).
- **Floor holds**: empty plan 0.0, trap 0.1, both < 0.8 threshold -> `floor_ok=True` (no reward
  leak; cheapest path can't pass).
- **Schema compatible** with `rex/run_ablation_v2.py::aligned_rewards` -> the McNemar follow-up
  consumes this output unchanged.

## T5 — the 750-episode run (deepseek-v4-pro, per-family 10, seeds 5, 16 workers, budget 3300s)
Real, deterministic, checkpointed, 0 errors throughout:
```
[progress]  50/750  (68s, 0 errors)
[progress] 100/750  (165s, 0 errors)
[progress] 150/750  (200s, 0 errors)   # zero_shot family complete; pass@1=0.24
[progress] 200/750  (457s, 0 errors)
[progress] 250/750  (717s, 0 errors)   # best_of_n underway (4 calls/episode)
...
```
### FINAL OUTCOME — the full sweep COMPLETED: 750/750, 0 errors, 2709.8 s (~45 min)
```
[progress] 750/750 new episodes  (2710s, 0 errors)
[a2] completed 750/750 episodes (FULL) in 2709.8s
floor check: empty_plan_max=0.0 trap_max=0.1 -> OK

condition           pass@1          95% CI  pass@2  pass@5   mean    std    n
zero_shot            0.240     [0.18,0.31]   0.424   0.752   0.48   0.37  150
best_of_n            0.307     [0.24,0.38]   0.521   0.845   0.61   0.33  150
retry_realistic      0.313     [0.24,0.39]   0.530   0.852   0.62   0.33  150
rex                  0.893     [0.83,0.93]   0.989   1.000   0.93   0.22  150
rex_no_oracle        0.287     [0.22,0.36]   0.492   0.820   0.59   0.33  150
```
Per family (pass@1): rex solves **simple=1.00, novel=1.00, cascade=0.68**; the controls stay
at cascade 0.02-0.12. Headline contrasts:
- REx lift over zero_shot:            **+0.653**
- REx over best_of_n (raw-compute control):       **+0.586**
- REx over retry_realistic (outcome-feedback ctrl): **+0.580**
- REx over rex_no_oracle (oracle-hint isolation):  **+0.606**

### McNemar paired test (re-used `rex/run_ablation_v2.py`, overall, n=150 pairs)
```
comparison                  A>B  B>A   p_exact sig
rex_vs_zero_shot             99    1    0.0000   *
rex_vs_best_of_n             88    0    0.0000   *
rex_vs_retry_realistic       88    1    0.0000   *
rex_vs_rex_no_oracle         91    0    0.0000   *
```
Every REx-vs-control difference is paired-significant at p<0.0001. The `rex_vs_rex_no_oracle`
split (91 REx-pass/control-fail vs 0 the other way) is the key scientific finding: REx's lift
is driven by the **oracle feedback**, not the tree structure alone.

The HUD gateway DID throttle deepseek to ~8-14 s/call under sustained 16-way concurrency
(best_of_n was the slow stretch, 717-997 s), but the run finished inside the 3300 s budget.
The time-box + checkpoint machinery was therefore exercised as a safety net but not needed —
and would have produced real `PARTIAL N/750` numbers had the budget been hit.
