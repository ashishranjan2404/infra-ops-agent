#!/usr/bin/env python3
"""validate_package.py — offline validation of the HF upload package.

Checks (no network):
  1. JSONL parses; every record has the required schema keys.
  2. README YAML front-matter parses and declares the 3 configs + correct counts.
  3. The loader script imports and exposes the 3 BuilderConfigs.
  4. dataset_info split counts in the card match the actual data.
Exit 0 on success, 1 on any failure.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JSONL = Path("/Users/mei/rl/opensre-traj/out/hud_trajectories.jsonl")
README = HERE / "README.md"

REQUIRED_KEYS = {
    "model", "trace_id", "scenario_id", "incident", "source", "reward",
    "subscores", "n_tool_calls", "tools_used", "n_agent_steps",
    "true_category", "answer",
}
SUBSCORE_KEYS = {
    "root_cause_category", "evidence_keywords", "ruled_out_red_herrings", "remediation_tool",
}

fails = []


def check(cond, msg):
    print(("  ok  " if cond else " FAIL ") + msg)
    if not cond:
        fails.append(msg)


def main():
    print("== 1. JSONL schema ==")
    records = [json.loads(l) for l in JSONL.read_text().splitlines() if l.strip()]
    check(len(records) == 197, f"197 records (got {len(records)})")
    bad = [i for i, r in enumerate(records) if not REQUIRED_KEYS.issubset(r)]
    check(not bad, f"all records have required keys (bad: {bad[:5]})")
    sub_bad = [i for i, r in enumerate(records)
               if not SUBSCORE_KEYS.issubset(r.get("subscores", {}))]
    check(not sub_bad, f"all subscores complete (bad: {sub_bad[:5]})")
    rew_bad = [i for i, r in enumerate(records) if not 0.0 <= r["reward"] <= 1.0]
    check(not rew_bad, f"all rewards in [0,1] (bad: {rew_bad[:5]})")

    n_syn = sum(r["source"] == "synthetic" for r in records)
    n_real = sum(r["source"] == "real" for r in records)
    check(n_syn == 83, f"83 synthetic (got {n_syn})")
    check(n_real == 114, f"114 real (got {n_real})")
    real_missing_src = [r["incident"] for r in records
                        if r["source"] == "real" and not r.get("source_url")]
    check(not real_missing_src, f"every real record has source_url (missing: {real_missing_src[:3]})")

    print("== 2. README YAML front-matter ==")
    text = README.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    check(m is not None, "front-matter block present")
    if m:
        try:
            import yaml
            meta = yaml.safe_load(m.group(1))
            check(isinstance(meta, dict), "front-matter is valid YAML mapping")
            check(meta.get("license") == "apache-2.0", "license == apache-2.0")
            cfg_names = {c["config_name"] for c in meta.get("configs", [])}
            check(cfg_names == {"all", "synthetic", "real"},
                  f"configs == all/synthetic/real (got {cfg_names})")
            di = {d["config_name"]: d for d in meta.get("dataset_info", [])}
            check(di["all"]["splits"][0]["num_examples"] == 197, "dataset_info all==197")
            check(di["synthetic"]["splits"][0]["num_examples"] == 83, "dataset_info synthetic==83")
            check(di["real"]["splits"][0]["num_examples"] == 114, "dataset_info real==114")
        except ImportError:
            print("  warn  PyYAML not installed; skipping deep YAML checks")

    print("== 3. Loader script ==")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "opensre_loader", HERE / "opensre_trajectories.py")
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        names = {c.name for c in mod.OpenSRETrajectories.BUILDER_CONFIGS}
        check(names == {"all", "synthetic", "real"}, f"loader exposes 3 configs (got {names})")
    except Exception as e:  # noqa: BLE001
        check(False, f"loader imports cleanly ({e})")

    print()
    if fails:
        print(f"VALIDATION FAILED ({len(fails)} issue(s))")
        return 1
    print("VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
