#!/usr/bin/env python3
"""H8 — Automated nightly pass@k eval (cron/launchd entry point).

Runs a small pass@k *smoke* against the latest model on a handful of incidents,
then appends a single JSON line to a history file so trend can be tracked over
time. Designed to be driven by cron or launchd (entries shipped alongside this
script in this same artifacts dir). It is intentionally thin: all the real
evaluation logic lives in `rex.eval_pass_at_k` (the project's single source of
truth for the unbiased pass@k estimator + deterministic judge).

Two execution paths:
  --dry-run   : exercise the WHOLE pipeline (model resolution, scenario pick,
                history append, locking) with a synthetic deterministic
                scorer. NO network, NO LLM calls. Used by CI / smoke / cron
                self-test. Always safe, always fast, fully validates the
                plumbing.
  (default)   : real eval via rex.eval_pass_at_k.run_eval — needs HUD_API_KEY.

History format: newline-delimited JSON (JSONL), one record per run, appended
under an advisory file lock so concurrent/overlapping cron fires don't corrupt
it. Each record is self-describing (schema_version included) so a downstream
dashboard can parse old + new rows.

Usage:
    # smoke / self-test (no network) — this is what `validate` runs:
    python3 nightly_eval.py --dry-run

    # what cron would actually run nightly:
    set -a; source ~/.zshrc; set +a
    python3 nightly_eval.py --model glm-5p2 --per-family 2 --seeds 2

    # inspect trend:
    python3 nightly_eval.py --show-history --history-file <path>
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import socket
import sys

SCHEMA_VERSION = 2

# ---------------------------------------------------------------------------
# Repo discovery. This file lives at experiments/ralph_outputs/H8/artifacts/,
# four levels under the repo root. We add the root to sys.path so `rex.*` and
# `agent.*` import cleanly no matter the cwd cron launches us in.
# ---------------------------------------------------------------------------
_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(_THIS), "..", "..", "..", ".."))
DEFAULT_HISTORY = os.path.join(
    os.path.dirname(_THIS), "nightly_eval_history.jsonl"
)


# ---------------------------------------------------------------------------
# Cross-platform advisory file lock (POSIX fcntl). Falls back to a no-op
# context manager on platforms without fcntl so the script never hard-fails.
# ---------------------------------------------------------------------------
class _FileLock:
    def __init__(self, path: str):
        self._lock_path = path + ".lock"
        self._fh = None

    def __enter__(self):
        try:
            import fcntl  # noqa: PLC0415

            self._fh = open(self._lock_path, "w")
            fcntl.flock(self._fh, fcntl.LOCK_EX)
        except Exception:  # noqa: BLE001 — locking is best-effort
            self._fh = None
        return self

    def __exit__(self, *exc):
        if self._fh is not None:
            try:
                import fcntl  # noqa: PLC0415

                fcntl.flock(self._fh, fcntl.LOCK_UN)
            except Exception:  # noqa: BLE001
                pass
            self._fh.close()
            self._fh = None
        return False


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def _pick_smoke_incidents(per_family: int):
    """Return a flat list of incident names for the smoke, family-balanced.

    Uses the real scenario registry so the dry-run path proves we can resolve
    actual incidents. Degrades gracefully if the registry can't be loaded.
    """
    try:
        sys.path.insert(0, REPO_ROOT)
        from rex.harness import scenarios_by_family  # noqa: PLC0415

        fam = scenarios_by_family()
        out = []
        for f in ("simple", "cascade", "novel"):
            out.extend(sorted(fam.get(f, []))[:per_family])
        return out
    except Exception as e:  # noqa: BLE001
        return {"error": f"{type(e).__name__}: {str(e)[:120]}"}


# ---------------------------------------------------------------------------
# Dry-run scorer: deterministic, no network. Produces a plausible-looking
# pass@k record so the append/lock/parse plumbing is exercised end to end.
# ---------------------------------------------------------------------------
def _dry_run_eval(model: str, per_family: int, seeds: int) -> dict:
    incidents = _pick_smoke_incidents(per_family)
    n_inc = len(incidents) if isinstance(incidents, list) else 0
    # Deterministic synthetic rewards seeded on the model name so the smoke is
    # reproducible but model-dependent (proves the model arg is plumbed).
    import hashlib  # noqa: PLC0415

    h = int(hashlib.sha256(model.encode()).hexdigest(), 16)
    n = max(1, n_inc) * max(1, seeds)
    passes = (h % (n + 1))
    p1 = passes / n
    return {
        "dry_run": True,
        "model": model,
        "incidents": incidents,
        "n_incidents": n_inc,
        "seeds": seeds,
        "summary": {
            "zero_shot": {"pass@1": round(p1, 4), "n": n, "passes": passes},
        },
        "note": "synthetic deterministic scorer — no LLM/network calls",
    }


def _real_eval(model: str, per_family: int, seeds: int, max_workers: int) -> dict:
    """Thin wrapper over the project's real pass@k pipeline."""
    sys.path.insert(0, REPO_ROOT)
    from rex.eval_pass_at_k import run_eval  # noqa: PLC0415

    out = run_eval(
        model,
        conditions=["zero_shot", "rex"],
        per_family=per_family,
        seeds=seeds,
        max_workers=max_workers,
        label=f"nightly:{model}",
    )
    # Compact the heavy result down to a trend-friendly summary for history.
    summary = {}
    for cond, d in out.get("by_condition", {}).items():
        o = d.get("overall", {})
        summary[cond] = {
            "pass@1": o.get("pass@1"),
            "pass@5": o.get("pass@5"),
            "mean_reward": o.get("mean_reward"),
            "reward_std": o.get("reward_std"),
            "n": o.get("n"),
        }
    return {
        "dry_run": False,
        "model": model,
        "seeds": seeds,
        "n_errors": out.get("n_errors", 0),
        "elapsed_s": out.get("elapsed_s"),
        "floor_check": out.get("floor_check"),
        "summary": summary,
    }


