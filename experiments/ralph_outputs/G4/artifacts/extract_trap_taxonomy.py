#!/usr/bin/env python3
"""G4 artifact: extract our trap-action taxonomy from the REAL repo.

Read-only. Pulls the trap-action labels out of the generated scenario YAMLs and the
scoring constants/feedback table out of rex/scoring.py (via AST — no import, no edit),
and emits a machine-readable taxonomy used by the G4 comparison report.

Usage:
    python3 extract_trap_taxonomy.py [REPO_ROOT] [OUT_JSON]
Defaults: REPO_ROOT=/Users/mei/rl  OUT=<this dir>/trap_taxonomy.json
"""
from __future__ import annotations

import ast
import collections
import glob
import json
import os
import sys

import yaml

DEFAULT_REPO = "/Users/mei/rl"
_TRAP_TOOLS_HINT = {"scale_deployment", "clear_cache", "restart_service",
                    "restart_pod", "rollback_deployment"}


def load_why_table(scoring_path: str) -> dict:
    """Extract the per-trap `why` explanation dict literal from rex/scoring.py.

    The dict is the receiver of a `.get(...)` call inside format_feedback, so we AST-walk
    for any Dict node whose string keys intersect the known trap tools. Tolerant: returns
    {} if none is found (the explanation is enrichment, not load-bearing)."""
    try:
        tree = ast.parse(open(scoring_path).read())
    except (OSError, SyntaxError):
        return {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            keys = [k.value for k in node.keys
                    if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            if _TRAP_TOOLS_HINT & set(keys):
                out = {}
                for k, v in zip(node.keys, node.values):
                    if isinstance(k, ast.Constant) and isinstance(v, ast.Constant):
                        out[k.value] = v.value
                if out:
                    return out
    return {}


def _const_assignments(scoring_path: str) -> dict:
    """Pull TRAP_PENALTY and the W_* weights from the module-level tuple assignment."""
    vals = {}
    try:
        tree = ast.parse(open(scoring_path).read())
    except (OSError, SyntaxError):
        return vals
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Tuple):
            names = [t.id for t in node.targets[0].elts] if isinstance(
                node.targets[0], ast.Tuple) else []
            consts = [e.value if isinstance(e, ast.Constant) else None
                      for e in node.value.elts]
            for n, c in zip(names, consts):
                if n in {"W_ROOT", "W_FIX", "W_RESOLVED", "TRAP_PENALTY"} and c is not None:
                    vals[n] = c
    return vals


def scenario_records(yaml_dir: str, why: dict) -> list:
    records = []
    for f in sorted(glob.glob(os.path.join(yaml_dir, "*.yaml"))):
        try:
            d = yaml.safe_load(open(f)) or {}
        except yaml.YAMLError:
            continue
        traps = d.get("trap_actions") or []
        if not traps:
            continue
        meta = d.get("meta", {}) or {}
        rc = d.get("root_cause", {}) or {}
        loc = str(rc.get("location", "")).split("->")[0].strip()
        gold_fix = sorted({s.get("tool") for s in
                           (d.get("canonical_fix", {}) or {}).get("steps", [])
                           if s.get("tool")})
        for t in traps:
            tool = t.get("tool")
            args = t.get("args", {}) or {}
            records.append({
                "scenario_id": meta.get("id", os.path.basename(f)),
                "file": os.path.basename(f),
                "failure_class": meta.get("failure_class"),
                "fault_node": loc,
                "trap": {"tool": tool, "target": args.get("target"),
                         "replicas": args.get("replicas")},
                "contrasted_gold_fix": gold_fix,
                "why_label": why.get(tool),
            })
    return records


def build_taxonomy(repo_root: str = DEFAULT_REPO) -> dict:
    scoring_path = os.path.join(repo_root, "rex", "scoring.py")
    yaml_dir = os.path.join(repo_root, "scenarios", "cidg", "generated")
    why = load_why_table(scoring_path)
    consts = _const_assignments(scoring_path)
    records = scenario_records(yaml_dir, why)
    tool_dist = collections.Counter(r["trap"]["tool"] for r in records)
    n_scen = len(glob.glob(os.path.join(yaml_dir, "*.yaml")))
    return {
        "trap_penalty": consts.get("TRAP_PENALTY"),
        "score_weights": {"root": consts.get("W_ROOT"), "fix": consts.get("W_FIX"),
                          "resolved": consts.get("W_RESOLVED")},
        "n_scenario_files": n_scen,
        "n_with_trap": len(records),
        "trap_tool_distribution": dict(tool_dist),
        "why_table_tools": sorted(why),
        "records": records,
    }


def main(repo_root: str = DEFAULT_REPO, out_path: str | None = None) -> dict:
    tax = build_taxonomy(repo_root)
    out_path = out_path or os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        "trap_taxonomy.json")
    with open(out_path, "w") as fh:
        json.dump(tax, fh, indent=2)
    return tax


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPO
    out = sys.argv[2] if len(sys.argv) > 2 else None
    t = main(root, out)
    print(f"scenarios={t['n_scenario_files']} with_trap={t['n_with_trap']} "
          f"trap_penalty={t['trap_penalty']} tools={t['trap_tool_distribution']}")
