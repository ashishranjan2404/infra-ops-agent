# 04 — Technical spec

## Module: `exptrack.py` (stdlib only)

### Public functions
```python
def init(project="sre-degrees", name=None, config=None, directory=None) -> Run
def select_backend() -> str   # "wandb" | "trackio" | "jsonl" | "none"
```
`init` NEVER raises. On any error it degrades jsonl -> noop.

### Run handles
```python
class Run:                      # abstract; best-effort no-op methods
    backend: str                # "wandb"|"trackio"|"jsonl"|"none"
    run_id: str
    path: str | None            # JSONL file path, else None
    def log(self, metrics: Mapping[str,Any], step: int|None=None) -> None
    def summary(self, data: Mapping[str,Any]) -> None
    def finish(self) -> None
    def __enter__/__exit__       # context manager; __exit__ never suppresses exc

class JsonlRun(Run)             # canonical local backend
class WandbRun(Run)             # wraps wandb OR trackio (.init/.log/.finish)
class NoopRun(Run)             # writes nothing
```

### Backend selection (env vars)
- `EXPTRACK_BACKEND` ∈ {auto,wandb,trackio,jsonl,none}; default `auto`.
  - explicit `wandb`/`trackio` degrade to `jsonl` if the import fails.
- `auto`: `WANDB_DISABLED in {true,1}` -> jsonl; else wandb if importable; else trackio;
  else jsonl.
- `EXPTRACK_DIR`: jsonl output dir (default `<module_dir>/_runs`).

### JSONL on-disk format (one object/line)
```
{"_type":"meta",   "run_id","project","name","config":{...},"ts":float}
{"_type":"metric", "step":int, "ts":float, <scalar metric keys...>}
{"_type":"summary","ts":float, <scalar summary keys...>}
```
- `log(step=None)` auto-increments an internal counter starting at 0.
- Value coercion (`_coerce_scalars`): None/bool/int/float/str kept; JSON-able
  list/tuple kept as list; everything else `str(...)`. Guarantees each line is valid JSON.

### Test cases (`test_exptrack.py`)
1. forced `jsonl` -> `select_backend()=="jsonl"`.
2. jsonl run writes 1 meta + 2 metric (steps 0,1 auto-increment) + 1 summary; values
   round-trip.
3. context manager finishes and metric is present.
4. non-scalar coercion: list preserved, dict stringified, bool/int kept.
5. `none` backend -> `backend=="none"`, `path is None`, methods don't raise.
6. log/summary after `finish()` don't raise (best-effort).
7. auto resolves to jsonl when wandb absent (env-conditional).
8. `WANDB_DISABLED=true` forces jsonl.

### Integration contracts
- Train (`opensre-traj/train_rft_v2.py`): one `init` after log-dir setup, one `track.log`
  per step mirroring the existing `line` dict, `summary`+`finish` at the end. Delivered as
  `train_rft_v2.exptrack.patch` (must pass `git apply --check`).
- Eval (`rex/eval_pass_at_k.py`): `init` in `main()`, `track.log` per condition with
  pass@1/pass@5/spread, `finish` after dump. Delivered as snippet.
