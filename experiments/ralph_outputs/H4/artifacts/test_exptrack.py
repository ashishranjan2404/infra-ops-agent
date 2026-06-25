"""Unit tests for exptrack — focused on the JSONL fallback + best-effort contract.

Run:
    python3 -m pytest experiments/ralph_outputs/H4/artifacts/test_exptrack.py -q
or (no pytest needed):
    python3 experiments/ralph_outputs/H4/artifacts/test_exptrack.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import exptrack  # noqa: E402


def _read(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def test_jsonl_backend_selected_when_forced(monkeypatch=None, tmp_path=None):
    os.environ["EXPTRACK_BACKEND"] = "jsonl"
    assert exptrack.select_backend() == "jsonl"


def test_jsonl_run_writes_meta_metric_summary(tmp_path):
    os.environ["EXPTRACK_BACKEND"] = "jsonl"
    run = exptrack.init(project="t", name="r", config={"lr": 1e-5, "model": "glm"},
                        directory=str(tmp_path))
    assert run.backend == "jsonl"
    run.log({"mean_reward": 0.5, "reward_std": 0.1}, step=0)
    run.log({"mean_reward": 0.7, "reward_std": 0.2})  # auto-increment step -> 1
    run.summary({"best_reward": 0.7})
    run.finish()

    recs = _read(run.path)
    meta = [r for r in recs if r["_type"] == "meta"]
    metrics = [r for r in recs if r["_type"] == "metric"]
    summ = [r for r in recs if r["_type"] == "summary"]

    assert len(meta) == 1
    assert meta[0]["config"]["model"] == "glm"
    assert len(metrics) == 2
    assert metrics[0]["step"] == 0 and metrics[1]["step"] == 1  # auto-increment
    assert metrics[1]["mean_reward"] == 0.7
    assert summ and summ[0]["best_reward"] == 0.7


def test_context_manager_finishes(tmp_path):
    os.environ["EXPTRACK_BACKEND"] = "jsonl"
    with exptrack.init(project="t", name="ctx", directory=str(tmp_path)) as run:
        run.log({"x": 1})
        path = run.path
    recs = _read(path)
    assert any(r["_type"] == "metric" for r in recs)


def test_non_scalar_values_are_coerced(tmp_path):
    os.environ["EXPTRACK_BACKEND"] = "jsonl"
    run = exptrack.init(project="t", name="coerce", directory=str(tmp_path))
    run.log({"rewards": [0.1, 0.2], "obj": {"a": 1}, "ok": True, "n": 4})
    run.finish()
    rec = [r for r in _read(run.path) if r["_type"] == "metric"][0]
    assert rec["rewards"] == [0.1, 0.2]   # JSON-able list preserved
    assert isinstance(rec["obj"], str)    # dict stringified
    assert rec["ok"] is True and rec["n"] == 4


def test_none_backend_is_noop(tmp_path):
    os.environ["EXPTRACK_BACKEND"] = "none"
    run = exptrack.init(project="t", name="noop", directory=str(tmp_path))
    assert run.backend == "none"
    run.log({"x": 1})       # must not raise
    run.summary({"y": 2})   # must not raise
    run.finish()
    assert run.path is None


def test_log_never_raises_after_finish(tmp_path):
    os.environ["EXPTRACK_BACKEND"] = "jsonl"
    run = exptrack.init(project="t", name="afterfin", directory=str(tmp_path))
    run.finish()
    run.log({"x": 1})       # best-effort: swallowed, no exception
    run.summary({"y": 2})


def test_auto_falls_back_to_jsonl_without_wandb(tmp_path):
    """In this env wandb is not installed, so auto must resolve to jsonl."""
    os.environ.pop("EXPTRACK_BACKEND", None)
    os.environ.pop("WANDB_DISABLED", None)
    try:
        __import__("wandb")
        has_wandb = True
    except Exception:
        has_wandb = False
    if not has_wandb:
        assert exptrack.select_backend() == "jsonl"


def test_wandb_disabled_env_forces_jsonl():
    os.environ.pop("EXPTRACK_BACKEND", None)
    os.environ["WANDB_DISABLED"] = "true"
    assert exptrack.select_backend() == "jsonl"
    os.environ.pop("WANDB_DISABLED", None)


if __name__ == "__main__":
    import tempfile

    failures = 0
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        with tempfile.TemporaryDirectory() as d:
            try:
                # call with tmp_path if the test takes one
                import inspect
                if "tmp_path" in inspect.signature(fn).parameters:
                    fn(tmp_path=d)
                else:
                    fn()
                print(f"PASS {fn.__name__}")
            except Exception as e:  # noqa: BLE001
                failures += 1
                print(f"FAIL {fn.__name__}: {type(e).__name__}: {e}")
    print(f"\n{'ALL PASS' if failures == 0 else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)
