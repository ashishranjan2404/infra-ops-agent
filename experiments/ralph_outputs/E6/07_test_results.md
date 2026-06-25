# E6 — 07 Test Results

## Unit tests — PASS (16/16)
```
$ python3 -m pytest test_fireball_ablate.py -q
................                                                         [100%]
16 passed in 0.02s
```
Covers: fixture load, VARIANTS constant, full==identity+tag, input-not-mutated (purity),
state_only drops assistant steps / keeps state-remediation / drops action-remediation /
strips gold action sequence, action_only drops tool steps / keeps fix / drops state / drops
evidence, **step partition equality**, concrete counts (3 asst + 2 tool in rec 0), dispatch,
unknown-variant raises, stream over all records, validation rejects bad records (3 cases).

## Harness on synthetic fixture — PASS
```
$ python3 run_ablation_e6.py --in fixture_fireball.jsonl --outdir ./_variants --report ./ablation_report.json
```
| variant | total_steps | assistant | tool | state_transition | canonical_fix | evidence |
|---|---|---|---|---|---|---|
| full | 10 | 6 | 4 | 2 | 2 | 2 |
| state_only | 4 | 0 | 4 | 2 | 0 | 2 |
| action_only | 6 | 6 | 0 | 0 | 2 | 0 |

Partition check: state_only(4) + action_only(6) = 10 = full. ✔

## Harness on REAL in-repo corpus (319 records) — PASS
```
$ python3 run_ablation_e6.py --in /Users/mei/rl/opensre-traj/out/trajectories.jsonl --outdir ./_variants_real
n_input 319
full         {n_records:319, total_steps:4654, mean:14.589, assistant:2327, tool:2327, state_trans:312, fix:319, evidence:319}
state_only   {n_records:319, total_steps:2327, mean:7.295,  assistant:0,    tool:2327, state_trans:312, fix:0,   evidence:319}
action_only  {n_records:319, total_steps:2327, mean:7.295,  assistant:2327, tool:0,    state_trans:0,   fix:319, evidence:0}
```
Partition check at scale: 2327 + 2327 = 4654 = full total_steps. ✔
3 × 319-line variant JSONLs written, all valid JSON (re-read without error).

## CLI single-variant smoke — PASS
```
$ python3 fireball_ablate.py --in fixture_fireball.jsonl --variant action_only --out /tmp/e6_ao.jsonl
[fireball_ablate] action_only: wrote 2 records -> /tmp/e6_ao.jsonl
```

## Fixes applied during dev
None required — transforms passed first run on fixture and the 319-record real corpus.

## NOT run (blocked, by design — NOT faked)
Per-variant model training and pass@k evaluation: requires the real FIREBALL D&D corpus
and a fireball-trained slug (absent from repo; see 09 + P7_fireball_status.md). **Zero
model metrics were produced or fabricated.**
