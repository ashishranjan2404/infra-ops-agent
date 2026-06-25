#!/usr/bin/env python3
"""D5 — self-contained validity tests (no network, Python 3.13). Run: python3 test_d5.py"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run(args):
    return subprocess.run([sys.executable] + args, cwd=HERE, capture_output=True, text=True)


def test_build_and_split():
    # T1/T2/T3: build is deterministic, split is a partition, pairs meet threshold.
    r1 = _run(["build_sft_data.py", "--min-reward", "0.5", "--seed", "7"])
    assert r1.returncode == 0, r1.stderr
    split = json.load(open(os.path.join(HERE, "split.json")))
    train, ev = set(split["train"]), set(split["eval"])
    assert train and ev and not (train & ev), "train/eval must be a disjoint partition"
    pairs = [json.loads(l) for l in open(os.path.join(HERE, "sft_pairs.jsonl"))]
    assert pairs, "expected >=1 SFT pair"
    assert all(p["demo_reward"] >= 0.5 for p in pairs), "all pairs must meet min_reward"
    assert all(p["scenario_id"] in train for p in pairs), "SFT pairs only from train split"
    # determinism: rebuild, split must be identical
    r2 = _run(["build_sft_data.py", "--min-reward", "0.5", "--seed", "7"])
    assert r2.returncode == 0
    assert json.load(open(os.path.join(HERE, "split.json")))["train"] == split["train"]
    print(f"  T1-T3 ok: {len(train)} train / {len(ev)} eval, {len(pairs)} pairs, deterministic")


def test_harness_offline():
    # T4: offline harness runs with no network and emits all five subscore columns.
    r = _run(["compare_harness.py", "--offline"])
    assert r.returncode == 0, r.stderr
    out = json.load(open(os.path.join(HERE, "comparison.json")))
    ms = out["summary"]["mean_subscores"]
    for k in ("root_cause_category", "mechanism_match", "evidence_keywords",
              "ruled_out_red_herrings", "remediation_tool"):
        assert k in ms and ms[k] is not None, f"missing subscore {k}"
    assert "proxy" in out["summary"]["mode"], "offline result must be labeled a proxy"
    print(f"  T4 ok: proxy_ceiling={out['summary']['mean_proxy_ceiling_v2']}, all subscores present")


def test_configs_share_keys():
    # T5: both configs point at SAME split + SAME base + SAME grader.
    import re
    def grab(path, key):
        for line in open(path):
            m = re.match(rf"\s*{key}:\s*(\S+)", line)
            if m:
                return m.group(1)
        return None
    cfgd = os.path.join(HERE, "configs")
    for key in ("base_model", "split_path", "grader", "eval_metric"):
        rv = grab(os.path.join(cfgd, "rft.yaml"), key)
        sv = grab(os.path.join(cfgd, "sft.yaml"), key)
        assert rv == sv and rv is not None, f"configs differ on shared key {key}: {rv} vs {sv}"
    print("  T5 ok: rft.yaml and sft.yaml share base_model/split_path/grader/eval_metric")


if __name__ == "__main__":
    test_build_and_split()
    test_harness_offline()
    test_configs_share_keys()
    print("ALL D5 TESTS PASSED")
