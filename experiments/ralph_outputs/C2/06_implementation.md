# C2 — Implementation

## What I built (all task-namespaced; no shared core file edited)
- `artifacts/cascade_synth.py` — runnable wrapper. Imports the baseline synthesis
  machinery from `rex.harness_synth` (features, labels, interpreter, scoring, search) and
  `rex.harness.scenarios_by_family` READ-ONLY. Overrides ONLY:
  - the incident split → cascade-only (14 train / 6 held-out),
  - the mutation model → `C2_MODEL` env var (gateway), via a save/restore wrapper around
    `hs.MODEL` so no module global leaks.
  It prints the same TRAIN/HELD-OUT confusion table as the baseline for 3 harnesses
  (empty seed, cascade-synth, hand-written `is_safe`) and dumps `cascade_synth.json`.
- `artifacts/cascade_synth.json` — real run output (model gpt-5.5, budget 8).
- `artifacts/compare.md` — the structured comparison (hazard coverage + held-out numbers
  + caveats) vs `rex/runs/harness_synth.json`.
- `artifacts/run_gpt55.log`, `run_deepseek_noop.log` — captured stdout (real evidence).

## No core files changed
Per the real-artifact rule I did not touch `rex/*.py`. The cascade split lives entirely
in my wrapper. If one wanted this in core, the proposed change would be to add a
`--family cascade` CLI flag to `rex/harness_synth.py:main` that sets TRAIN/HELDOUT from
`scenarios_by_family()`; I document that here rather than editing the file.

## How it ran
```
set -a; source ~/.zshrc; set +a
C2_MODEL=gpt-5.5 python3 experiments/ralph_outputs/C2/artifacts/cascade_synth.py
```

## Key result (see compare.md for full numbers)
Cascade-only synthesis finds a **structurally different, narrower** rule-set:
- KEEPS `treats_forbidden_category` (the canonical cascade guard).
- DROPS every leaf/node guard (`leak_active`, `at_replica_limit`,
  `rollback_without_deploy`) — those hazards are absent from cascade training data, so they
  are unlearnable (no supervision).
- ADDS one over-general `scale_deployment` blanket block (overfits the cascade signal that
  scaling the loud victim is usually a trap) → 5 held-out false-blocks.

## Real blocker encountered (and handled, not faked)
The mutation operator originally pinned to `deepseek-v4-pro` (per the "Anthropic out of
credits → use gateway/deepseek" memory) returned EMPTY completions, so synthesis
degenerated to the empty seed (score 0.395, flat). Diagnosed live (raw completion length
0), then switched the operator to `gpt-5.5` (verified to return parseable JSON rules) and
re-ran. The deepseek no-op is itself a recorded finding about engine fragility.
