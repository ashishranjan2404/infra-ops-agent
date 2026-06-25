"""Self-contained tests for the H7 model registry + CLI (no pytest plugins needed)."""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "model_registry.json")
CLI = os.path.join(HERE, "model_registry.py")


def _run(*args):
    return subprocess.run([sys.executable, CLI, *args], capture_output=True, text=True)


def test_json_parses_and_required_fields():
    reg = json.load(open(DB))
    assert reg["schema_version"]
    req = {"id", "slug", "base", "provider", "role", "training_status",
           "eval_pass_at_1", "frontier_baseline_mean", "frontier_rex_mean",
           "train_mean_reward_start", "train_mean_reward_end", "source"}
    ids = set()
    for m in reg["models"]:
        assert req <= set(m), f"{m.get('id')} missing {req - set(m)}"
        assert m["role"] in ("eval", "trainable")
        ids.add(m["id"])
    assert len(ids) == len(reg["models"]), "duplicate ids"


def test_known_real_references_present():
    ids = {m["id"] for m in json.load(open(DB))["models"]}
    # real ROSTER + forked slugs that MUST exist
    for x in ("claude-opus-4-8", "glm-5p2", "opensre-qwen3-8b", "opensre-qwen3-30b"):
        assert x in ids, x


def test_cli_list_and_filter():
    r = _run("list")
    assert r.returncode == 0 and "claude-opus-4-8" in r.stdout
    r = _run("list", "--role", "trainable")
    assert r.returncode == 0 and "opensre-qwen3-8b" in r.stdout
    assert "claude-opus-4-8" not in r.stdout


def test_cli_show_by_slug_and_missing():
    r = _run("show", "opensre-qwen3-8b-1e439a")  # lookup by slug
    assert r.returncode == 0 and "Qwen/Qwen3-8B" in r.stdout
    r = _run("show", "does-not-exist")
    assert r.returncode == 2


def test_cli_stats_training_deltas():
    r = _run("stats")
    assert r.returncode == 0
    assert "total models: 11" in r.stdout
    assert "0.5220 -> 0.4910" in r.stdout  # real flat qwen3-8b run


if __name__ == "__main__":
    n = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
            n += 1
    print(f"\n{n} tests passed")