def append_history(history_file: str, record: dict) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(history_file)), exist_ok=True)
    line = json.dumps(record, sort_keys=True)
    with _FileLock(history_file):
        with open(history_file, "a") as fh:
            fh.write(line + "\n")


def show_history(history_file: str) -> int:
    if not os.path.exists(history_file):
        print(f"(no history yet at {history_file})")
        return 0
    rows = 0
    with open(history_file) as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            rows += 1
            s = r.get("result", {}).get("summary", {})
            zs = s.get("zero_shot", {})
            print(
                f"{r.get('ts','?'):<22} {r.get('model','?'):<14} "
                f"{'DRY' if r.get('dry_run') else 'REAL':<5} "
                f"zero_shot pass@1={zs.get('pass@1')}"
            )
    print(f"-- {rows} run(s) in history")
    return 0


def run(args) -> dict:
    started = _now_iso()
    status = "ok"
    err = None
    try:
        if args.dry_run:
            result = _dry_run_eval(args.model, args.per_family, args.seeds)
        else:
            result = _real_eval(args.model, args.per_family, args.seeds, args.max_workers)
    except Exception as e:  # noqa: BLE001 — never let a bad eval crash the nightly job
        status = "error"
        err = f"{type(e).__name__}: {str(e)[:200]}"
        result = {"dry_run": args.dry_run, "model": args.model}

    record = {
        "schema_version": SCHEMA_VERSION,
        "ts": started,
        "finished": _now_iso(),
        "host": socket.gethostname(),
        "model": args.model,
        "dry_run": bool(args.dry_run),
        "status": status,
        "error": err,
        "result": result,
    }
    append_history(args.history_file, record)
    return record


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Nightly pass@k eval (cron/launchd entry point)")
    ap.add_argument("--model", default="glm-5p2", help="model slug to eval (the 'latest' model)")
    ap.add_argument("--per-family", type=int, default=2, help="incidents per family for the smoke")
    ap.add_argument("--seeds", type=int, default=2, help="seeds per incident")
    ap.add_argument("--max-workers", type=int, default=4)
    ap.add_argument("--history-file", default=DEFAULT_HISTORY)
    ap.add_argument("--dry-run", action="store_true",
                    help="exercise plumbing with a synthetic scorer; no network")
    ap.add_argument("--show-history", action="store_true", help="print history and exit")
    return ap


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.show_history:
        return show_history(args.history_file)
    rec = run(args)
    print(json.dumps(rec, indent=2, sort_keys=True))
    # Exit non-zero on a real eval error so cron's MAILTO surfaces it; a dry-run
    # error also surfaces (the smoke is supposed to be green).
    return 0 if rec["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
