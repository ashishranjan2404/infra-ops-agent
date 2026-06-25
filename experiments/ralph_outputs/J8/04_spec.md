# 04 — Technical Spec

## Components
1. `demo_trace.py` — the playable trace.
2. `record_demo.sh` — recorder/capture wrapper.
3. `storyboard.md` — 9-shot list with timecodes.
4. `narration.md` — N1..N9 cues.

## `demo_trace.py` — contracts

### Imports (real, read-only)
- `from sim.spec import Action, load_spec`
- `from sim.engine import World, apply_action, is_resolved`
- Repo root prepended to `sys.path` so it runs from any cwd.

### Function signatures
```python
def run(scenario_path: str) -> int        # returns 0 iff is_resolved(world) at the end
def main() -> int                          # argparse: --scenario PATH, --fast
def _emit(text: str, *, type_it: bool=False) -> None
def _prompt(cmd: str) -> None              # prints "sre-degrees$ <cmd>" typed
def _snapshot(world: World, node: str) -> str   # "node  error=..%  p99=..ms", colorized
```

### Trajectory (fixed, 3 engine interactions)
| step | action | expected `is_resolved` | enforced by |
|------|--------|------------------------|-------------|
| open | `World.from_spec(spec)` | `False` | scenario injects fault |
| band-aid | `Action("restart_pod", {target: root})` | `False` | `assert not ok` |
| fix | `Action("scale_deployment", {target: root})` | `True` | exit code |

`root = spec.root_cause.location.split("->")[0].strip()`; `victim = first SLO node`.

### Determinism knobs
- `--fast` / `DEMO_FAST` → `_TYPE_DELAY=0, _LINE_PAUSE=0`.
- `NO_COLOR` → ANSI disabled (clean transcript).

### Output format (one frame)
```
sre-degrees$ agent act --tool restart_pod --target search-api
  search-api       error= 70.0%  p99=  50.0ms
  [ORACLE] root still active — restart did not clear the fault
```

## `record_demo.sh` — contract
- `set -euo pipefail`; `cd` to script dir.
- Always: `NO_COLOR=1 python3 demo_trace.py --fast | tee demo_output.txt`; propagate exit code
  via `PIPESTATUS`.
- If `command -v asciinema`: `asciinema rec --overwrite -c "python3 demo_trace.py" demo.cast`
  (non-fatal on failure).
- Else: print install hint, skip `.cast`.

## Test cases
- **T1** scenario loads + fault injected → `is_resolved == False` at open.
- **T2** band-aid `restart_pod` on `cpu_starve` → still `False` (engine REMEDIATION excludes it).
- **T3** `scale_deployment` on root → `True`.
- **T4** `demo_trace.py --fast` exit code == 0.
- **T5** `demo_output.txt` produced and contains both `[ORACLE] root still active` and
  `RESOLVED`.
- **T6** YAML parse: chosen scenario validates via `sim.spec`.

## File formats
- `demo_output.txt`: UTF-8 plain text, NO_COLOR.
- `demo.cast`: asciinema v2 JSON (only when asciinema present).
