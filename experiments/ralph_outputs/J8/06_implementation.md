# 06 — Implementation

## What I built (all under `experiments/ralph_outputs/J8/artifacts/`)

| file | what it is |
|------|------------|
| `demo_trace.py` | Asciinema-style typed terminal demo. Loads a REAL CIDG scenario, injects the fault via `World.from_spec`, plays a 3-step trajectory (open → wrong band-aid → causal fix) through `sim/engine.py`, prints engine-computed metrics each step, exits 0 iff `is_resolved`. |
| `record_demo.sh` | Recorder. Always captures `demo_output.txt` (NO_COLOR, `--fast`, exit code via `PIPESTATUS`). Records an animated `demo.cast` only if `asciinema` is installed; otherwise prints install hint and skips. |
| `test_demo_trace.py` | 4 pytest cases (T1–T5) guarding the engine invariants so the demo can't be staged or silently drift. |
| `storyboard.md` | 9-shot storyboard with timecodes, capture recipe, scenario rationale. |
| `narration.md` | Timed narration cues N1–N9 (~150 words, ~90s cut). |
| `demo_output.txt` | REAL captured transcript from running the recorder. |

## Key implementation decisions (traceable to grill/ouroboros)
- **Real engine, scripted policy.** The metrics and resolve/non-resolve are computed by
  `sim/engine.py`; only the action sequence is fixed (for reproducible re-recording). No LLM
  call, no network, no key — runs with bare `python3`.
- **Staging guard.** `assert not ok` after the band-aid step: if anyone makes the wrong tool
  actually correct, the demo crashes instead of silently faking a success.
- **Why `44-search-cpu-starve`.** Its SLO is `error_rate_pct` (engine-tracked). `cpu_starve` is
  in `REMEDIATION` for `scale_deployment`/`increase_memory_limit` but NOT `restart_pod`, so the
  "band-aid fails, causal fix wins" beat is grounded in the simulator's physics. Verified the
  initial `21-leaf-oom` scenario uses a `pod_restarts` SLO the engine doesn't track (KeyError),
  so it was rejected — documented in 07.
- **No shared core files touched.** `sim/`, `rex/`, `agent/`, dashboards untouched. Everything
  new is task-namespaced under J8/artifacts.

## How to run
```
cd experiments/ralph_outputs/J8/artifacts
python3 demo_trace.py            # animated typed playback
./record_demo.sh                 # capture transcript (+ .cast if asciinema present)
python3 -m pytest test_demo_trace.py -q
```
