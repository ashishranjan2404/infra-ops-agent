# E4 — 08 Verification

## Success criteria (from 01/03) vs reality

| Criterion | Met? | Evidence |
|---|---|---|
| Harness imports frozen REx primitives, edits NO shared core file | YES | `compare_simple8.py` only `import`s from `rex.*`/`agent.*`/`compute_pass_at_k`; `git status` shows only new files under `experiments/ralph_outputs/E4/` |
| 8 simple incidents pinned + validated | YES | `SIMPLE_8` (len 8, no dupes); `validate_incidents` passes — test 2 green |
| Offline tests pass | YES | `6 passed in 0.04s` (07 §1) |
| Real run, 0 fabricated numbers | YES | `run_standin.json`, 46.7s, 0 errors, deterministic judge (07 §4) |
| Per-incident delta + "does it hurt?" reported | YES | `per_incident[].hurts`, `regression.mean_delta_b_minus_a`, `verdict` |
| Honest BLOCKED verdict on the actual question | YES | blocker documented in 01/07/09 + in-band `note` in the JSON |
| Fireball blocker documented, not fabricated | YES | cross-checked `P7_fireball_status.md`; no slug invented |

## Are outputs real, not placeholder?
- `run_standin.json` is a genuine execution: 48 episodes (2 policies × 8 incidents
  × 3 seeds), each a real model call + real `run_plan` + real `score_plan`. The
  pass@1 values (0.667, 0.333, etc.) are k/3 fractions — exactly what real seed runs
  produce, not round placeholders.
- The two policies are FROZEN frontier models explicitly labelled `*_standin`; the
  JSON `note` and every doc state these are NOT the trained policies.

## Scope guard
`git status --short experiments/ralph_outputs/E4` confirms all writes are inside the
E4 directory. No `rex/`, `sim/`, `agent/`, `experiments/*.py`, dashboard, or other
task dir was touched. No `.patch` needed (harness composes existing public APIs).

## What is verified vs what remains blocked
- **Verified:** the comparison instrument is correct, reproducible, and runnable.
- **Blocked:** the scientific claim ("does specialised training hurt simple cases")
  — requires the FIREBALL-trained and OpenSRE-GRPO-trained slugs, neither of which
  exists in the repo. This is a data/checkpoint blocker, faithfully reported.
