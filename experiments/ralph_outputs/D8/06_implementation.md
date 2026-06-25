# D8 — 06 Implementation

## What was actually built (all under `experiments/ralph_outputs/D8/artifacts/`)

### 1. `fireball_adapter.py` (data-ingest adapter — the core deliverable)
Converts one FIREBALL actual-play record into one training example in the
project's existing trajectory training format. Key points:
- Reads the published FIREBALL fields defensively (all optional); a record is
  skipped (and counted) unless it has a non-empty `commands` AND at least one of
  `before_state`/`after_state` — i.e. it must be an actual `s -> a -> s'`
  transition.
- Emits an explicit transition: user turn = `STATE_BEFORE / CONTEXT / ACTION`;
  assistant turn = `RESULT / NARRATION / STATE_AFTER`.
- `_reward_for` produces a documented **data-quality weight** in `[0,1]` (command
  0.4, before-state 0.2, after-state 0.2, observable state change 0.2) — NOT a
  Fireball game score. This was the explicit fix from the grill/ouroboros.
- `_fmt_state` renders the actor-list state compactly (`Name(hp=..)[effects]`).
- CLI: `--in <fireball.jsonl> --out <train.jsonl>`; prints
  `{records_in, examples_out, skipped}`.

### 2. `fireball_fixture.jsonl` (synthetic fixture — 7 records)
Mimics the FIREBALL schema with unmistakably synthetic `syn-combat-*` ids.
Covers: a hit (state change), a kill, a multi-target fireball, a **miss**
(no state change), a heal, a **no-command** turn (must skip), and a buff/effect
turn. Exercises every adapter branch.

### 3. `test_fireball_adapter.py` (unit test — 11 cases)
Skip rules (no command / no state / non-dict), message shape, state-change
detection, reward weighting (1.0 with change, 0.8 without), multi-target render,
stream filtering (6 of 7), `convert_file` roundtrip (7 in / 6 out / 1 skip,
every line valid json), and malformed-jsonl-line handling.

### 4. `fireball_sft.config.yaml` (training config)
SFT on the adapted data (open model `Qwen/Qwen3-8B` fork) + the Claim-2 transfer
eval on `opensre-traj/hud_env_static.py` (pass@1/2/5, split cascade vs simple,
baselines zero-shot / opensre-trained / fireball-trained). Carries the
**fail-closed guard** (`is_real_fireball: false`, `min_examples_for_real_run`)
and a `provenance` block naming the blocker and `do_not_fabricate: true`.

### 5. `fireball_train.jsonl` (generated)
Output of running the adapter on the fixture (6 examples). Demonstrates the
end-to-end transform.

## Shared-core safety
No shared core file was edited. Everything lives in the D8 artifacts dir. The
config *references* `opensre-traj/hud_env_static.py` and `train_rft_v2.py` as
downstream targets but does not modify them.

## How to run
```
# unit test
python3 -m pytest experiments/ralph_outputs/D8/artifacts/test_fireball_adapter.py -q
# convert (fixture -> training format)
python3 experiments/ralph_outputs/D8/artifacts/fireball_adapter.py \
    --in  experiments/ralph_outputs/D8/artifacts/fireball_fixture.jsonl \
    --out experiments/ralph_outputs/D8/artifacts/fireball_train.jsonl
```

## BLOCKER
Real FIREBALL corpus is not in the repo (pending from Wenji). No real training or
transfer-eval was run; no Fireball result is claimed. See 07 / 09 / SUMMARY.
