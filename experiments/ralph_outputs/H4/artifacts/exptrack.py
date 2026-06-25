"""exptrack — a lightweight experiment-tracking shim for the SRE-Degrees repo.

Goal: ONE tiny API that the eval / train loops can call to record run config +
per-step metrics, that uses Weights & Biases (or Trackio, a drop-in W&B-compatible
shim) when it is installed and configured, and otherwise falls back to a local
append-only JSONL file. Nothing in the core loops should ever crash because a
tracker is missing, mis-keyed, or offline — tracking is best-effort.

Design contract
---------------
- `init(...) -> Run`            start a run; returns a Run handle (never raises).
- `Run.log(metrics, step=None)` log a flat dict of scalars (best-effort).
- `Run.summary(d)`             set/merge run-level summary scalars.
- `Run.finish()`              close the run / flush the file.
- `Run` is also a context manager (`with init(...) as run:`).

Backend selection (in order):
  1. EXPTRACK_BACKEND env var: one of {auto, wandb, trackio, jsonl, none}. Default "auto".
  2. "auto" -> use wandb if importable AND not disabled, else trackio if importable,
     else jsonl.
  3. "none" -> a no-op run (still returns a usable handle).

The JSONL fallback is fully self-contained (stdlib only) and is what the unit
tests exercise, so the contract is verified without any network or extra deps.

JSONL on-disk format (one JSON object per line):
  {"_type":"meta",   "run_id","project","name","config","ts"}
  {"_type":"metric", "step", "ts", <metric keys...>}
  {"_type":"summary","ts", <summary keys...>}

This module is dependency-free and import-safe under Python 3.9+.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict, Mapping, Optional

__all__ = ["init", "Run", "JsonlRun", "WandbRun", "NoopRun", "select_backend"]

_DEFAULT_DIR = os.environ.get(
    "EXPTRACK_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "_runs"),
)


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _coerce_scalars(d: Mapping[str, Any]) -> Dict[str, Any]:
    """Keep only JSON-serialisable values; stringify the rest. Never raises."""
    out: Dict[str, Any] = {}
    for k, v in dict(d).items():
        key = str(k)
        if v is None or isinstance(v, (bool, int, float, str)):
            out[key] = v
        elif isinstance(v, (list, tuple)):
            try:
                json.dumps(list(v))
                out[key] = list(v)
            except (TypeError, ValueError):
                out[key] = str(v)
        else:
            out[key] = str(v)
    return out


def select_backend() -> str:
    """Resolve the concrete backend name: wandb | trackio | jsonl | none."""
    pref = (os.environ.get("EXPTRACK_BACKEND") or "auto").strip().lower()
    if pref in ("jsonl", "none", "wandb", "trackio"):
        # explicit wandb/trackio still degrade to jsonl if the import fails
        if pref == "wandb" and _import("wandb") is None:
            return "jsonl"
        if pref == "trackio" and _import("trackio") is None:
            return "jsonl"
        return pref
    # auto
    if os.environ.get("WANDB_DISABLED", "").lower() in ("true", "1"):
        return "jsonl"
    if _import("wandb") is not None:
        return "wandb"
    if _import("trackio") is not None:
        return "trackio"
    return "jsonl"


def _import(name: str):
    try:
        return __import__(name)
    except Exception:  # noqa: BLE001  - any import failure -> not available
        return None


# --------------------------------------------------------------------------- #
# Run implementations
# --------------------------------------------------------------------------- #
class Run:
    """Abstract handle. All methods are best-effort and must not raise."""

    backend: str = "base"
    run_id: str = ""
    path: Optional[str] = None

    def log(self, metrics: Mapping[str, Any], step: Optional[int] = None) -> None: ...
    def summary(self, data: Mapping[str, Any]) -> None: ...
    def finish(self) -> None: ...

    def __enter__(self) -> "Run":
        return self

    def __exit__(self, *exc) -> bool:
        self.finish()
        return False  # never suppress exceptions from the wrapped block


class NoopRun(Run):
    backend = "none"

    def __init__(self, run_id: str):
        self.run_id = run_id


class JsonlRun(Run):
    """Local append-only JSONL backend (stdlib only)."""

    backend = "jsonl"

    def __init__(self, project: str, name: str, config: Mapping[str, Any],
                 directory: str, run_id: str):
        self.project = project
        self.name = name
        self.run_id = run_id
        os.makedirs(directory, exist_ok=True)
        self.path = os.path.join(directory, f"{run_id}.jsonl")
        self._step = -1
        self._fh = open(self.path, "a", encoding="utf-8")
        self._write({"_type": "meta", "run_id": run_id, "project": project,
                     "name": name, "config": _coerce_scalars(config),
                     "ts": time.time()})

    def _write(self, obj: Dict[str, Any]) -> None:
        try:
            self._fh.write(json.dumps(obj) + "\n")
            self._fh.flush()
        except Exception:  # noqa: BLE001 - tracking is best-effort
            pass

    def log(self, metrics: Mapping[str, Any], step: Optional[int] = None) -> None:
        if step is None:
            self._step += 1
            step = self._step
        else:
            self._step = step
        rec = {"_type": "metric", "step": int(step), "ts": time.time()}
        rec.update(_coerce_scalars(metrics))
        self._write(rec)

    def summary(self, data: Mapping[str, Any]) -> None:
        rec = {"_type": "summary", "ts": time.time()}
        rec.update(_coerce_scalars(data))
        self._write(rec)

    def finish(self) -> None:
        try:
            self._fh.close()
        except Exception:  # noqa: BLE001
            pass


class WandbRun(Run):
    """Thin wrapper over wandb / trackio (both expose .init/.log/.finish)."""

    def __init__(self, mod, backend: str, project: str, name: str,
                 config: Mapping[str, Any]):
        self._mod = mod
        self.backend = backend
        self._run = mod.init(project=project, name=name,
                             config=dict(_coerce_scalars(config)))
        self.run_id = getattr(self._run, "id", "") or name

    def log(self, metrics: Mapping[str, Any], step: Optional[int] = None) -> None:
        try:
            self._mod.log(dict(_coerce_scalars(metrics)), step=step)
        except Exception:  # noqa: BLE001
            pass

    def summary(self, data: Mapping[str, Any]) -> None:
        try:
            for k, v in _coerce_scalars(data).items():
                self._run.summary[k] = v
        except Exception:  # noqa: BLE001
            pass

    def finish(self) -> None:
        try:
            self._mod.finish()
        except Exception:  # noqa: BLE001
            pass


# --------------------------------------------------------------------------- #
# public entry point
# --------------------------------------------------------------------------- #
def init(project: str = "sre-degrees",
         name: Optional[str] = None,
         config: Optional[Mapping[str, Any]] = None,
         directory: Optional[str] = None) -> Run:
    """Start a tracking run. NEVER raises; falls back to JSONL/no-op on any error."""
    config = config or {}
    run_id = (name or "run") + "-" + uuid.uuid4().hex[:8]
    name = name or run_id
    backend = select_backend()
    try:
        if backend in ("wandb", "trackio"):
            mod = _import(backend)
            if mod is not None and hasattr(mod, "init"):
                return WandbRun(mod, backend, project, name, config)
            backend = "jsonl"
        if backend == "none":
            return NoopRun(run_id)
        return JsonlRun(project, name, config, directory or _DEFAULT_DIR, run_id)
    except Exception:  # noqa: BLE001 - last-ditch: degrade to no-op, never crash caller
        return NoopRun(run_id)
